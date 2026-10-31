from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.products.models import Product, ProductVariant
from .models import Quotation, QuotationItem, Subscription


def calculate_next_billing_date(current_date, billing_interval):
    """Calculate the next billing date based on billing interval."""
    if billing_interval == Subscription.BillingInterval.MONTHLY:
        return current_date + relativedelta(months=1)
    elif billing_interval == Subscription.BillingInterval.QUARTERLY:
        return current_date + relativedelta(months=3)
    elif billing_interval == Subscription.BillingInterval.YEARLY:
        return current_date + relativedelta(years=1)
    return current_date + relativedelta(months=1)


def generate_quotation_number():
    year = timezone.now().year
    prefix = f"QT-{year}-"
    last_quote = (
        Quotation.objects.filter(quotation_number__startswith=prefix)
        .order_by("-quotation_number")
        .first()
    )
    if not last_quote:
        return f"{prefix}0001"
    try:
        last_num = int(last_quote.quotation_number.split("-")[-1])
        next_num = last_num + 1
    except (ValueError, IndexError):
        next_num = 1
    return f"{prefix}{next_num:04d}"


def generate_subscription_number():
    year = timezone.now().year
    prefix = f"SUB-{year}-"
    last_sub = (
        Subscription.objects.filter(subscription_number__startswith=prefix)
        .order_by("-subscription_number")
        .first()
    )
    if not last_sub:
        return f"{prefix}0001"
    try:
        last_num = int(last_sub.subscription_number.split("-")[-1])
        next_num = last_num + 1
    except (ValueError, IndexError):
        next_num = 1
    return f"{prefix}{next_num:04d}"


@transaction.atomic
def create_or_update_quotation(customer, created_by, items_data, valid_until=None, notes="", instance=None):
    """Create or update quotation and compute total amounts."""
    if not items_data:
        raise ValidationError({"items": "At least one product item is required."})

    if instance is None:
        quotation = Quotation.objects.create(
            quotation_number=generate_quotation_number(),
            customer=customer,
            created_by=created_by,
            valid_until=valid_until,
            notes=notes,
            status=Quotation.Status.DRAFT,
        )
    else:
        quotation = instance
        if quotation.status != Quotation.Status.DRAFT:
            raise ValidationError({"status": "Only draft quotations can be edited."})
        if customer:
            quotation.customer = customer
        quotation.valid_until = valid_until
        quotation.notes = notes
        quotation.items.all().delete()

    subtotal_sum = Decimal("0.00")

    for item in items_data:
        product = item["product"]
        variant = item.get("variant")
        quantity = item.get("quantity", 1)

        if variant and variant.product_id != product.id:
            raise ValidationError(
                {"variant": f"Variant '{variant.name}' does not belong to product '{product.name}'."}
            )

        unit_price = variant.final_price if variant else product.sales_price
        line_subtotal = Decimal(unit_price) * Decimal(quantity)
        subtotal_sum += line_subtotal

        QuotationItem.objects.create(
            quotation=quotation,
            product=product,
            variant=variant,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=line_subtotal,
        )

    quotation.subtotal = subtotal_sum
    quotation.total = subtotal_sum
    quotation.save()
    return quotation


@transaction.atomic
def convert_quotation_to_subscription(quotation, billing_interval=Subscription.BillingInterval.MONTHLY):
    """Convert an accepted quotation into a subscription."""
    if quotation.status != Quotation.Status.ACCEPTED:
        raise ValidationError(
            {"detail": f"Only accepted quotations can be converted. Current status is '{quotation.status}'."}
        )

    if hasattr(quotation, "subscription") and quotation.subscription:
        raise ValidationError(
            {"detail": f"Quotation {quotation.quotation_number} has already been converted to subscription {quotation.subscription.subscription_number}."}
        )

    primary_item = quotation.items.first()
    if not primary_item:
        raise ValidationError({"detail": "Quotation contains no line items to convert."})

    today = date.today()
    next_billing = calculate_next_billing_date(today, billing_interval)

    subscription = Subscription.objects.create(
        subscription_number=generate_subscription_number(),
        customer=quotation.customer,
        quotation=quotation,
        product=primary_item.product,
        variant=primary_item.variant,
        contracted_price=quotation.total,
        billing_interval=billing_interval,
        status=Subscription.Status.ACTIVE,
        start_date=today,
        next_billing_date=next_billing,
        notes=f"Converted from quotation {quotation.quotation_number}. {quotation.notes}".strip(),
    )

    return subscription
