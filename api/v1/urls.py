from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from api.v1.views.report_views import ReportResultView, ReportView
from api.v1.viewsets.order_viewsets import OrderViewSet
from api.v1.viewsets.product_viewsets import ProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="products")
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("", include(router.urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema-v1"),
    path(
        "schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema-v1"),
        name="swagger-ui-v1",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema-v1"),
        name="redoc-v1",
    ),
    path("reports/get_report", ReportView.as_view(), name="reports"),
    path("reports/status/", ReportResultView.as_view(), name="report-status"),
]
