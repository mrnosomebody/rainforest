import logging

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.v1.pagination import DefaultCursorPagination
from api.v1.serializers.product_serializers import (
    ProductCreateSerializer,
    ProductReadSerializer,
    ProductUpdateSerializer,
)
from cache.product_cache import get_product_cache
from products.models import Product

logger = logging.getLogger(__name__)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    filter_backends = [OrderingFilter]
    ordering_fields = ["name", "price", "stock"]
    pagination_class = DefaultCursorPagination
    serializer_class_map = {
        "create": ProductCreateSerializer,
        "update": ProductUpdateSerializer,
        "partial_update": ProductUpdateSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_class_map.get(self.action, ProductReadSerializer)

    @method_decorator(ratelimit(key="ip", rate="10/m", block=True))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        product_cache = get_product_cache()
        cached_data = product_cache.get_product(pk)

        if cached_data:
            logger.info("ProductCache hit")
            return Response(cached_data)

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        product_cache.set_product(pk, serializer.data)

        return Response(serializer.data)
