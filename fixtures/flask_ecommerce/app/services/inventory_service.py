from typing import Any, Dict, List, Optional
from fixtures.flask_ecommerce.app import db
from fixtures.flask_ecommerce.app.models.inventory import StockItem, Warehouse


class InventoryService:
    """Manages stock level allocation, reservations, warehouse replenishment, and backorders."""

    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        """Reserve units of product from available warehouse stock."""
        stock = StockItem.query.filter_by(product_id=product_id).first()
        if not stock:
            return False

        available = stock.quantity_on_hand - stock.quantity_reserved
        if available < quantity:
            return False

        stock.quantity_reserved += quantity
        db.session.commit()
        return True

    def release_reservation(self, product_id: str, quantity: int) -> bool:
        """Release reserved units back to available inventory."""
        stock = StockItem.query.filter_by(product_id=product_id).first()
        if not stock:
            return False

        stock.quantity_reserved = max(0, stock.quantity_reserved - quantity)
        db.session.commit()
        return True

    def replenish_stock(self, warehouse_id: str, product_id: str, quantity: int) -> StockItem:
        """Add new units to warehouse stock."""
        stock = StockItem.query.filter_by(warehouse_id=warehouse_id, product_id=product_id).first()
        if stock:
            stock.quantity_on_hand += quantity
        else:
            stock = StockItem(
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity_on_hand=quantity,
            )
            db.session.add(stock)

        db.session.commit()
        return stock
