from django.urls import path
from .views import (
    QuotationListCreateView,
    QuotationDetailView,
    QuotationSendView,
    QuotationAcceptView,
    QuotationRejectView,
    QuotationTemplateListCreateView,
    QuotationTemplateDetailView,
    MockCatalogView,
)

urlpatterns = [
    # Quotations
    path("", QuotationListCreateView.as_view(), name="quotation-list-create"),
    path("<int:pk>/", QuotationDetailView.as_view(), name="quotation-detail"),
    path("<int:pk>/send/", QuotationSendView.as_view(), name="quotation-send"),
    path("<int:pk>/accept/", QuotationAcceptView.as_view(), name="quotation-accept"),
    path("<int:pk>/reject/", QuotationRejectView.as_view(), name="quotation-reject"),
    # Templates
    path("templates/", QuotationTemplateListCreateView.as_view(), name="template-list-create"),
    path("templates/<int:pk>/", QuotationTemplateDetailView.as_view(), name="template-detail"),
    # Integration Stubs for Module 2 & 3
    path("catalog-preview/", MockCatalogView.as_view(), name="catalog-preview"),
]

