from decimal import Decimal

import pytest

from orders.dto import OrderDTO, OrderItemDTO
from orders.models import Order
from orders.services.order import create_order_service
from products.models import Product


@pytest.fixture
def product():
    def _product(name: str, stock: int, price: str, cost: str):
        return Product.objects.create(
            name=name, stock=stock, price=Decimal(price), cost=Decimal(cost)
        )

    return _product


@pytest.mark.django_db
def test_create_order_service(product):
    product1 = product("pr1", 10, "100", "10")
    product2 = product("pr2", 10, "200", "20")
    order_dto = OrderDTO(
        items=[
            OrderItemDTO(product_id=product1.id, quantity=2),
            OrderItemDTO(product_id=product2.id, quantity=3),
        ]
    )

    result = create_order_service(order_dto=order_dto)

    assert isinstance(result, Order)
