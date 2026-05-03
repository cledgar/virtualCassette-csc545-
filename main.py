"""
Entry point for the Real-Time Audio FX application.
"""

from asyncio.log import logger
import logging
import sys
import tkinter as tk
from pathlib import Path

# Setup path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import application modules
import config
from app import App
from ui.main_window import MainWindow


def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def main() -> None:
    """Main entry point."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Real-Time Audio FX application")

    # Create Tkinter root
    root = tk.Tk()

    # Create application
    app = App()

    # Create main window
    window = MainWindow(root, app)

    # Setup shutdown handler
    def on_closing():
        logger.info("Application closing")
        app.shutdown()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Run application
    try:
        window.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        app.shutdown()
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        app.shutdown()


if __name__ == "__main__":
    main()

    logger.info("Application terminated")


if __name__ == "__main__":
    main()
