"""Order domain model for the shop.

Discounting is implemented based on the customer's loyalty tier -- see the
user manual's "Order discounts" section for the business rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.loyalty import LoyaltyTier

_TIER_DISCOUNTS: dict[LoyaltyTier, float] = {
    LoyaltyTier.BRONZE: 0.0,
    LoyaltyTier.SILVER: 0.05,
    LoyaltyTier.GOLD: 0.30,
}


def _resolve_tier(tier: LoyaltyTier | str) -> LoyaltyTier:
    """Resolve a `LoyaltyTier`, accepting either an enum member or a string
    matching its value (e.g. "bronze") or name (e.g. "BRONZE")."""
    if isinstance(tier, LoyaltyTier):
        return tier
    if isinstance(tier, str):
        try:
            return LoyaltyTier(tier)
        except ValueError:
            try:
                return LoyaltyTier[tier.upper()]
            except KeyError:
                pass
    raise ValueError(f"invalid loyalty tier: {tier!r}")


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
    tier: LoyaltyTier = LoyaltyTier.BRONZE

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
        subtotal = self.subtotal
        if subtotal < 0:
            raise ValueError("subtotal must not be negative")
        discount = _TIER_DISCOUNTS[_resolve_tier(self.tier)]
        return round(subtotal * (1 - discount), 2)
