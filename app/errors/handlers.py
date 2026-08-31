import logging
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
from app.errors.exceptions import AppException

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask):
    """Register global error handlers for JSON API and web requests."""

    @app.errorhandler(AppException)
    def handle_app_exception(err: AppException):
        logger.warning("Domain exception [%s]: %s (Details: %s)", err.error_code, err.message, err.details)
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        response_data = {
            "success": False,
            "error": {
                "code": err.name.upper().replace(" ", "_"),
                "message": err.description,
            },
        }
        return jsonify(response_data), err.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_exception(err: Exception):
        logger.exception("Unhandled server exception on %s %s: %s", request.method, request.path, err)
        response_data = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
            },
        }
        return jsonify(response_data), 500
