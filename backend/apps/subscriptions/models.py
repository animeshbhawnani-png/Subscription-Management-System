from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Quotation(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"

    quotation_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quotations",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_quotations",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    valid_until = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "quotations"

    def __str__(self):
        return f"{self.quotation_number} ({self.customer.email}) - {self.status}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="quotation_items",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="quotation_items",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        db_table = "quotation_items"

    def __str__(self):
        return f"{self.quotation.quotation_number} - {self.product.name} (x{self.quantity})"


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    class BillingInterval(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"

    subscription_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    quotation = models.OneToOneField(
        Quotation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscription",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subscriptions",
    )
    contracted_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    billing_interval = models.CharField(
        max_length=20,
        choices=BillingInterval.choices,
        default=BillingInterval.MONTHLY,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    start_date = models.DateField()
    next_billing_date = models.DateField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "subscriptions"

    def __str__(self):
        return f"{self.subscription_number} - {self.customer.email} ({self.status})"
