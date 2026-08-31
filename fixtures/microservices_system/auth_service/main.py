"""Auth Microservice for Microservices System."""

import os
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "auth_service", "status": "running"}), 200


@app.route("/verify-token", methods=["POST"])
def verify_token():
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        return jsonify({"valid": False, "error": "Missing token"}), 401
    return jsonify({"valid": True, "claims": {"user_id": "usr_9981", "role": "admin"}}), 200


if __name__ == "__main__":
    app.run(port=5001)
