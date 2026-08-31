import logging
import time
from flask import Flask, g, request

logger = logging.getLogger(__name__)


def init_request_logger(app: Flask):
    """Attach request timing and logging hooks to Flask app."""

    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_response(response):
        duration_ms = 0
        if hasattr(g, "start_time"):
            duration_ms = int((time.time() - g.start_time) * 1000)

        # Do not log noisy static asset queries in debug console
        if not request.path.startswith("/static/"):
            logger.info(
                "%s %s -> %s (%d ms) [IP: %s]",
                request.method,
                request.path,
                response.status_code,
                duration_ms,
                request.remote_addr,
            )
        return response
