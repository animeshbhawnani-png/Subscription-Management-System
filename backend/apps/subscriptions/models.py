"""
Subscription model. Created by converting an accepted Quotation.
Module 5 (Invoicing) reads from this table.
"""
from django.db import models
from django.conf import settings
from apps.customers.models import Customer
from apps.quotations.models import Quotation


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE   = "active",   "Active"
        PAUSED   = "paused",   "Paused"
        CLOSED   = "closed",   "Closed"
        EXPIRED  = "expired",  "Expired"

    class BillingInterval(models.TextChoices):
        DAILY    = "daily",    "Daily"
        WEEKLY   = "weekly",   "Weekly"
        MONTHLY  = "monthly",  "Monthly"
        YEARLY   = "yearly",   "Yearly"

    quotation = models.OneToOneField(
        Quotation, on_delete=models.PROTECT,
        related_name="subscription",
        help_text="Source quotation that was converted"
    )
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="subscriptions")

    # shortcut: plan_id is an int ref to Module 3; replace with FK when merged
    plan_id = models.IntegerField(null=True, blank=True)
    plan_name = models.CharField(max_length=200, blank=True)  # snapshot
    billing_interval = models.CharField(
        max_length=10, choices=BillingInterval.choices, default=BillingInterval.MONTHLY
    )

    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    agreed_price = models.DecimalField(max_digits=12, decimal_places=2,
                                       help_text="Grand total agreed in quotation")

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_billing_date = models.DateField(null=True, blank=True)

    paused_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    renewal_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="subscriptions_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"SUB-{self.pk} | {self.customer.company_name} | {self.status}"
