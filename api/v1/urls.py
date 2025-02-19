from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.v1.viewsets.product_viewsets import ProductViewSet
from api.v1.viewsets.order_viewsets import OrderViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
]
