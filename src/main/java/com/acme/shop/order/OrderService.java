package com.acme.shop.order;

import java.math.BigDecimal;

/**
 * Business rules for applying a discount to an order. Kept separate from
 * the Order entity itself so the rules (caps, validation) can change
 * without touching persistence.
 */
public class OrderService {

    private static final BigDecimal MAX_DISCOUNT_PERCENT = BigDecimal.valueOf(50);

    /**
     * Applies a discount percentage to an order's total.
     *
     * Business rules:
     *  - A discount below 0% or above 50% is rejected -- 50% is the
     *    maximum a shopper can ever receive, regardless of promo code.
     *  - Applying a discount never changes the stored subtotal, only the
     *    discountPercent field, so the original price is always
     *    recoverable for receipts and refunds.
     *  - The computed total is never allowed to go negative, even if a
     *    caller bypasses this method and sets an out-of-range percent
     *    directly (Order.total() itself floors at zero as a second line
     *    of defense).
     */
    public void applyDiscount(Order order, BigDecimal percent) {
        if (percent == null || percent.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Discount percent cannot be negative");
        }
        if (percent.compareTo(MAX_DISCOUNT_PERCENT) > 0) {
            throw new IllegalArgumentException(
                "Discount percent cannot exceed " + MAX_DISCOUNT_PERCENT + "%");
        }
        order.setDiscountPercent(percent);
    }

    /** Removes any discount previously applied, restoring the full subtotal as the total. */
    public void clearDiscount(Order order) {
        order.setDiscountPercent(BigDecimal.ZERO);
    }
}
