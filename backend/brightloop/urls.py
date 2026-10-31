from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/customers/", include("apps.customers.urls")),
    path("api/quotations/", include("apps.quotations.urls")),
    path("api/subscriptions/", include("apps.subscriptions.urls")),
]
