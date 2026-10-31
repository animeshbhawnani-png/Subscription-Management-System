"""
Module 1 – Auth & User Management tests.
Run with: python manage.py test apps.users
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_customer(self):
        u = User.objects.create_user("c@test.com", "Pass@word1")
        self.assertEqual(u.role, "customer")
        self.assertTrue(u.check_password("Pass@word1"))

    def test_create_staff(self):
        u = User.objects.create_user("s@test.com", "Pass@word1", role="staff")
        self.assertEqual(u.role, "staff")

    def test_create_superuser(self):
        u = User.objects.create_superuser("a@test.com", "Pass@word1")
        self.assertEqual(u.role, "admin")
        self.assertTrue(u.is_superuser)

    def test_email_unique(self):
        User.objects.create_user("dup@test.com", "Pass@word1")
        with self.assertRaises(Exception):
            User.objects.create_user("dup@test.com", "Pass@word1")


class RegisterAPITests(TestCase):
    def test_register_success(self):
        r = self.client.post(
            "/api/auth/register/",
            {"email": "new@test.com", "password": "Pass@word1"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertIsNone(r.json()["error"])

    def test_register_weak_password(self):
        r = self.client.post(
            "/api/auth/register/",
            {"email": "x@test.com", "password": "weak"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 422)

    def test_register_duplicate_email(self):
        payload = {"email": "dup2@test.com", "password": "Pass@word1"}
        self.client.post("/api/auth/register/", payload, content_type="application/json")
        r = self.client.post("/api/auth/register/", payload, content_type="application/json")
        self.assertGreaterEqual(r.status_code, 400)

    def test_login_and_me(self):
        User.objects.create_user("me@test.com", "Pass@word1")
        r = self.client.post(
            "/api/auth/login/",
            {"email": "me@test.com", "password": "Pass@word1"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        token = r.json()["access"]
        r2 = self.client.get(
            "/api/auth/me/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["data"]["email"], "me@test.com")
