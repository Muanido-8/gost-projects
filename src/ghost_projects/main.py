import sys
import logging
from PySide6.QtWidgets import QApplication
from ghost_projects.ui.main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ghost_projects")

def main():
    """
    Main entry point for the Ghost Projects Desktop Application.
    """
    logger.info("Starting Ghost Projects Desktop Interface...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Ghost Projects")
    app.setOrganizationName("Ghost Projects")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("A critical error occurred during application startup")
        sys.exit(1)