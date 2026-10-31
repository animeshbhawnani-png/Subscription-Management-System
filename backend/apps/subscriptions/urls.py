from django.urls import path
from .views import (
    SubscriptionListView,
    SubscriptionDetailView,
    ConvertQuotationView,
    SubscriptionPauseView,
    SubscriptionResumeView,
    SubscriptionRenewView,
    SubscriptionCloseView,
)

urlpatterns = [
    path("", SubscriptionListView.as_view(), name="subscription-list"),
    path("<int:pk>/", SubscriptionDetailView.as_view(), name="subscription-detail"),
    path("convert/<int:quotation_id>/", ConvertQuotationView.as_view(), name="subscription-convert"),
    path("<int:pk>/pause/", SubscriptionPauseView.as_view(), name="subscription-pause"),
    path("<int:pk>/resume/", SubscriptionResumeView.as_view(), name="subscription-resume"),
    path("<int:pk>/renew/", SubscriptionRenewView.as_view(), name="subscription-renew"),
    path("<int:pk>/close/", SubscriptionCloseView.as_view(), name="subscription-close"),
]

