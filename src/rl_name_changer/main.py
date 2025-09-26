"""
Rocket League Name Changer - Main Application Entry Point
"""

import logging
import customtkinter as ctk

from rl_name_changer.config import APP_NAME, APP_VERSION
from rl_name_changer.logging_setup import setup_logging
from rl_name_changer.gui import SpooferGUI
from rl_name_changer.cleanup import setup_cleanup_handlers, set_proxy_controller


def main():
    """Main application entry point."""
    # Setup logging first
    logger = setup_logging()
    logger.info(f"{APP_NAME} v{APP_VERSION} starting ...")

    # Setup cleanup handlers
    setup_cleanup_handlers()

    # Setup CustomTkinter appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create and run GUI
    root = ctk.CTk()
    app = SpooferGUI(root)

    # Register proxy controller for cleanup
    set_proxy_controller(app.proxy)

    # Setup close handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    logger.info("GUI ready.")

    try:
        root.mainloop()
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        raise
    finally:
        logger.info("Application exited cleanly.")


if __name__ == "__main__":
    main()
