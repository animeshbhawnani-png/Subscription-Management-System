"""
Quotation and QuotationTemplate models.

Integration pattern (snapshot):
  - product_id / plan_id store the FK reference to Module 2/3 tables.
  - product_name, unit_price etc. are snapshotted at quotation time so
    historical quotes never change when teammates update their data.

shortcut: product and plan FK fields point to integer IDs only (no DB FK
  constraint), because Module 2/3 tables don't exist yet. Replace with
  proper ForeignKey once teammates' apps are merged.
"""
from django.db import models
from django.conf import settings
from apps.customers.models import Customer


class QuotationTemplate(models.Model):
    name = models.CharField(max_length=200)
    validity_days = models.PositiveIntegerField(default=30, help_text="Default validity in days")
    payment_terms = models.TextField(blank=True, help_text="Default payment terms text")
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="quotation_templates"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quotation_templates"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Quotation(models.Model):
    class Status(models.TextChoices):
        DRAFT     = "draft",     "Draft"
        SENT      = "sent",      "Sent"
        ACCEPTED  = "accepted",  "Accepted"
        REJECTED  = "rejected",  "Rejected"
        EXPIRED   = "expired",   "Expired"
        CONVERTED = "converted", "Converted to Subscription"

    quotation_number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="quotations")
    template = models.ForeignKey(
        QuotationTemplate, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="quotations"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    quotation_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    payment_terms = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Calculated totals — always recomputed by the backend, never trusted from frontend
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="quotations_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quotations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.quotation_number} — {self.customer.company_name}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")

    # Snapshot fields (Module 2 / 3 integration contract)
    # shortcut: using plain int IDs instead of FK until Module 2/3 tables exist
    product_id = models.IntegerField(null=True, blank=True, help_text="Ref to Module 2 product")
    plan_id = models.IntegerField(null=True, blank=True, help_text="Ref to Module 3 plan")

    # Snapshotted at quotation creation — history-safe
    description = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                   help_text="Percentage e.g. 18 for 18% GST")

    # Computed by service layer
    line_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "quotation_items"

    def __str__(self):
        return f"{self.description} x{self.quantity}"
