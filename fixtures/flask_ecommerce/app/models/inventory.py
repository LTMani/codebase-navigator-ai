import uuid
from datetime import datetime, timezone
from fixtures.flask_ecommerce.app import db


class Warehouse(db.Model):
    __tablename__ = "warehouses"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    location_code = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, default=10000)
    is_active = db.Column(db.Boolean, default=True)


class StockItem(db.Model):
    __tablename__ = "stock_items"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    warehouse_id = db.Column(db.String(36), db.ForeignKey("warehouses.id"), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey("products.id"), nullable=False)
    quantity_on_hand = db.Column(db.Integer, default=0, nullable=False)
    quantity_reserved = db.Column(db.Integer, default=0, nullable=False)
    reorder_threshold = db.Column(db.Integer, default=10)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    warehouse = db.relationship("Warehouse")
    product = db.relationship("Product")
