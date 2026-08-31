from flask import Blueprint, jsonify, request
from fixtures.flask_ecommerce.app.repositories.order_repo import OrderRepository

cart_bp = Blueprint("cart", __name__)
order_repo = OrderRepository()


@cart_bp.route("/<user_id>", methods=["GET"])
def get_cart(user_id: str):
    items = order_repo.get_user_cart(user_id)
    return jsonify({
        "user_id": user_id,
        "items": [
            {
                "id": i.id,
                "product_id": i.product_id,
                "product_name": i.product.name if i.product else None,
                "quantity": i.quantity,
                "price": i.product.price if i.product else 0.0,
            }
            for i in items
        ]
    }), 200


@cart_bp.route("/<user_id>/add", methods=["POST"])
def add_to_cart(user_id: str):
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    item = order_repo.add_to_cart(user_id, product_id, quantity)
    return jsonify({"success": True, "cart_item_id": item.id}), 201
