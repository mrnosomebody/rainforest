from uuid import UUID

from orders.dto import OrderCreateDTO
from orders.models import Order, OrderItem
from products.models import Product


def create_order_items_service(order: Order, order_create_dto: OrderCreateDTO,
                               locked_products: dict[UUID, Product]) -> None:
    order_items = []

    for item in order_create_dto.items:
        product = locked_products.get(item.product_id)
        order_items.append(
            OrderItem(
                order=order,
                product=product,
                quantity=item.quantity,
                price_at_purchase=product.price,
            )
        )

    OrderItem.objects.bulk_create(order_items)
