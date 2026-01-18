from pydantic import BaseModel
from typing import Optional

class OrderBase(BaseModel):
    user_id: int
    product: str
    amount: int

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int

    class Config:
        from_attributes = True

