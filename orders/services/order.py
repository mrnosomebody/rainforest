import uuid

from django.db import transaction
from django.db.models import F

from api.v1.exceptions import OrderCancellationError, OrderCreationError
from orders.dto import OrderDTO, OrderItemDTO
from orders.enums import OrderStatus
from orders.models import Order
from orders.services.order_item import create_order_items_service
from products.models import Product


def _get_locked_products(order_dto: OrderDTO) -> dict[uuid.UUID, Product]:
    product_ids = [item.product_id for item in order_dto.items]
    locked_products = Product.objects.select_for_update().filter(id__in=product_ids)
    return {product.id: product for product in locked_products}


def _calculate_stock_deltas(order_dto: OrderDTO) -> dict[uuid.UUID, int]:
    """
    Вычисляет суммарное требуемое уменьшение stock для каждого продукта.
    """
    stock_deltas: dict[uuid.UUID, int] = {}

    for item in order_dto.items:
        product_id = item.product_id
        stock_deltas[product_id] = stock_deltas.get(product_id, 0) + item.quantity

    return stock_deltas


def _update_products_stock(stock_deltas: dict, increase: bool = False) -> None:
    for product_id, quantity in stock_deltas.items():
        update_expr = F("stock") + quantity if increase else F("stock") - quantity
        Product.objects.filter(id=product_id).update(stock=update_expr)


def _check_order_stock(
    order_dto: OrderDTO, locked_products: dict[uuid.UUID, Product]
) -> None:
    for item in order_dto.items:
        product_id = item.product_id
        locked_product = locked_products.get(product_id)

        if locked_product is None:
            raise OrderCreationError(f"Product with id {product_id} not found.")

        if locked_product.stock < item.quantity:
            raise OrderCreationError(
                f"Not enough stock for product {locked_product.name}. Available: {locked_product.stock}"
            )


@transaction.atomic
def create_order_service(order_dto: OrderDTO) -> Order:
    """
    Создает заказ на основе валидированных данных из OrderCreateDTO.

    Логика:
      1. Получаем и блокируем продукты.
      2. Проверяем, что для каждого продукта достаточно stock.
      3. Вычисляем дельты для обновления stock.
      4. Обновляем stock.
      5. Создаем заказ и его позиции (order items).
    """
    locked_products = _get_locked_products(order_dto=order_dto)

    _check_order_stock(order_dto=order_dto, locked_products=locked_products)

    stock_deltas = _calculate_stock_deltas(order_dto=order_dto)
    _update_products_stock(stock_deltas=stock_deltas)

    order = Order.objects.create()

    create_order_items_service(
        order=order, order_dto=order_dto, locked_products=locked_products
    )

    return order


@transaction.atomic
def cancel_order_service(order: Order):
    if order.status == OrderStatus.CANCELED:
        raise OrderCancellationError(detail="Order is already canceled")

    order_items = [
        OrderItemDTO(product_id=item.product.id, quantity=item.quantity)
        for item in order.items.all()
    ]
    order_dto = OrderDTO(items=order_items)

    _get_locked_products(order_dto=order_dto)

    stock_deltas = _calculate_stock_deltas(order_dto=order_dto)
    _update_products_stock(stock_deltas=stock_deltas)

    Order.objects.filter(id=order.id).update(status=OrderStatus.CANCELED)
