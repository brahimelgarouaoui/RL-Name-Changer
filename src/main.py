#!/usr/bin/env python3
"""
RL Name Changer - Main Entry Point
Minimalistic GUI tool for changing Rocket League display names via proxy interception.
"""

import sys
import os


def setup_paths():
    """Setup Python paths for both development and PyInstaller frozen environments."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        bundle_dir = sys._MEIPASS
        src_path = os.path.join(bundle_dir, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
    else:
        # Running in development
        project_root = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(project_root, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)


def main():
    """Main entry point."""
    try:
        setup_paths()

        # Import and run the application
        from rl_name_changer import run_app

        run_app()

    except ImportError as e:
        import traceback

        print(f"Import Error: {e}")
        print(f"Python path: {sys.path}")
        traceback.print_exc()

        # Keep console open for debugging
        if getattr(sys, "frozen", False):
            input("Press Enter to exit...")
        sys.exit(1)

    except Exception as e:
        import traceback

        print(f"Unexpected error: {e}")
        traceback.print_exc()

        # Keep console open for debugging
        if getattr(sys, "frozen", False):
            input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
