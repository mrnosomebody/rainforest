from dataclasses import dataclass
from uuid import UUID


@dataclass
class OrderItemDTO:
    product_id: UUID
    quantity: int


@dataclass
class OrderDTO:
    items: list[OrderItemDTO]
