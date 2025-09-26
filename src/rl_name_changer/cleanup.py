"""
Rocket League Name Changer - Cleanup and Exception Handling Module
"""

import sys
import logging
import atexit
import signal
from tkinter import messagebox

from .system_utils import disable_system_proxy

logger = logging.getLogger(__name__)

# Global proxy controller reference
_proxy_controller = None


def set_proxy_controller(proxy_controller):
    """Set the global proxy controller reference for cleanup."""
    global _proxy_controller
    _proxy_controller = proxy_controller


def cleanup_global():
    """Global cleanup function - stops proxy and disables system proxy."""
    logger.info("Global cleanup: stopping proxy and disabling system proxy.")
    try:
        if _proxy_controller and _proxy_controller.is_running():
            _proxy_controller.stop(timeout=5.0)
    except Exception as e:
        logger.error(f"Error stopping proxy during cleanup: {e}")
    finally:
        try:
            disable_system_proxy()
        except Exception as e:
            logger.error(f"Error disabling system proxy during cleanup: {e}")


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler that triggers cleanup."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical(
        "Unhandled Exception", exc_info=(exc_type, exc_value, exc_traceback)
    )

    try:
        cleanup_global()
    except Exception as e:
        logger.error("Cleanup after crash failed: %s", e)

    messagebox.showerror(
        "Application Error",
        f"An unexpected error occurred:\n\n{exc_value}\n\n"
        f"Details have been written to the log file.\n"
        f"Please restart the application. If the problem persists, share the log file.",
    )


def _signal_handler(signum, frame):
    """Handle signals (Ctrl+C, SIGTERM) and cleanup."""
    logger.warning("Signal %s received: initiating cleanup.", signum)
    cleanup_global()
    sys.exit(0)


def setup_cleanup_handlers():
    """Setup all cleanup handlers (exception, signals, atexit)."""
    # Exception handler
    sys.excepthook = handle_exception

    # Atexit handler
    atexit.register(cleanup_global)

    # Signal handlers
    signal.signal(signal.SIGINT, _signal_handler)
    try:
        signal.signal(signal.SIGTERM, _signal_handler)
    except Exception:
        # SIGTERM might not be available in all Windows environments
        pass

    logger.debug("Cleanup handlers registered successfully.")
