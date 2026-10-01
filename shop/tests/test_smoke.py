from app.order import Order
from app.loyalty import LoyaltyAccount, LoyaltyTier


def test_order_subtotal():
    order = Order(customer_id="c1")
    order.add_item("Widget", 10.0, 2)
    order.add_item("Gadget", 5.0, 1)
    assert order.subtotal == 25.0


def test_loyalty_account_starts_bronze():
    account = LoyaltyAccount(customer_id="c1")
    assert account.tier is LoyaltyTier.BRONZE
    assert account.points == 0
