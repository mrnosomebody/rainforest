from http.client import responses

from pydantic import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response

from api.v1.exceptions import OrderCreationError
from api.v1.serializers.order_serializers import OrderCreateSerializer, \
    OrderUpdateSerializer, OrderReadSerializer
from orders.dto import OrderCreateDTO
from orders.models import Order, OrderItem
from orders.services.order import create_order_service


class OrderViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer

        return OrderReadSerializer

    def get_queryset(self):
        return Order.objects.all()

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data['items']

        try:
            order_create_dto = OrderCreateDTO(items=validated_data)
        except ValidationError as exc:
            return Response(exc.errors(), status=status.HTTP_400_BAD_REQUEST)

        try:
            order = create_order_service(order_create_dto)
            print(order)
            print(order.__dict__)
        except OrderCreationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        print(order)
        print(order.__dict__)
        response_serializer = OrderReadSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """
        Позволяет обновить статус заказа.
        Если статус меняется на 'canceled', возвращаем товары на склад.
        Пример payload для отмены:
        { "status": "canceled" }
        """
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status == 'canceled' and order.status != 'canceled':
            # Возвращаем товары на склад
            for item in order.items.all():
                product = item.product
                product.stock += item.quantity
                product.save()
            order.status = 'canceled'
            order.save()

        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

