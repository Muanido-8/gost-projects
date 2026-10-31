import logging
from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout, 
    QLabel, QFrame, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QThread, Slot

from ghost_projects.ui.views.welcome_view import WelcomeView
from ghost_projects.ui.views.results_view import ResultsView
from ghost_projects.ui.worker import InvestigationWorker
from ghost_projects.ui.styles.dark_theme import STYLESHEET

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GHOST PROJECTS")
        self.setMinimumSize(800, 600)
        
        # Apply Global Styles
        self.setStyleSheet(STYLESHEET)
        
        self.init_ui()
        
        # Threading references
        self.worker_thread = None
        self.worker = None

    def init_ui(self):
        # Central Widget and Stack
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        
        # Views
        self.welcome_view = WelcomeView()
        self.results_view = ResultsView()
        
        self.stack.addWidget(self.welcome_view)
        self.stack.addWidget(self.results_view)
        
        self.main_layout.addWidget(self.stack)

        # Loading Overlay
        self.loading_overlay = QFrame(self)
        self.loading_overlay.setFixedSize(self.size())
        self.loading_overlay.setStyleSheet("background-color: rgba(18, 18, 18, 200);")
        self.loading_overlay.hide()
        
        self.overlay_layout = QVBoxLayout(self.loading_overlay)
        self.overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_label = QLabel("Awakening...")
        self.status_label.setObjectName("IntroText")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; color: #00FFC8;")
        self.overlay_layout.addWidget(self.status_label)

        # Connections
        self.welcome_view.exorcise_button.clicked.connect(self.start_investigation)
        self.results_view.back_requested.connect(self.show_welcome)

    def show_welcome(self):
        self.stack.setCurrentWidget(self.welcome_view)
        self.loading_overlay.hide()

    def start_investigation(self):
        project_path = self.welcome_view.get_selected_path()
        if not project_path:
            return

        # UI State: Loading
        self.welcome_view.exorcise_button.setEnabled(False)
        self.welcome_view.select_button.setEnabled(False)
        self.show_loading_overlay()

        # Setup Worker and Thread
        self.worker_thread = QThread()
        self.worker = InvestigationWorker(project_path)
        self.worker.moveToThread(self.worker_thread)

        # Connect Signals
        self.worker_thread.started.connect(self.worker.run)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.on_investigation_finished)
        self.worker.error.connect(self.on_investigation_error)
        
        # Cleanup
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def show_loading_overlay(self):
        self.loading_overlay.setFixedSize(self.size())
        self.loading_overlay.show()
        self.loading_overlay.raise_()

    def update_status(self, message: str):
        self.status_label.setText(message)

    @Slot(str)
    def on_investigation_finished(self, result_text: str):
        self.loading_overlay.hide()
        self.welcome_view.exorcise_button.setEnabled(True)
        self.welcome_view.select_button.setEnabled(True)
        
        self.results_view.set_results(result_text)
        self.stack.setCurrentWidget(self.results_view)

    @Slot(str)
    def on_investigation_error(self, error_message: str):
        self.loading_overlay.hide()
        self.welcome_view.exorcise_button.setEnabled(True)
        self.welcome_view.select_button.setEnabled(True)
        
        self.results_view.set_error(error_message)
        self.stack.setCurrentWidget(self.results_view)

    def resizeEvent(self, event):
        self.loading_overlay.setFixedSize(self.size())
        super().resizeEvent(event)