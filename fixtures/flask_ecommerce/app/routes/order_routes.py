from flask import Blueprint, jsonify, request
from fixtures.flask_ecommerce.app.services.checkout_service import CheckoutService

order_bp = Blueprint("orders", __name__)
checkout_service = CheckoutService()


@order_bp.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    shipping_address = data.get("shipping_address")
    payment_method = data.get("payment_method", "credit_card")

    if not user_id or not shipping_address:
        return jsonify({"error": "user_id and shipping_address are required"}), 400

    try:
        result = checkout_service.process_checkout(
            user_id=user_id,
            shipping_address=shipping_address,
            payment_method=payment_method,
        )
        return jsonify({"success": True, "order": result}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
