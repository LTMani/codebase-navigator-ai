import uuid
from typing import Any, Dict
from fixtures.flask_ecommerce.app.models.schema import Order, OrderItem, Payment
from fixtures.flask_ecommerce.app.repositories.catalog_repo import CatalogRepository
from fixtures.flask_ecommerce.app.repositories.order_repo import OrderRepository


class CheckoutService:
    """Orchestrates checkout, inventory validation, order persistence, and payment processing."""

    def __init__(self):
        self.catalog_repo = CatalogRepository()
        self.order_repo = OrderRepository()

    def process_checkout(self, user_id: str, shipping_address: str, payment_method: str) -> Dict[str, Any]:
        """Convert active cart to confirmed Order and process payment transaction."""
        cart_items = self.order_repo.get_user_cart(user_id)
        if not cart_items:
            raise ValueError("Shopping cart is empty.")

        total_amount = 0.0
        order_items = []

        for item in cart_items:
            product = item.product
            if product.inventory_count < item.quantity:
                raise ValueError(f"Insufficient stock for product '{product.name}'. Available: {product.inventory_count}")

            item_subtotal = product.price * item.quantity
            total_amount += item_subtotal

            # Reserve inventory
            product.inventory_count -= item.quantity

            order_items.append(OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
                subtotal=item_subtotal,
            ))

        # Create Order
        order = Order(
            user_id=user_id,
            total_amount=round(total_amount, 2),
            status="paid",
            shipping_address=shipping_address,
            items=order_items,
        )
        self.order_repo.create_order(order)

        # Process Payment
        tx_ref = f"TX-{uuid.uuid4().hex[:12].upper()}"
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method=payment_method,
            status="completed",
            transaction_reference=tx_ref,
        )
        self.order_repo.record_payment(payment)

        # Clear shopping cart
        self.order_repo.clear_cart(user_id)

        return {
            "order_id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "transaction_reference": tx_ref,
            "items_count": len(order_items),
        }
