"""
Rocket League Name Changer - System Utilities Module
"""

import socket
import subprocess
import winreg
import platform
import re
import logging

logger = logging.getLogger(__name__)


def is_port_in_use(host, port):
    """Check if a port is already in use."""
    logger.debug(f"Checking port {port} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            logger.debug(f"Port {port} is free.")
            return False
        except OSError:
            logger.warning(f"Port {port} is already in use.")
            return True
        except Exception as e:
            logger.error(f"Error checking port {port}: {e}")
            return True


def set_system_proxy(host, port):
    """Set Windows system proxy settings."""
    logger.info(f"Setting system proxy to {host}:{port}")
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0,
            winreg.KEY_WRITE,
        )
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"{host}:{port}")
        winreg.SetValueEx(
            key,
            "ProxyOverride",
            0,
            winreg.REG_SZ,
            "<local>;*.epicgames.com;*.psyonix.com;*.live.psynet.gg",
        )
        winreg.CloseKey(key)
        logger.info("System proxy set successfully.")
        return True
    except PermissionError:
        logger.error("Permission denied while setting proxy. Run as administrator.")
        return False
    except Exception as e:
        logger.error(f"Failed to set proxy: {e}")
        return False


def disable_system_proxy():
    """Disable Windows system proxy settings."""
    logger.info("Disabling system proxy ...")
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0,
            winreg.KEY_WRITE,
        )
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        for val_name in ["ProxyServer", "ProxyOverride"]:
            try:
                winreg.DeleteValue(key, val_name)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        logger.info("System proxy disabled.")
        return True
    except Exception as e:
        logger.error(f"Failed to disable proxy: {e}")
        return False


def is_process_running(process_name):
    """Check if a process is currently running (Windows only)."""
    logger.debug(f"Checking if process '{process_name}' is running ...")
    if platform.system() != "Windows":
        logger.warning("Process detection only implemented for Windows.")
        return False
    try:
        cmd = ["tasklist", "/FO", "CSV", "/NH", "/FI", f"IMAGENAME eq {process_name}"]
        output = subprocess.check_output(
            cmd, creationflags=subprocess.CREATE_NO_WINDOW
        ).decode("utf-8")
        return (
            re.search(rf'"{re.escape(process_name)}"', output, re.IGNORECASE)
            is not None
        )
    except Exception as e:
        logger.error(f"Process check failed: {e}")
        return False
