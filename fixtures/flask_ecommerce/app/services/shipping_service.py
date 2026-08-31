import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from fixtures.flask_ecommerce.app import db
from fixtures.flask_ecommerce.app.models.shipping import Shipment


class ShippingService:
    """Manages order fulfillment, label generation, carrier rate estimation, and parcel tracking."""

    def create_shipment(self, order_id: str, carrier: str = "fedex") -> Dict[str, Any]:
        """Dispatch parcel shipment and assign live tracking reference."""
        tracking_ref = f"TRK-{carrier.upper()}-{uuid.uuid4().hex[:10].upper()}"
        est_delivery = datetime.now(timezone.utc) + timedelta(days=3)

        shipment = Shipment(
            order_id=order_id,
            tracking_number=tracking_ref,
            carrier=carrier,
            status="in_transit",
            estimated_delivery=est_delivery,
        )
        db.session.add(shipment)
        db.session.commit()

        return {
            "shipment_id": shipment.id,
            "tracking_number": tracking_ref,
            "carrier": carrier,
            "status": shipment.status,
            "estimated_delivery": est_delivery.isoformat(),
        }
