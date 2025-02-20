from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views.report_views import ReportResultView, ReportView
from api.v1.viewsets.order_viewsets import OrderViewSet
from api.v1.viewsets.product_viewsets import ProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="products")
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("", include(router.urls)),
    path("reports/get_report", ReportView.as_view(), name="reports"),
    path("reports/status/", ReportResultView.as_view(), name="report-status"),
]
