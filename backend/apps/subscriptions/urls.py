from django.urls import path
from .views import (
    CatalogListView,
    CustomerListView,
    QuotationAcceptView,
    QuotationConvertView,
    QuotationDetailView,
    QuotationListCreateView,
    QuotationRejectView,
    SubscriptionCloseView,
    SubscriptionDetailView,
    SubscriptionListView,
    SubscriptionPauseView,
    SubscriptionRenewView,
    SubscriptionResumeView,
)

urlpatterns = [
    # Helpers for Quotation Building
    path("customers/", CustomerListView.as_view(), name="customer-list"),
    path("catalog/", CatalogListView.as_view(), name="catalog-list"),

    # Quotations
    path("quotations/", QuotationListCreateView.as_view(), name="quotation-list-create"),
    path("quotations/<int:pk>/", QuotationDetailView.as_view(), name="quotation-detail"),
    path("quotations/<int:pk>/accept/", QuotationAcceptView.as_view(), name="quotation-accept"),
    path("quotations/<int:pk>/reject/", QuotationRejectView.as_view(), name="quotation-reject"),
    path("quotations/<int:pk>/convert/", QuotationConvertView.as_view(), name="quotation-convert"),

    # Subscriptions
    path("subscriptions/", SubscriptionListView.as_view(), name="subscription-list"),
    path("subscriptions/<int:pk>/", SubscriptionDetailView.as_view(), name="subscription-detail"),
    path("subscriptions/<int:pk>/pause/", SubscriptionPauseView.as_view(), name="subscription-pause"),
    path("subscriptions/<int:pk>/resume/", SubscriptionResumeView.as_view(), name="subscription-resume"),
    path("subscriptions/<int:pk>/renew/", SubscriptionRenewView.as_view(), name="subscription-renew"),
    path("subscriptions/<int:pk>/close/", SubscriptionCloseView.as_view(), name="subscription-close"),
]
