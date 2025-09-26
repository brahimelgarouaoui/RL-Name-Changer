"""
Rocket League Name Changer - Configuration Management Module
"""

import json
import os
import logging
from .config import CONFIG_FILE_PATH, DEFAULT_CONFIG

logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from JSON file or return defaults."""
    logger.debug("Loading config.json ...")
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                logger.info("Config loaded successfully.")
                return {**DEFAULT_CONFIG, **config}
        except json.JSONDecodeError as e:
            logger.error(f"Config file corrupted: {e}. Using defaults.")
            return DEFAULT_CONFIG
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}. Using defaults.")
            return DEFAULT_CONFIG
    else:
        logger.warning("Config file not found. Using defaults.")
        return DEFAULT_CONFIG


def save_config(config):
    """Save configuration to JSON file."""
    logger.debug("Saving config.json ...")
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logger.info("Config saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
