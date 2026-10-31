from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Quotation, QuotationTemplate
from .serializers import (
    QuotationSerializer,
    QuotationCreateSerializer,
    QuotationTemplateSerializer,
)
from . import services
from apps.users.permissions import IsAdminOrStaff


def _ok(data):
    return Response({"data": data, "error": None})


def _created(data):
    return Response({"data": data, "error": None}, status=status.HTTP_201_CREATED)


def _err(msg, code=status.HTTP_400_BAD_REQUEST):
    return Response({"data": None, "error": msg}, status=code)


# ── Quotation Template Views ──────────────────────────────────────────────────
class QuotationTemplateListCreateView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        templates = QuotationTemplate.objects.filter(is_active=True)
        return _ok(QuotationTemplateSerializer(templates, many=True).data)

    def post(self, request):
        s = QuotationTemplateSerializer(data=request.data)
        if not s.is_valid():
            return _err(s.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)
        template = s.save(created_by=request.user)
        return _created(QuotationTemplateSerializer(template).data)


class QuotationTemplateDetailView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request, pk):
        template = get_object_or_404(QuotationTemplate, pk=pk)
        return _ok(QuotationTemplateSerializer(template).data)

    def put(self, request, pk):
        template = get_object_or_404(QuotationTemplate, pk=pk)
        s = QuotationTemplateSerializer(template, data=request.data, partial=True)
        if not s.is_valid():
            return _err(s.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)
        s.save()
        return _ok(s.data)

    def delete(self, request, pk):
        template = get_object_or_404(QuotationTemplate, pk=pk)
        template.is_active = False
        template.save(update_fields=["is_active"])
        return _ok({"detail": "Template deactivated successfully."})


# ── Quotation Views ───────────────────────────────────────────────────────────
class QuotationListCreateView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        status_filter = request.query_params.get("status")
        customer_filter = request.query_params.get("customer_id")
        
        services.expire_stale_quotations()
        qs = Quotation.objects.all().select_related("customer", "template").prefetch_related("items")
        if status_filter:
            qs = qs.filter(status=status_filter)
        if customer_filter:
            qs = qs.filter(customer_id=customer_filter)

        return _ok(QuotationSerializer(qs, many=True).data)

    def post(self, request):
        s = QuotationCreateSerializer(data=request.data, context={"request": request})
        if not s.is_valid():
            return _err(s.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)
        quotation = s.save()
        return _created(QuotationSerializer(quotation).data)


class QuotationDetailView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request, pk):
        services.expire_stale_quotations()
        quotation = get_object_or_404(
            Quotation.objects.select_related("customer", "template").prefetch_related("items"),
            pk=pk,
        )
        return _ok(QuotationSerializer(quotation).data)

    def put(self, request, pk):
        quotation = get_object_or_404(Quotation, pk=pk)
        if quotation.status != Quotation.Status.DRAFT:
            return _err("Only draft quotations can be modified.")
        
        # Simple metadata update (expiry, notes, payment_terms)
        allowed_fields = ["expiry_date", "payment_terms", "notes", "template"]
        for f in allowed_fields:
            if f in request.data:
                setattr(quotation, f, request.data[f])
        quotation.save()
        return _ok(QuotationSerializer(quotation).data)


class QuotationSendView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        quotation = get_object_or_404(Quotation, pk=pk)
        try:
            q = services.send_quotation(quotation)
            return _ok(QuotationSerializer(q).data)
        except ValueError as e:
            return _err(str(e))


class QuotationAcceptView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        quotation = get_object_or_404(Quotation, pk=pk)
        try:
            q = services.accept_quotation(quotation)
            return _ok(QuotationSerializer(q).data)
        except ValueError as e:
            return _err(str(e))


class QuotationRejectView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        quotation = get_object_or_404(Quotation, pk=pk)
        try:
            q = services.reject_quotation(quotation)
            return _ok(QuotationSerializer(q).data)
        except ValueError as e:
            return _err(str(e))


# ── Temporary Catalog API (Stubs for Module 2 & Module 3 integration) ────────
class MockCatalogView(APIView):
    """
    Supplies development catalog for Module 2 (Products) and Module 3 (Plans)
    until teammate modules are merged.
    """
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        products = [
            {"id": 101, "name": "Business Software", "product_type": "service", "sales_price": 2000.00, "is_available": True},
            {"id": 102, "name": "Enterprise Analytics Add-on", "product_type": "service", "sales_price": 750.00, "is_available": True},
            {"id": 103, "name": "Cloud Storage Pack (100GB)", "product_type": "service", "sales_price": 300.00, "is_available": True},
        ]
        plans = [
            {"id": 201, "name": "Basic Monthly", "price": 499.00, "billing_interval": "monthly", "minimum_quantity": 1, "is_active": True},
            {"id": 202, "name": "Professional Tier", "price": 999.00, "billing_interval": "monthly", "minimum_quantity": 1, "is_active": True},
            {"id": 203, "name": "Enterprise Annual", "price": 9999.00, "billing_interval": "yearly", "minimum_quantity": 5, "is_active": True},
        ]
        return _ok({"products": products, "plans": plans})
