"""
Main entry point for MuseGUI application
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from .ui.main_window import MainWindow


def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    log_dir = Path.home() / '.musegui' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure logging
    log_file = log_dir / 'musegui.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("MuseGUI Starting...")
    logger.info("=" * 60)


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Create Qt application
        app = QApplication(sys.argv)

        # Set application metadata
        app.setApplicationName("MuseGUI")
        app.setOrganizationName("MuseGUI")
        app.setApplicationVersion("1.0.0")

        # Enable high DPI scaling
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

        # Create and show main window
        window = MainWindow()
        window.show()

        logger.info("MuseGUI window displayed")

        # Run application
        exit_code = app.exec()

        logger.info(f"MuseGUI exiting with code {exit_code}")
        return exit_code

    except Exception as e:
        logger.exception(f"Fatal error in MuseGUI: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
