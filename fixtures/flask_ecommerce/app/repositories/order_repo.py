from typing import List, Optional
from fixtures.flask_ecommerce.app import db
from fixtures.flask_ecommerce.app.models.schema import CartItem, Order, OrderItem, Payment


class OrderRepository:
    """Data access layer for shopping carts, orders, and payment records."""

    def get_user_cart(self, user_id: str) -> List[CartItem]:
        return CartItem.query.filter_by(user_id=user_id).all()

    def add_to_cart(self, user_id: str, product_id: str, quantity: int = 1) -> CartItem:
        existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        if existing:
            existing.quantity += quantity
            db.session.commit()
            return existing

        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(item)
        db.session.commit()
        return item

    def clear_cart(self, user_id: str):
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()

    def create_order(self, order: Order) -> Order:
        db.session.add(order)
        db.session.commit()
        return order

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        return Order.query.filter_by(id=order_id).first()

    def record_payment(self, payment: Payment) -> Payment:
        db.session.add(payment)
        db.session.commit()
        return payment
