"""Order domain model for the shop.

Discounting is not implemented yet -- see the user manual's "Order discounts"
section for the business rules to add.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LineItem:
    name: str
    unit_price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.unit_price * self.quantity


@dataclass
class Order:
    customer_id: str
    items: list[LineItem] = field(default_factory=list)

    def add_item(self, name: str, unit_price: float, quantity: int = 1) -> None:
        if unit_price < 0:
            raise ValueError("unit_price must not be negative")
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self.items.append(LineItem(name=name, unit_price=unit_price, quantity=quantity))

    @property
    def subtotal(self) -> float:
        return sum(item.subtotal for item in self.items)

    @property
    def total(self) -> float:
        # TODO: apply the customer's loyalty-tier discount here (see the user
        # manual's "Order discounts" section).
        return self.subtotal
