"""Tests for discount calculation on Order.total based on loyalty tier."""

import pytest

from app.loyalty import LoyaltyTier
from app.order import Order


def _order_with_subtotal(tier, subtotal: float) -> Order:
    order = Order(customer_id="c1", tier=tier)
    if subtotal != 0:
        order.add_item("Item", unit_price=subtotal, quantity=1)
    return order


# --- happy path ---------------------------------------------------------


def test_bronze_tier_no_discount():
    order = _order_with_subtotal(LoyaltyTier.BRONZE, 100)
    assert order.total == 100.00


def test_silver_tier_five_percent_discount():
    order = _order_with_subtotal(LoyaltyTier.SILVER, 100)
    assert order.total == 95.00


def test_gold_tier_thirty_percent_discount():
    order = _order_with_subtotal(LoyaltyTier.GOLD, 100)
    assert order.total == 70.00


def test_tier_accepts_string_value():
    order = _order_with_subtotal("silver", 100)
    assert order.total == 95.00


def test_tier_accepts_string_name_uppercase():
    order = _order_with_subtotal("GOLD", 100)
    assert order.total == 70.00


def test_no_loyalty_account_defaults_to_bronze():
    order = Order(customer_id="c1")
    order.add_item("Item", unit_price=100, quantity=1)
    assert order.tier is LoyaltyTier.BRONZE
    assert order.total == 100.00


def test_total_rounded_to_two_decimal_places():
    order = Order(customer_id="c1", tier=LoyaltyTier.SILVER)
    order.add_item("Item", unit_price=33.333, quantity=1)
    # subtotal = 33.333, discount 5% -> 31.66635 -> rounds to 31.67
    assert order.total == round(33.333 * 0.95, 2)
    assert order.total == 31.67


# --- negative / error cases --------------------------------------------


def test_invalid_tier_value_raises_value_error():
    order = Order(customer_id="c1", tier="INVALID")
    order.add_item("Item", unit_price=100, quantity=1)
    with pytest.raises(ValueError):
        _ = order.total


def test_negative_subtotal_raises_value_error():
    order = Order(customer_id="c1", tier=LoyaltyTier.BRONZE)
    # Bypass add_item's own validation to construct a negative subtotal
    # directly via the line items list.
    from app.order import LineItem

    order.items.append(LineItem(name="Refund", unit_price=-100.0, quantity=1))
    with pytest.raises(ValueError):
        _ = order.total


# --- edge cases ----------------------------------------------------------


def test_zero_subtotal_results_in_zero_total():
    order = Order(customer_id="c1", tier=LoyaltyTier.GOLD)
    assert order.subtotal == 0
    assert order.total == 0.00
