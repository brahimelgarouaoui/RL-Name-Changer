"""
Rocket League Name Changer - Configuration and Constants Module
"""

import os
import sys

# --- App Info ---
APP_NAME = "RLNameChanger"
APP_VERSION = "1.0.0"

# --- APP_DIR setup ---
if sys.platform == "win32":
    APP_DIR = os.path.join(os.getenv("APPDATA"), APP_NAME)
elif sys.platform == "darwin":
    APP_DIR = os.path.join(
        os.path.expanduser("~"), "Library", "Application Support", APP_NAME
    )
else:
    APP_DIR = os.path.join(os.path.expanduser("~"), ".config", APP_NAME)

os.makedirs(APP_DIR, exist_ok=True)

# --- Configuration ---
MITMPROXY_LISTEN_HOST = "127.0.0.1"
MITMPROXY_LISTEN_PORT = 8080
ROCKET_LEAGUE_PROCESS_NAME = "RocketLeague.exe"
SCAN_INTERVAL_SECONDS = 0.5
MAX_NAME_LENGTH = 32

CONFIG_FILE_NAME = "config.json"
CONFIG_FILE_PATH = os.path.join(APP_DIR, CONFIG_FILE_NAME)
LOG_FILE = os.path.join(APP_DIR, "mitmproxy_app_log.txt")

DEFAULT_CONFIG = {
    "last_spoof_name": "RL Name Changer",
    "auto_scan_on_startup": False,
}


# --- Path Helper for PyInstaller ---
def get_asset_path(relative_path):
    """Get the absolute path to a resource file."""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
