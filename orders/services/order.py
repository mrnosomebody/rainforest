import uuid

from django.db import transaction
from django.db.models import F

from api.v1.exceptions import OrderCreationError
from orders.dto import OrderCreateDTO
from orders.models import Order
from orders.services.order_item import create_order_items_service
from products.models import Product


def _get_locked_products(order_create_dto: OrderCreateDTO) -> dict[uuid.UUID, Product]:
    """
    Получает и блокирует (select_for_update) все продукты, участвующие в заказе.

    :param order_create_dto: Объект OrderCreateDTO, содержащий список позиций заказа.
    :return: Словарь, где ключ — id продукта, значение — заблокированный экземпляр Product.
    """
    product_ids = [item.product_id for item in order_create_dto.items]
    locked_products = Product.objects.select_for_update().filter(id__in=product_ids)
    return {product.id: product for product in locked_products}


def _calculate_stock_deltas(order_create_dto: OrderCreateDTO) -> dict[uuid.UUID, int]:
    """
    Вычисляет суммарное требуемое уменьшение stock для каждого продукта.

    :param order_create_dto: DTO для создания заказа.
    :return: Словарь вида {product: quantity}.
    """
    stock_deltas = {}

    for item in order_create_dto.items:
        product_id = item.product_id
        stock_deltas[product_id] = stock_deltas.get(product_id, 0) + item.quantity

    return stock_deltas


def _update_products_stock(stock_deltas: dict) -> None:
    for product_id, quantity in stock_deltas.items():
        Product.objects.filter(id=product_id).update(stock=F('stock') - quantity)


def _check_order_stock(order_create_dto: OrderCreateDTO, locked_products: dict[uuid.UUID, Product]) -> None:
    for item in order_create_dto.items:
        product_id = item.product_id
        locked_product = locked_products.get(product_id)

        if locked_product is None:
            raise OrderCreationError(f"Product with id {product_id} not found.")

        if locked_product.stock < item.quantity:
            raise OrderCreationError(
                f"Not enough stock for product {locked_product.name}. Available: {locked_product.stock}"
            )


@transaction.atomic
def create_order_service(order_create_dto: OrderCreateDTO) -> Order:
    """
    Создает заказ на основе валидированных данных из OrderCreateDTO.

    Логика:
      1. Получаем и блокируем продукты.
      2. Проверяем, что для каждого продукта достаточно stock.
      3. Вычисляем дельты для обновления stock.
      4. Обновляем stock.
      5. Создаем заказ и его позиции (order items).

    :param order_create_dto: DTO для создания заказа.
    :return: созданный объект Order.
    :raises OrderCreationError: если проверка stock не проходит.
    """
    locked_products = _get_locked_products(order_create_dto=order_create_dto)

    _check_order_stock(order_create_dto=order_create_dto, locked_products=locked_products)

    stock_deltas = _calculate_stock_deltas(order_create_dto=order_create_dto)
    _update_products_stock(stock_deltas=stock_deltas)

    order = Order.objects.create()

    create_order_items_service(order=order, order_create_dto=order_create_dto, locked_products=locked_products)

    return order
