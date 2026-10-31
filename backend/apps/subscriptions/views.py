from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Subscription
from .serializers import SubscriptionSerializer, ConvertQuotationSerializer
from . import services
from apps.quotations.models import Quotation
from apps.users.permissions import IsAdminOrStaff


def _ok(data):
    return Response({"data": data, "error": None})


def _created(data):
    return Response({"data": data, "error": None}, status=status.HTTP_201_CREATED)


def _err(msg, code=status.HTTP_400_BAD_REQUEST):
    return Response({"data": None, "error": msg}, status=code)


class SubscriptionListView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        status_filter = request.query_params.get("status")
        customer_filter = request.query_params.get("customer_id")
        
        qs = Subscription.objects.all().select_related("customer", "quotation")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if customer_filter:
            qs = qs.filter(customer_id=customer_filter)
            
        return _ok(SubscriptionSerializer(qs, many=True).data)


class SubscriptionDetailView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request, pk):
        sub = get_object_or_404(Subscription.objects.select_related("customer", "quotation"), pk=pk)
        return _ok(SubscriptionSerializer(sub).data)


class ConvertQuotationView(APIView):
    """
    POST /api/subscriptions/convert/<quotation_id>/
    Converts an ACCEPTED quotation into an ACTIVE Subscription.
    """
    permission_classes = [IsAdminOrStaff]

    def post(self, request, quotation_id):
        quotation = get_object_or_404(Quotation, pk=quotation_id)
        s = ConvertQuotationSerializer(data=request.data)
        if not s.is_valid():
            return _err(s.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)
            
        try:
            sub = services.convert_quotation_to_subscription(
                quotation=quotation,
                start_date=s.validated_data["start_date"],
                billing_interval=s.validated_data["billing_interval"],
                created_by=request.user,
            )
            return _created(SubscriptionSerializer(sub).data)
        except ValueError as e:
            return _err(str(e))


class SubscriptionPauseView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        sub = get_object_or_404(Subscription, pk=pk)
        try:
            updated = services.pause_subscription(sub)
            return _ok(SubscriptionSerializer(updated).data)
        except ValueError as e:
            return _err(str(e))


class SubscriptionResumeView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        sub = get_object_or_404(Subscription, pk=pk)
        try:
            updated = services.resume_subscription(sub)
            return _ok(SubscriptionSerializer(updated).data)
        except ValueError as e:
            return _err(str(e))


class SubscriptionRenewView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        sub = get_object_or_404(Subscription, pk=pk)
        try:
            updated = services.renew_subscription(sub)
            return _ok(SubscriptionSerializer(updated).data)
        except ValueError as e:
            return _err(str(e))


class SubscriptionCloseView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        sub = get_object_or_404(Subscription, pk=pk)
        try:
            updated = services.close_subscription(sub)
            return _ok(SubscriptionSerializer(updated).data)
        except ValueError as e:
            return _err(str(e))
