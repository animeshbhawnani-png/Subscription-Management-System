from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "plan_name", "billing_interval", "agreed_price", "status", "start_date", "next_billing_date")
    list_filter = ("status", "billing_interval", "start_date")
    search_fields = ("customer__company_name", "plan_name")
    readonly_fields = ("created_at", "updated_at")
