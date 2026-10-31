from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "company_name", "contact_name", "email", "phone",
                  "address", "gstin", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

