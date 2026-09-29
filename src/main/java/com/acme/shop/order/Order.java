package com.acme.shop.order;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import java.math.BigDecimal;

/**
 * A customer order. Holds the pre-discount subtotal and the discount
 * percentage applied to it (0-100), so the final total can always be
 * recomputed from these two fields rather than persisted separately.
 */
@Entity
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String customerEmail;

    @Column(nullable = false)
    private BigDecimal subtotal;

    /** Percentage, 0-100. Zero means no discount applied. */
    @Column(nullable = false)
    private BigDecimal discountPercent = BigDecimal.ZERO;

    public Order() {
    }

    public Order(String customerEmail, BigDecimal subtotal) {
        this.customerEmail = customerEmail;
        this.subtotal = subtotal;
    }

    public Long getId() {
        return id;
    }

    public String getCustomerEmail() {
        return customerEmail;
    }

    public BigDecimal getSubtotal() {
        return subtotal;
    }

    public BigDecimal getDiscountPercent() {
        return discountPercent;
    }

    public void setDiscountPercent(BigDecimal discountPercent) {
        this.discountPercent = discountPercent;
    }

    /** Subtotal minus the discount, never negative. */
    public BigDecimal total() {
        BigDecimal discountAmount = subtotal.multiply(discountPercent)
            .divide(BigDecimal.valueOf(100));
        BigDecimal result = subtotal.subtract(discountAmount);
        return result.max(BigDecimal.ZERO);
    }
}
