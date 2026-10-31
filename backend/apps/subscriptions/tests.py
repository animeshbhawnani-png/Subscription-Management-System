from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.products.models import Product, ProductVariant
from apps.subscriptions.models import Quotation, Subscription

User = get_user_model()


class Module3APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user("admin@test.com", "Pass@word1", role="admin")
        self.staff = User.objects.create_user("staff@test.com", "Pass@word1", role="staff")
        self.customer = User.objects.create_user("cust@test.com", "Pass@word1", role="customer")
        self.other_customer = User.objects.create_user("other@test.com", "Pass@word1", role="customer")

        # Products
        self.product = Product.objects.create(
            name="Cloud Storage",
            product_type="Software",
            sales_price=Decimal("100.00"),
            cost_price=Decimal("40.00"),
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name="1TB Extra",
            additional_price=Decimal("50.00"),
        )

    def test_quotation_creation_and_calculation(self):
        self.client.force_authenticate(self.staff)
        payload = {
            "customer_id": self.customer.id,
            "valid_until": "2026-12-31",
            "notes": "Introductory discount",
            "items": [
                {
                    "product_id": self.product.id,
                    "variant_id": self.variant.id,
                    "quantity": 2,
                }
            ],
        }
        res = self.client.post("/api/quotations/", payload, format="json")
        self.assertEqual(res.status_code, 201)
        data = res.json()["data"]
        self.assertTrue(data["quotation_number"].startswith("QT-"))
        # variant final_price is 100 + 50 = 150. 150 * 2 = 300.00
        self.assertEqual(Decimal(str(data["total"])), Decimal("300.00"))
        self.assertEqual(data["status"], "draft")

    def test_customer_isolation_and_acceptance(self):
        # Staff creates quote
        self.client.force_authenticate(self.staff)
        res = self.client.post(
            "/api/quotations/",
            {
                "customer_id": self.customer.id,
                "items": [{"product_id": self.product.id, "quantity": 1}],
            },
            format="json",
        )
        quote_id = res.json()["data"]["id"]

        # Other customer cannot access
        self.client.force_authenticate(self.other_customer)
        res_other = self.client.get(f"/api/quotations/{quote_id}/")
        self.assertEqual(res_other.status_code, 404)

        # Assigned customer can accept
        self.client.force_authenticate(self.customer)
        res_accept = self.client.post(f"/api/quotations/{quote_id}/accept/")
        self.assertEqual(res_accept.status_code, 200)
        self.assertEqual(res_accept.json()["data"]["status"], "accepted")

    def test_conversion_to_subscription_and_lifecycle(self):
        # Create and accept quotation
        self.client.force_authenticate(self.staff)
        res = self.client.post(
            "/api/quotations/",
            {
                "customer_id": self.customer.id,
                "items": [{"product_id": self.product.id, "quantity": 1}],
            },
            format="json",
        )
        quote_id = res.json()["data"]["id"]

        self.client.force_authenticate(self.customer)
        self.client.post(f"/api/quotations/{quote_id}/accept/")

        # Convert to subscription by staff
        self.client.force_authenticate(self.staff)
        res_convert = self.client.post(
            f"/api/quotations/{quote_id}/convert/",
            {"billing_interval": "monthly"},
            format="json",
        )
        self.assertEqual(res_convert.status_code, 201)
        sub_data = res_convert.json()["data"]
        sub_id = sub_data["id"]
        self.assertTrue(sub_data["subscription_number"].startswith("SUB-"))
        self.assertEqual(sub_data["status"], "active")

        # Duplicate conversion is prevented
        res_dup = self.client.post(f"/api/quotations/{quote_id}/convert/")
        self.assertEqual(res_dup.status_code, 400)

        # Pause subscription
        res_pause = self.client.post(f"/api/subscriptions/{sub_id}/pause/")
        self.assertEqual(res_pause.status_code, 200)
        self.assertEqual(res_pause.json()["data"]["status"], "paused")

        # Resume subscription
        res_resume = self.client.post(f"/api/subscriptions/{sub_id}/resume/")
        self.assertEqual(res_resume.status_code, 200)
        self.assertEqual(res_resume.json()["data"]["status"], "active")

        # Renew subscription
        res_renew = self.client.post(f"/api/subscriptions/{sub_id}/renew/")
        self.assertEqual(res_renew.status_code, 200)

        # Close subscription
        res_close = self.client.post(f"/api/subscriptions/{sub_id}/close/")
        self.assertEqual(res_close.status_code, 200)
        self.assertEqual(res_close.json()["data"]["status"], "cancelled")
