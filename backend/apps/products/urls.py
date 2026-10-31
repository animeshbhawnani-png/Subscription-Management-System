from django.urls import path

from .views import (
    ProductDetailView,
    ProductListCreateView,
    ProductVariantDetailView,
    ProductVariantListCreateView,
)

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="product-list-create"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("<int:product_pk>/variants/", ProductVariantListCreateView.as_view(), name="variant-list-create"),
    path(
        "<int:product_pk>/variants/<int:pk>/",
        ProductVariantDetailView.as_view(),
        name="variant-detail",
    ),
]
