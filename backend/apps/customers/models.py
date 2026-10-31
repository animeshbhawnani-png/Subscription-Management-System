from django.db import models
from django.conf import settings


class Customer(models.Model):
    """
    Owned by Module 4. Teammates' modules reference customer_id.
    Links to the auth user record for login; extra business fields stored here.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        null=True,
        blank=True,
    )
    company_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=20, blank=True, help_text="GST Identification Number")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"
        ordering = ["company_name"]

    def __str__(self):
        return f"{self.company_name} ({self.email})"
