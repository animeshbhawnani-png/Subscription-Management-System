from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Product, ProductVariant


User = get_user_model()


class ProductAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user("admin-products@test.com", "Pass@word1", role="admin")
        self.customer = User.objects.create_user("customer-products@test.com", "Pass@word1")
        self.client.force_authenticate(self.admin)
        self.payload = {
            "name": "Accounting",
            "product_type": "Software",
            "sales_price": "1000.00",
            "cost_price": "400.00",
            "notes": "Annual plan",
        }

    def test_product_crud_and_search(self):
        response = self.client.post("/api/products/", self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        product_id = response.json()["data"]["id"]

        response = self.client.get("/api/products/?search=account")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)

        response = self.client.put(
            f"/api/products/{product_id}/",
            {**self.payload, "name": "Accounting Pro"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["name"], "Accounting Pro")

        response = self.client.delete(f"/api/products/{product_id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Product.objects.filter(pk=product_id).exists())

    def test_variant_final_price_crud(self):
        product = Product.objects.create(
            name="CRM",
            product_type="Software",
            sales_price=Decimal("1000.00"),
            cost_price=Decimal("500.00"),
        )
        response = self.client.post(
            f"/api/products/{product.id}/variants/",
            {"name": "Odoo", "additional_price": "560.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        variant_id = response.json()["data"]["id"]
        self.assertEqual(response.json()["data"]["final_price"], "1560.00")

        response = self.client.put(
            f"/api/products/{product.id}/variants/{variant_id}/",
            {"name": "Odoo Enterprise", "additional_price": "600.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["final_price"], "1600.00")

        response = self.client.delete(f"/api/products/{product.id}/variants/{variant_id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(ProductVariant.objects.filter(pk=variant_id).exists())

    def test_invalid_prices_and_required_fields_are_rejected(self):
        response = self.client.post(
            "/api/products/",
            {**self.payload, "name": " ", "sales_price": "-1"},
            format="json",
        )
        self.assertEqual(response.status_code, 422)

        product = Product.objects.create(
            name="Support",
            product_type="Service",
            sales_price=Decimal("10.00"),
            cost_price=Decimal("5.00"),
        )
        response = self.client.post(
            f"/api/products/{product.id}/variants/",
            {"name": " ", "additional_price": "-2"},
            format="json",
        )
        self.assertEqual(response.status_code, 422)

    def test_only_admin_can_manage_products(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(None)
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 401)
