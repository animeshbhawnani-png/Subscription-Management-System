from django.test import TestCase
from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth import get_user_model

from apps.customers.models import Customer
from apps.quotations.models import Quotation, QuotationItem
from apps.quotations import services as q_services
from apps.subscriptions import services as sub_services
from apps.subscriptions.models import Subscription

User = get_user_model()

class QuotationCalculationsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("staff@brightloop.com", "Pass@word1", role="staff")
        self.customer = Customer.objects.create(
            company_name="Acme Corp",
            contact_name="Alice Smith",
            email="alice@acme.com"
        )
        self.quotation = Quotation.objects.create(
            quotation_number=q_services.generate_quotation_number(),
            customer=self.customer,
            expiry_date=date.today() + timedelta(days=15),
            created_by=self.user
        )

    def test_calculation_formula(self):
        # Spec calculation:
        # Software subscription unit 2000, qty 2 -> subtotal 4000
        # Discount 10% (400) -> taxable 3600
        # Tax 18% (648) -> line total 4248
        item = QuotationItem(
            quotation=self.quotation,
            description="Software Subscription",
            quantity=Decimal("2"),
            unit_price=Decimal("2000.00"),
            discount_percent=Decimal("10.00"),
            tax_rate=Decimal("18.00"),
        )
        q_services.compute_item(item)
        item.save()
        q_services.recalculate_quotation(self.quotation)

        self.assertEqual(item.line_subtotal, Decimal("4000.00"))
        self.assertEqual(item.line_discount, Decimal("400.00"))
        self.assertEqual(item.line_tax, Decimal("648.00"))
        self.assertEqual(item.line_total, Decimal("4248.00"))

        self.quotation.refresh_from_db()
        self.assertEqual(self.quotation.subtotal, Decimal("4000.00"))
        self.assertEqual(self.quotation.discount_amount, Decimal("400.00"))
        self.assertEqual(self.quotation.taxable_amount, Decimal("3600.00"))
        self.assertEqual(self.quotation.tax_amount, Decimal("648.00"))
        self.assertEqual(self.quotation.grand_total, Decimal("4248.00"))

    def test_workflow_lifecycle_and_conversion(self):
        # 1. Draft -> Sent
        q_services.send_quotation(self.quotation)
        self.assertEqual(self.quotation.status, Quotation.Status.SENT)

        # 2. Sent -> Accepted
        q_services.accept_quotation(self.quotation)
        self.assertEqual(self.quotation.status, Quotation.Status.ACCEPTED)

        # 3. Accepted -> Subscription conversion
        item = QuotationItem.objects.create(
            quotation=self.quotation,
            plan_id=202,
            description="Professional Tier",
            quantity=Decimal("1"),
            unit_price=Decimal("999.00"),
            line_subtotal=Decimal("999.00"),
            line_total=Decimal("999.00")
        )
        self.quotation.grand_total = Decimal("999.00")
        self.quotation.save()

        sub = sub_services.convert_quotation_to_subscription(
            quotation=self.quotation,
            start_date=date.today(),
            billing_interval="monthly",
            created_by=self.user
        )

        self.assertEqual(sub.status, Subscription.Status.ACTIVE)
        self.assertEqual(sub.agreed_price, Decimal("999.00"))
        self.assertEqual(sub.plan_id, 202)
        self.quotation.refresh_from_db()
        self.assertEqual(self.quotation.status, Quotation.Status.CONVERTED)

        # 4. Duplicate conversion rejected
        with self.assertRaises(ValueError):
            sub_services.convert_quotation_to_subscription(
                quotation=self.quotation,
                start_date=date.today(),
                billing_interval="monthly",
                created_by=self.user
            )

        # 5. Subscription lifecycle: pause, resume, renew, close
        sub_services.pause_subscription(sub)
        self.assertEqual(sub.status, Subscription.Status.PAUSED)

        sub_services.resume_subscription(sub)
        self.assertEqual(sub.status, Subscription.Status.ACTIVE)

        sub_services.renew_subscription(sub)
        self.assertEqual(sub.renewal_count, 1)

        sub_services.close_subscription(sub)
        self.assertEqual(sub.status, Subscription.Status.CLOSED)
