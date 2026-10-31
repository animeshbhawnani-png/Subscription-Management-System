from rest_framework import serializers
from .models import Quotation, QuotationItem, QuotationTemplate
from apps.quotations import services


class QuotationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationTemplate
        fields = ["id", "name", "validity_days", "payment_terms", "notes", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ["id", "product_id", "plan_id", "description", "quantity",
                  "unit_price", "discount_percent", "tax_rate",
                  "line_subtotal", "line_discount", "line_tax", "line_total"]
        read_only_fields = ["id", "line_subtotal", "line_discount", "line_tax", "line_total"]


class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.company_name", read_only=True)

    class Meta:
        model = Quotation
        fields = [
            "id", "quotation_number", "customer", "customer_name", "template",
            "status", "quotation_date", "expiry_date", "payment_terms", "notes",
            "subtotal", "discount_amount", "taxable_amount", "tax_amount", "grand_total",
            "items", "created_at",
        ]
        read_only_fields = [
            "id", "quotation_number", "quotation_date", "status",
            "subtotal", "discount_amount", "taxable_amount", "tax_amount", "grand_total",
            "created_at",
        ]


class QuotationCreateSerializer(serializers.ModelSerializer):
    """Used on POST — accepts items inline, calculates totals server-side."""
    items = QuotationItemSerializer(many=True)

    class Meta:
        model = Quotation
        fields = ["customer", "template", "expiry_date", "payment_terms", "notes", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user
        quotation = Quotation.objects.create(
            quotation_number=services.generate_quotation_number(),
            created_by=user,
            **validated_data,
        )
        for item_data in items_data:
            item = QuotationItem(quotation=quotation, **item_data)
            services.compute_item(item)
            item.save()
        services.recalculate_quotation(quotation)
        return quotation

