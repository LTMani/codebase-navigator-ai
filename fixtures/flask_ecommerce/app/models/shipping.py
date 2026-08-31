import uuid
from datetime import datetime, timezone
from fixtures.flask_ecommerce.app import db


class Shipment(db.Model):
    __tablename__ = "shipments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey("orders.id"), nullable=False)
    tracking_number = db.Column(db.String(100), unique=True, nullable=False)
    carrier = db.Column(db.String(50), nullable=False)  # fedex, ups, dhl, usps
    status = db.Column(db.String(50), default="label_created")  # label_created, in_transit, out_for_delivery, delivered
    estimated_delivery = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    order = db.relationship("Order")
