from django.contrib import admin
from .models import Quotation, QuotationItem, QuotationTemplate

class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 0
    readonly_fields = ("line_subtotal", "line_discount", "line_tax", "line_total")

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("quotation_number", "customer", "status", "grand_total", "expiry_date", "created_at")
    list_filter = ("status", "quotation_date", "expiry_date")
    search_fields = ("quotation_number", "customer__company_name")
    readonly_fields = ("quotation_number", "subtotal", "discount_amount", "taxable_amount", "tax_amount", "grand_total", "created_at")
    inlines = [QuotationItemInline]

@admin.register(QuotationTemplate)
class QuotationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "validity_days", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
