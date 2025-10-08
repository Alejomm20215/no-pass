"""Logging configuration"""

import logging
import sys
from pathlib import Path

from app.config.settings import Settings


def setup_logging(settings: Settings) -> None:
    """Setup application logging"""

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler for errors and warnings
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.WARNING)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Disable noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("pikepdf").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger for a specific module"""
    return logging.getLogger(f"app.{name}")
