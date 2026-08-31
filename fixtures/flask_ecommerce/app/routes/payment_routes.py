from flask import Blueprint, jsonify, request
from fixtures.flask_ecommerce.app.models.schema import Payment

payment_bp = Blueprint("payments", __name__)


@payment_bp.route("/<transaction_ref>", methods=["GET"])
def get_payment_status(transaction_ref: str):
    payment = Payment.query.filter_by(transaction_reference=transaction_ref).first()
    if not payment:
        return jsonify({"error": "Payment transaction not found"}), 404

    return jsonify({
        "transaction_reference": payment.transaction_reference,
        "amount": payment.amount,
        "status": payment.status,
        "payment_method": payment.payment_method,
    }), 200
