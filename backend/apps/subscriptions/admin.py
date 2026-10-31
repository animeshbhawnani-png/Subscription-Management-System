from django.contrib import admin
from .models import Quotation, QuotationItem, Subscription


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 0


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("quotation_number", "customer", "status", "total", "valid_until", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("quotation_number", "customer__email")
    inlines = [QuotationItemInline]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscription_number", "customer", "product", "status", "contracted_price", "billing_interval", "next_billing_date")
    list_filter = ("status", "billing_interval")
    search_fields = ("subscription_number", "customer__email", "product__name")
