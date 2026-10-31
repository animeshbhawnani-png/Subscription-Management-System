from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.products.models import Product, ProductVariant
from apps.products.serializers import ProductSerializer, ProductVariantSerializer
from .models import Quotation, QuotationItem, Subscription

User = get_user_model()


class QuotationItemWriteSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
    )
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source="variant",
        required=False,
        allow_null=True,
    )
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, attrs):
        product = attrs.get("product")
        variant = attrs.get("variant")
        if variant and variant.product_id != product.id:
            raise serializers.ValidationError(
                f"Variant '{variant.name}' does not belong to product '{product.name}'."
            )
        return attrs


class QuotationItemReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    variant_name = serializers.CharField(source="variant.name", read_only=True, default=None)

    class Meta:
        model = QuotationItem
        fields = [
            "id",
            "product",
            "product_name",
            "variant",
            "variant_name",
            "quantity",
            "unit_price",
            "subtotal",
        ]
        read_only_fields = fields


class QuotationCreateUpdateSerializer(serializers.ModelSerializer):
    items = QuotationItemWriteSerializer(many=True, write_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="customer",
        required=False,
    )

    class Meta:
        model = Quotation
        fields = [
            "id",
            "customer_id",
            "valid_until",
            "notes",
            "items",
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value


class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemReadSerializer(many=True, read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    created_by_email = serializers.CharField(source="created_by.email", read_only=True, default=None)
    has_subscription = serializers.SerializerMethodField()
    subscription_id = serializers.SerializerMethodField()
    subscription_number = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
        fields = [
            "id",
            "quotation_number",
            "customer",
            "customer_email",
            "created_by",
            "created_by_email",
            "status",
            "valid_until",
            "subtotal",
            "total",
            "notes",
            "has_subscription",
            "subscription_id",
            "subscription_number",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_has_subscription(self, obj):
        return hasattr(obj, "subscription") and obj.subscription is not None

    def get_subscription_id(self, obj):
        if hasattr(obj, "subscription") and obj.subscription is not None:
            return obj.subscription.id
        return None

    def get_subscription_number(self, obj):
        if hasattr(obj, "subscription") and obj.subscription is not None:
            return obj.subscription.subscription_number
        return None


class SubscriptionSerializer(serializers.ModelSerializer):
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    variant_name = serializers.CharField(source="variant.name", read_only=True, default=None)
    quotation_number = serializers.CharField(source="quotation.quotation_number", read_only=True, default=None)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "subscription_number",
            "customer",
            "customer_email",
            "quotation",
            "quotation_number",
            "product",
            "product_name",
            "variant",
            "variant_name",
            "contracted_price",
            "billing_interval",
            "status",
            "start_date",
            "next_billing_date",
            "cancelled_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ConvertQuotationSerializer(serializers.Serializer):
    billing_interval = serializers.ChoiceField(
        choices=Subscription.BillingInterval.choices,
        default=Subscription.BillingInterval.MONTHLY,
    )
