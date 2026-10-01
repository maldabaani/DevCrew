"""Loyalty program domain model.

Bonus-point calculation and tier upgrades are not implemented yet -- see the
user manual's "Loyalty bonus" section for the business rules to add.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LoyaltyTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


@dataclass
class LoyaltyAccount:
    customer_id: str
    tier: LoyaltyTier = LoyaltyTier.BRONZE
    points: int = 0

    def record_purchase(self, amount: float) -> None:
        """Award points for a purchase and upgrade the tier if a threshold is
        crossed. See the user manual's "Loyalty bonus" section for the exact
        point multipliers and tier thresholds -- not implemented yet."""
        if amount < 0:
            raise ValueError("amount must not be negative")
        # TODO: award bonus points based on tier and amount, then upgrade the
        # tier if a points threshold is crossed (see the manual).
