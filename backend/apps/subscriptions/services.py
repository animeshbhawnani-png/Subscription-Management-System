"""
Business logic for subscription lifecycle.
"""
from datetime import date, timedelta
from django.db import transaction
from django.utils import timezone

from apps.quotations.models import Quotation
from .models import Subscription


def _billing_delta(interval: str) -> timedelta:
    return {
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
        "monthly": timedelta(days=30),
        "yearly": timedelta(days=365),
    }[interval]


@transaction.atomic
def convert_quotation_to_subscription(quotation: Quotation, start_date: date,
                                       billing_interval: str, created_by) -> Subscription:
    """
    Convert an accepted quotation into a subscription.
    Raises ValueError if quotation is not accepted or already converted.
    """
    if quotation.status != Quotation.Status.ACCEPTED:
        raise ValueError("Only accepted quotations can be converted to subscriptions.")
    if hasattr(quotation, "subscription"):
        raise ValueError("This quotation has already been converted.")

    delta = _billing_delta(billing_interval)
    next_billing = start_date + delta

    # Snapshot plan info from first item that has a plan_id
    plan_item = quotation.items.filter(plan_id__isnull=False).first()
    plan_id = plan_item.plan_id if plan_item else None
    plan_name = plan_item.description if plan_item else ""

    # Total quantity = sum of all item quantities
    total_qty = sum(i.quantity for i in quotation.items.all())

    sub = Subscription.objects.create(
        quotation=quotation,
        customer=quotation.customer,
        plan_id=plan_id,
        plan_name=plan_name,
        billing_interval=billing_interval,
        quantity=total_qty,
        agreed_price=quotation.grand_total,
        status=Subscription.Status.ACTIVE,
        start_date=start_date,
        next_billing_date=next_billing,
        created_by=created_by,
    )
    quotation.status = Quotation.Status.CONVERTED
    quotation.save(update_fields=["status"])
    return sub


def pause_subscription(sub: Subscription) -> Subscription:
    if sub.status != Subscription.Status.ACTIVE:
        raise ValueError("Only active subscriptions can be paused.")
    sub.status = Subscription.Status.PAUSED
    sub.paused_at = timezone.now()
    sub.save(update_fields=["status", "paused_at"])
    return sub


def resume_subscription(sub: Subscription) -> Subscription:
    if sub.status != Subscription.Status.PAUSED:
        raise ValueError("Only paused subscriptions can be resumed.")
    sub.status = Subscription.Status.ACTIVE
    sub.paused_at = None
    sub.save(update_fields=["status", "paused_at"])
    return sub


def renew_subscription(sub: Subscription) -> Subscription:
    if sub.status not in (Subscription.Status.ACTIVE, Subscription.Status.EXPIRED):
        raise ValueError("Only active or expired subscriptions can be renewed.")
    delta = _billing_delta(sub.billing_interval)
    sub.next_billing_date = (sub.next_billing_date or date.today()) + delta
    sub.renewal_count += 1
    sub.status = Subscription.Status.ACTIVE
    sub.save(update_fields=["next_billing_date", "renewal_count", "status"])
    return sub


def close_subscription(sub: Subscription) -> Subscription:
    if sub.status == Subscription.Status.CLOSED:
        raise ValueError("Subscription is already closed.")
    sub.status = Subscription.Status.CLOSED
    sub.closed_at = timezone.now()
    sub.save(update_fields=["status", "closed_at"])
    return sub

