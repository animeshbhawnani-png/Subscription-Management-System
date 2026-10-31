"""
Business logic for quotations.
All financial calculations happen here — never trust frontend totals.
"""
import uuid
from decimal import Decimal
from datetime import date, timedelta

from django.db import transaction

from .models import Quotation, QuotationItem


def generate_quotation_number():
    """QUO-YYYYMMDD-XXXX (unique 4-char hex suffix)."""
    today = date.today().strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:4].upper()
    number = f"QUO-{today}-{suffix}"
    # Retry on the rare collision
    while Quotation.objects.filter(quotation_number=number).exists():
        suffix = uuid.uuid4().hex[:4].upper()
        number = f"QUO-{today}-{suffix}"
    return number


def compute_item(item: QuotationItem) -> QuotationItem:
    """Recalculate a single line item. Returns the item (not yet saved)."""
    qty = Decimal(str(item.quantity))
    unit = Decimal(str(item.unit_price))
    disc_pct = Decimal(str(item.discount_percent))
    tax_pct = Decimal(str(item.tax_rate))

    subtotal = qty * unit
    discount = (subtotal * disc_pct / 100).quantize(Decimal("0.01"))
    taxable = subtotal - discount
    tax = (taxable * tax_pct / 100).quantize(Decimal("0.01"))
    total = taxable + tax

    item.line_subtotal = subtotal
    item.line_discount = discount
    item.line_tax = tax
    item.line_total = total
    return item


def recalculate_quotation(quotation: Quotation) -> Quotation:
    """
    Recompute all quotation-level totals from its items.
    Saves totals to DB. Call after any item add/edit/delete.
    """
    items = quotation.items.all()
    subtotal = sum(i.line_subtotal for i in items)
    discount = sum(i.line_discount for i in items)
    tax = sum(i.line_tax for i in items)
    taxable = subtotal - discount

    quotation.subtotal = subtotal
    quotation.discount_amount = discount
    quotation.taxable_amount = taxable
    quotation.tax_amount = tax
    quotation.grand_total = taxable + tax
    quotation.save(update_fields=[
        "subtotal", "discount_amount", "taxable_amount", "tax_amount", "grand_total"
    ])
    return quotation


def _assert_draft(quotation: Quotation):
    if quotation.status != Quotation.Status.DRAFT:
        raise ValueError(f"Quotation is '{quotation.status}' — only drafts can be edited.")


def send_quotation(quotation: Quotation) -> Quotation:
    _assert_draft(quotation)
    quotation.status = Quotation.Status.SENT
    quotation.save(update_fields=["status"])
    # shortcut: email dispatch not implemented; add Celery task when email creds ready
    return quotation


def accept_quotation(quotation: Quotation) -> Quotation:
    if quotation.status != Quotation.Status.SENT:
        raise ValueError("Only a sent quotation can be accepted.")
    quotation.status = Quotation.Status.ACCEPTED
    quotation.save(update_fields=["status"])
    return quotation


def reject_quotation(quotation: Quotation) -> Quotation:
    if quotation.status != Quotation.Status.SENT:
        raise ValueError("Only a sent quotation can be rejected.")
    quotation.status = Quotation.Status.REJECTED
    quotation.save(update_fields=["status"])
    return quotation


def expire_stale_quotations():
    """
    Mark sent/draft quotations whose expiry_date has passed as expired.
    shortcut: call this from a daily management command; Celery beat will replace it in Phase 7.
    """
    today = date.today()
    updated = Quotation.objects.filter(
        status__in=[Quotation.Status.DRAFT, Quotation.Status.SENT],
        expiry_date__lt=today,
    ).update(status=Quotation.Status.EXPIRED)
    return updated

