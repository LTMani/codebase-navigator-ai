import uuid
from datetime import datetime, timezone
from fixtures.flask_ecommerce.app import db


class Coupon(db.Model):
    __tablename__ = "coupons"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    discount_type = db.Column(db.String(20), default="percentage")  # percentage, fixed_amount
    discount_value = db.Column(db.Float, nullable=False)
    min_order_amount = db.Column(db.Float, default=0.0)
    max_uses = db.Column(db.Integer, default=1000)
    used_count = db.Column(db.Integer, default=0)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def is_valid_for(self, order_amount: float) -> bool:
        if not self.is_active or self.used_count >= self.max_uses:
            return False
        if self.min_order_amount > order_amount:
            return False
        if self.expires_at and self.expires_at < datetime.now(timezone.utc):
            return False
        return True

    def calculate_discount(self, order_amount: float) -> float:
        if not self.is_valid_for(order_amount):
            return 0.0
        if self.discount_type == "percentage":
            return round(order_amount * (self.discount_value / 100.0), 2)
        return min(self.discount_value, order_amount)
