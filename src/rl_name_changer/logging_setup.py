"""
Rocket League Name Changer - Logging Module
"""

import logging
import colorlog
from .config import LOG_FILE


def setup_logging():
    """Setup colored console and file logging."""
    # Console formatter with colors
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] [%(levelname)s]%(reset)s %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Reduce mitmproxy spam
    logging.getLogger("mitmproxy").setLevel(logging.INFO)
    logging.getLogger("mitmproxy.net.http2").setLevel(logging.INFO)
    logging.getLogger("hpack").setLevel(logging.WARNING)
    logging.getLogger("mitmproxy.net.tcp").setLevel(logging.WARNING)
    logging.getLogger("mitmproxy.addons").setLevel(logging.INFO)

    logger.debug("Colored logging initialized successfully")
    return logger
