from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status, viewsets
from rest_framework.response import Response

from api.v1.exceptions import OrderCreationError
from api.v1.pagination import DefaultCursorPagination
from api.v1.serializers.order_serializers import (
    OrderCreateSerializer,
    OrderReadSerializer,
    OrderUpdateSerializer,
)
from orders.dto import OrderDTO, OrderItemDTO
from orders.enums import OrderStatus
from orders.models import Order
from orders.services.order import cancel_order_service, create_order_service


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    pagination_class = DefaultCursorPagination

    serializer_class_map = {
        "create": OrderCreateSerializer,
        "update": OrderUpdateSerializer,
        "partial_update": OrderUpdateSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_class_map.get(self.action, OrderReadSerializer)

    @method_decorator(ratelimit(key="ip", rate="5/m", block=True))
    def create(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        validated_data = request_serializer.validated_data["items"]

        order_dto = OrderDTO(items=[OrderItemDTO(**item) for item in validated_data])

        try:
            order = create_order_service(order_dto)
        except OrderCreationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = OrderReadSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @method_decorator(ratelimit(key="ip", rate="5/m", block=True))
    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get("status")

        if new_status == OrderStatus.CANCELED:
            cancel_order_service(order=order)

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
