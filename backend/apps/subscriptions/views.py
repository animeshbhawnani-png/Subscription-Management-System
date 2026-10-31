from datetime import date
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quotation, Subscription
from .permissions import IsOwnerOrStaffOrAdmin, IsStaffOrAdmin
from .serializers import (
    ConvertQuotationSerializer,
    QuotationCreateUpdateSerializer,
    QuotationSerializer,
    SubscriptionSerializer,
)
from .services import (
    calculate_next_billing_date,
    convert_quotation_to_subscription,
    create_or_update_quotation,
)


from apps.products.models import Product
from apps.products.serializers import ProductSerializer
from apps.users.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


def _ok(data, code=status.HTTP_200_OK):
    return Response({"data": data, "error": None}, status=code)


def _err(message, code=status.HTTP_400_BAD_REQUEST):
    return Response({"data": None, "error": message}, status=code)


class CustomerListView(APIView):
    """GET /api/customers/ - Helper for staff/admin to select customers."""
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def get(self, request):
        customers = User.objects.filter(role="customer").order_by("email")
        return _ok(UserSerializer(customers, many=True).data)


class CatalogListView(APIView):
    """GET /api/catalog/ - Helper for staff/customer to select products with variants."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.prefetch_related("variants").all()
        return _ok(ProductSerializer(products, many=True).data)


class QuotationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ("admin", "staff"):
            quotations = Quotation.objects.select_related("customer", "created_by", "subscription").prefetch_related("items__product", "items__variant").all()
        else:
            quotations = Quotation.objects.filter(customer=user).select_related("customer", "created_by", "subscription").prefetch_related("items__product", "items__variant")

        status_filter = request.query_params.get("status")
        if status_filter:
            quotations = quotations.filter(status=status_filter)

        search = request.query_params.get("search", "").strip()
        if search:
            quotations = quotations.filter(quotation_number__icontains=search)

        serializer = QuotationSerializer(quotations, many=True)
        return _ok(serializer.data)

    def post(self, request):
        user = request.user
        if user.role not in ("admin", "staff"):
            return _err("Only administrators and staff can create quotations.", status.HTTP_403_FORBIDDEN)

        serializer = QuotationCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return _err(serializer.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)

        customer = serializer.validated_data.get("customer")
        if not customer:
            return _err({"customer_id": "Customer is required."}, status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            quotation = create_or_update_quotation(
                customer=customer,
                created_by=user,
                items_data=serializer.validated_data["items"],
                valid_until=serializer.validated_data.get("valid_until"),
                notes=serializer.validated_data.get("notes", ""),
            )
            return _ok(QuotationSerializer(quotation).data, code=status.HTTP_201_CREATED)
        except ValidationError as e:
            return _err(e.detail, status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            return _err(str(e), status.HTTP_400_BAD_REQUEST)


class QuotationDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrStaffOrAdmin]

    def get_object(self, pk, user):
        try:
            quotation = Quotation.objects.select_related("customer", "created_by", "subscription").prefetch_related("items__product", "items__variant").get(pk=pk)
        except Quotation.DoesNotExist:
            return None

        if user.role not in ("admin", "staff") and quotation.customer != user:
            return None
        return quotation

    def get(self, request, pk):
        quotation = self.get_object(pk, request.user)
        if not quotation:
            return _err("Quotation not found.", status.HTTP_404_NOT_FOUND)
        return _ok(QuotationSerializer(quotation).data)

    def put(self, request, pk):
        if request.user.role not in ("admin", "staff"):
            return _err("Only staff and admin can edit quotations.", status.HTTP_403_FORBIDDEN)

        quotation = self.get_object(pk, request.user)
        if not quotation:
            return _err("Quotation not found.", status.HTTP_404_NOT_FOUND)

        if quotation.status != Quotation.Status.DRAFT:
            return _err("Only draft quotations can be modified.", status.HTTP_400_BAD_REQUEST)

        serializer = QuotationCreateUpdateSerializer(quotation, data=request.data, partial=True)
        if not serializer.is_valid():
            return _err(serializer.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            customer = serializer.validated_data.get("customer", quotation.customer)
            updated = create_or_update_quotation(
                customer=customer,
                created_by=quotation.created_by,
                items_data=serializer.validated_data.get("items", []),
                valid_until=serializer.validated_data.get("valid_until", quotation.valid_until),
                notes=serializer.validated_data.get("notes", quotation.notes),
                instance=quotation,
            )
            return _ok(QuotationSerializer(updated).data)
        except ValidationError as e:
            return _err(e.detail, status.HTTP_422_UNPROCESSABLE_ENTITY)


class QuotationAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            quotation = Quotation.objects.get(pk=pk)
        except Quotation.DoesNotExist:
            return _err("Quotation not found.", status.HTTP_404_NOT_FOUND)

        if request.user.role not in ("admin", "staff") and quotation.customer != request.user:
            return _err("You do not have permission to accept this quotation.", status.HTTP_403_FORBIDDEN)

        if quotation.status == Quotation.Status.ACCEPTED:
            return _err("Quotation is already accepted.", status.HTTP_400_BAD_REQUEST)

        if quotation.status not in (Quotation.Status.DRAFT, Quotation.Status.SENT):
            return _err(f"Cannot accept quotation with status '{quotation.status}'.", status.HTTP_400_BAD_REQUEST)

        quotation.status = Quotation.Status.ACCEPTED
        quotation.save(update_fields=["status", "updated_at"])
        return _ok(QuotationSerializer(quotation).data)


class QuotationRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            quotation = Quotation.objects.get(pk=pk)
        except Quotation.DoesNotExist:
            return _err("Quotation not found.", status.HTTP_404_NOT_FOUND)

        if request.user.role not in ("admin", "staff") and quotation.customer != request.user:
            return _err("You do not have permission to reject this quotation.", status.HTTP_403_FORBIDDEN)

        if quotation.status == Quotation.Status.REJECTED:
            return _err("Quotation is already rejected.", status.HTTP_400_BAD_REQUEST)

        quotation.status = Quotation.Status.REJECTED
        quotation.save(update_fields=["status", "updated_at"])
        return _ok(QuotationSerializer(quotation).data)


class QuotationConvertView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def post(self, request, pk):
        try:
            quotation = Quotation.objects.select_related("customer").prefetch_related("items__product", "items__variant").get(pk=pk)
        except Quotation.DoesNotExist:
            return _err("Quotation not found.", status.HTTP_404_NOT_FOUND)

        serializer = ConvertQuotationSerializer(data=request.data)
        if not serializer.is_valid():
            return _err(serializer.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)

        billing_interval = serializer.validated_data.get("billing_interval", Subscription.BillingInterval.MONTHLY)

        try:
            subscription = convert_quotation_to_subscription(quotation, billing_interval=billing_interval)
            return _ok(SubscriptionSerializer(subscription).data, code=status.HTTP_201_CREATED)
        except ValidationError as e:
            return _err(e.detail, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return _err(str(e), status.HTTP_400_BAD_REQUEST)


class SubscriptionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ("admin", "staff"):
            subs = Subscription.objects.select_related("customer", "quotation", "product", "variant").all()
        else:
            subs = Subscription.objects.filter(customer=user).select_related("customer", "quotation", "product", "variant")

        status_filter = request.query_params.get("status")
        if status_filter:
            subs = subs.filter(status=status_filter)

        search = request.query_params.get("search", "").strip()
        if search:
            subs = subs.filter(subscription_number__icontains=search)

        serializer = SubscriptionSerializer(subs, many=True)
        return _ok(serializer.data)


class SubscriptionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrStaffOrAdmin]

    def get_object(self, pk, user):
        try:
            sub = Subscription.objects.select_related("customer", "quotation", "product", "variant").get(pk=pk)
        except Subscription.DoesNotExist:
            return None

        if user.role not in ("admin", "staff") and sub.customer != user:
            return None
        return sub

    def get(self, request, pk):
        sub = self.get_object(pk, request.user)
        if not sub:
            return _err("Subscription not found.", status.HTTP_404_NOT_FOUND)
        return _ok(SubscriptionSerializer(sub).data)


class SubscriptionPauseView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def post(self, request, pk):
        try:
            sub = Subscription.objects.get(pk=pk)
        except Subscription.DoesNotExist:
            return _err("Subscription not found.", status.HTTP_404_NOT_FOUND)

        if sub.status != Subscription.Status.ACTIVE:
            return _err(f"Cannot pause subscription with status '{sub.status}'. Must be active.", status.HTTP_400_BAD_REQUEST)

        sub.status = Subscription.Status.PAUSED
        sub.save(update_fields=["status", "updated_at"])
        return _ok(SubscriptionSerializer(sub).data)


class SubscriptionResumeView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def post(self, request, pk):
        try:
            sub = Subscription.objects.get(pk=pk)
        except Subscription.DoesNotExist:
            return _err("Subscription not found.", status.HTTP_404_NOT_FOUND)

        if sub.status != Subscription.Status.PAUSED:
            return _err(f"Cannot resume subscription with status '{sub.status}'. Must be paused.", status.HTTP_400_BAD_REQUEST)

        sub.status = Subscription.Status.ACTIVE
        sub.save(update_fields=["status", "updated_at"])
        return _ok(SubscriptionSerializer(sub).data)


class SubscriptionRenewView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def post(self, request, pk):
        try:
            sub = Subscription.objects.get(pk=pk)
        except Subscription.DoesNotExist:
            return _err("Subscription not found.", status.HTTP_404_NOT_FOUND)

        if sub.status not in (Subscription.Status.ACTIVE, Subscription.Status.PAUSED, Subscription.Status.EXPIRED):
            return _err(f"Cannot renew subscription with status '{sub.status}'.", status.HTTP_400_BAD_REQUEST)

        # Extend billing period
        sub.next_billing_date = calculate_next_billing_date(sub.next_billing_date or date.today(), sub.billing_interval)
        sub.status = Subscription.Status.ACTIVE
        sub.save(update_fields=["next_billing_date", "status", "updated_at"])
        return _ok(SubscriptionSerializer(sub).data)


class SubscriptionCloseView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def post(self, request, pk):
        try:
            sub = Subscription.objects.get(pk=pk)
        except Subscription.DoesNotExist:
            return _err("Subscription not found.", status.HTTP_404_NOT_FOUND)

        if sub.status == Subscription.Status.CANCELLED:
            return _err("Subscription is already closed/cancelled.", status.HTTP_400_BAD_REQUEST)

        sub.status = Subscription.Status.CANCELLED
        sub.cancelled_at = timezone.now()
        sub.save(update_fields=["status", "cancelled_at", "updated_at"])
        return _ok(SubscriptionSerializer(sub).data)
