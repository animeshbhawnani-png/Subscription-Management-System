from rest_framework import serializers

from .models import Product, ProductVariant


class ProductVariantSerializer(serializers.ModelSerializer):
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ["id", "product", "name", "additional_price", "final_price"]
        read_only_fields = ["id", "product", "final_price"]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Variant name is required.")
        return value.strip()


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_type",
            "sales_price",
            "cost_price",
            "notes",
            "created_at",
            "updated_at",
            "variants",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "variants"]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Product name is required.")
        return value.strip()

    def validate_product_type(self, value):
        if not value.strip():
            raise serializers.ValidationError("Product type is required.")
        return value.strip()


class ProductVariantCreateSerializer(ProductVariantSerializer):
    class Meta(ProductVariantSerializer.Meta):
        read_only_fields = ["id", "product", "final_price"]
