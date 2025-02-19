from uuid import UUID

from pydantic import BaseModel, conint


class OrderItemCreateDTO(BaseModel):
    product_id: UUID
    quantity: conint(gt=0)  # гарантируем, что количество > 0

class OrderCreateDTO(BaseModel):
    items: list[OrderItemCreateDTO]

