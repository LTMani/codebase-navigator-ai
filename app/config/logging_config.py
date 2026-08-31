import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def configure_logging(app_name: str = "codebase_navigator", log_level: str = "INFO", log_file: Optional[str] = None):
    """Configure structured application logging with console and rotating file output."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to prevent duplication
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    log_format = logging.Formatter(
        fmt="[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # File Handler (if path specified)
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                filename=str(log_path),
                maxBytes=10 * 1024 * 1024,  # 10 MB per file
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(log_format)
            root_logger.addHandler(file_handler)
        except Exception as err:
            sys.stderr.write(f"Failed to initialize rotating file logger at {log_file}: {err}\n")

    # Mute noisy third-party loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger = logging.getLogger(app_name)
    logger.info("Logging configured at level %s", log_level)
    return logger
