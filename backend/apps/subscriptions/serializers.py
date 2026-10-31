from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.company_name", read_only=True)
    quotation_number = serializers.CharField(source="quotation.quotation_number", read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id", "quotation", "quotation_number", "customer", "customer_name",
            "plan_id", "plan_name", "billing_interval", "quantity", "agreed_price",
            "status", "start_date", "end_date", "next_billing_date",
            "paused_at", "closed_at", "renewal_count", "notes", "created_at",
        ]
        read_only_fields = fields


class ConvertQuotationSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    billing_interval = serializers.ChoiceField(choices=["daily", "weekly", "monthly", "yearly"])

