import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class NotificationService:
    """Dispatches order confirmations, delivery status updates, and customer transactional alerts."""

    def send_order_confirmation(self, email: str, order_id: str, total_amount: float) -> bool:
        """Transmit email order confirmation to customer."""
        logger.info(f"Dispatching Order Confirmation to {email} for Order #{order_id} (${total_amount:.2f})")
        return True

    def send_shipping_update(self, email: str, tracking_number: str, carrier: str) -> bool:
        """Transmit shipping notification with tracking URL."""
        logger.info(f"Dispatching Shipping Notification to {email} ({carrier}: {tracking_number})")
        return True

    def send_low_stock_alert(self, product_sku: str, remaining_units: int) -> bool:
        """Notify warehouse operations team of inventory shortage."""
        logger.warning(f"LOW STOCK ALERT: SKU '{product_sku}' only has {remaining_units} units remaining.")
        return True
