import uuid
from datetime import datetime, timezone
from fixtures.flask_ecommerce.app import db


class ProductReview(db.Model):
    __tablename__ = "product_reviews"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.String(36), db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    title = db.Column(db.String(128), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    is_verified_purchase = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product")
    user = db.relationship("User")
