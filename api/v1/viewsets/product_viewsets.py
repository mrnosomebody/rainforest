from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from api.v1.serializers.product_serializers import (
    ProductReadSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer
)
from products.models import Product


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    filter_backends = [OrderingFilter]
    ordering_fields = ['name', 'price', 'stock']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer

        return ProductReadSerializer



