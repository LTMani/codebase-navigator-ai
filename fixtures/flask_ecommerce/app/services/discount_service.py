from typing import Any, Dict, Optional
from fixtures.flask_ecommerce.app import db
from fixtures.flask_ecommerce.app.models.discount import Coupon


class DiscountService:
    """Validates and applies promotional codes, volume discounts, and loyalty vouchers."""

    def apply_coupon(self, code: str, order_amount: float) -> Dict[str, Any]:
        """Validate coupon code and compute discount deduction."""
        coupon = Coupon.query.filter_by(code=code.upper()).first()
        if not coupon:
            raise ValueError(f"Invalid promotional code '{code}'")

        if not coupon.is_valid_for(order_amount):
            raise ValueError(f"Promotional code '{code}' is expired or does not meet minimum order requirements.")

        discount_amount = coupon.calculate_discount(order_amount)
        final_amount = max(0.0, order_amount - discount_amount)

        coupon.used_count += 1
        db.session.commit()

        return {
            "coupon_code": coupon.code,
            "discount_amount": discount_amount,
            "original_amount": order_amount,
            "final_amount": final_amount,
        }
