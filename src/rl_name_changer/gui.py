"""
Rocket League Name Changer - GUI Module
"""

import time
import logging
from tkinter import messagebox
from threading import Event

import customtkinter as ctk

from .config_manager import load_config, save_config
from .system_utils import is_port_in_use, set_system_proxy, disable_system_proxy
from .proxy import ProxyController
from .config import MITMPROXY_LISTEN_HOST, MITMPROXY_LISTEN_PORT

logger = logging.getLogger(__name__)


class SpooferGUI:
    """Main GUI class for the Rocket League Name Spoofer."""

    def __init__(self, master):
        logger.info("Initializing GUI ...")
        self.master = master
        self.is_proxy_running = False
        self.auto_scan_var = ctk.BooleanVar(value=False)
        self.auto_scan_stop_event = Event()
        self.rl_process_active = False
        self.app_config = load_config()
        self.new_name_var = ctk.StringVar(value=self.app_config["last_spoof_name"])
        self.auto_scan_var.set(self.app_config.get("auto_scan_on_startup", False))

        # Initialize proxy controller
        self.proxy = ProxyController(MITMPROXY_LISTEN_HOST, MITMPROXY_LISTEN_PORT)

        self._setup_window()
        self._create_widgets()
        self._bind_events()

    def _setup_window(self):
        """Setup the main window properties."""
        logger.debug("Setting up main window ...")
        self.master.title("Rocket League Name Changer")
        self.master.geometry("500x400")
        self.master.resizable(False, False)

    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        logger.debug("Creating widgets ...")
        main_frame = ctk.CTkFrame(self.master)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Rocket League Name Changer",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(pady=(10, 20))

        # Name input section
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", padx=10, pady=(0, 20))

        ctk.CTkLabel(input_frame, text="Display Name:").pack(pady=(10, 5))
        self.new_name_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.new_name_var,
            placeholder_text="Enter your desired display name",
        )
        self.new_name_entry.pack(pady=(0, 10), padx=10, fill="x")

        # Control buttons
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=10, pady=(0, 20))

        self.toggle_button = ctk.CTkButton(
            control_frame,
            text="ACTIVATE",
            command=self.toggle_proxy_clicked,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.toggle_button.pack(pady=15)

        # Auto-scan checkbox
        self.auto_scan_checkbox = ctk.CTkCheckBox(
            control_frame,
            text="Auto-attach to Rocket League",
            variable=self.auto_scan_var,
        )
        self.auto_scan_checkbox.pack(pady=(0, 15))

        # Status section
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(fill="x", padx=10)

        ctk.CTkLabel(
            status_frame, text="Status:", font=ctk.CTkFont(weight="bold")
        ).pack(pady=(10, 5))
        self.status_label = ctk.CTkLabel(status_frame, text="Proxy: Inactive")
        self.status_label.pack(pady=(0, 10))

    def _bind_events(self):
        """Bind event handlers to widgets."""
        self.new_name_entry.bind("<KeyRelease>", self.on_name_entry_change)
        self.auto_scan_checkbox.configure(command=self.on_auto_scan_toggle)

    def on_name_entry_change(self, event):
        """Handle name entry changes and save config."""
        current_config = {
            "last_spoof_name": self.new_name_var.get(),
            "auto_scan_on_startup": self.auto_scan_var.get(),
        }
        save_config(current_config)

        # Update proxy if running
        if self.is_proxy_running:
            self.proxy.update_spoof_name(self.new_name_var.get())

        logger.debug(f"Name entry changed: {self.new_name_var.get()}")

    def toggle_proxy_clicked(self):
        """Handle proxy toggle button clicks."""
        if not self.is_proxy_running:
            self.start_proxy()
        else:
            self.stop_proxy()

    def start_proxy(self):
        """Start the proxy and system proxy configuration."""
        logger.info("Starting proxy ...")

        # Validate name
        name = self.new_name_var.get().strip()
        if not name:
            messagebox.showerror("Invalid Name", "Please enter a display name.")
            return

        # Check port with retries (for TIME_WAIT)
        for i in range(5):
            if not is_port_in_use(MITMPROXY_LISTEN_HOST, MITMPROXY_LISTEN_PORT):
                break
            logger.debug("Port still busy (TIME_WAIT), retrying in 0.5s...")
            time.sleep(0.5)
        else:
            messagebox.showerror(
                "Port Error", f"Port {MITMPROXY_LISTEN_PORT} still in use after retries"
            )
            return

        # Set system proxy
        if not set_system_proxy(MITMPROXY_LISTEN_HOST, MITMPROXY_LISTEN_PORT):
            messagebox.showerror(
                "Proxy Error",
                "Could not set system proxy. Try running as administrator.",
            )
            return

        try:
            # Start mitmproxy
            ok = self.proxy.start(name)
            if not ok:
                raise RuntimeError("Proxy failed to start (timeout waiting for ready).")

            self.is_proxy_running = True
            self.status_label.configure(text="Proxy: Active", text_color="green")
            self.toggle_button.configure(
                text="DEACTIVATE", fg_color="red", hover_color="dark red"
            )
            logger.info("Proxy started and marked active.")

        except Exception as e:
            logger.error("Start proxy failed: %s", e)
            disable_system_proxy()
            messagebox.showerror("Proxy Error", f"Failed to start proxy: {e}")

        # Disable button briefly to avoid rapid clicks
        self.toggle_button.configure(state="disabled")
        self.master.after(1000, lambda: self.toggle_button.configure(state="normal"))

    def stop_proxy(self):
        """Stop the proxy and disable system proxy."""
        logger.info("Stopping proxy ...")
        try:
            self.proxy.stop(timeout=5.0)
        finally:
            disable_system_proxy()

        self.is_proxy_running = False
        self.status_label.configure(text="Proxy: Inactive", text_color="white")
        self.toggle_button.configure(text="ACTIVATE", fg_color=None, hover_color=None)
        logger.info("Proxy stopped and system proxy disabled.")

    def on_auto_scan_toggle(self):
        """Handle auto-scan checkbox changes."""
        if self.auto_scan_var.get():
            logger.info("Auto-scan enabled.")
        else:
            logger.info("Auto-scan disabled.")

        # Save config
        current_config = {
            "last_spoof_name": self.new_name_var.get(),
            "auto_scan_on_startup": self.auto_scan_var.get(),
        }
        save_config(current_config)

    def on_closing(self):
        """Handle application closing."""
        logger.info("Closing application ...")
        try:
            if self.is_proxy_running:
                self.stop_proxy()
        finally:
            self.master.destroy()
