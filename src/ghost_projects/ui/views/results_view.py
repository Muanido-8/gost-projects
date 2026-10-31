from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QPlainTextEdit
from PySide6.QtCore import Qt, Signal

class ResultsView(QWidget):
    back_requested = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Header
        self.header = QLabel("INVESTIGATION RESULTS")
        self.header.setObjectName("AppTitle")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.header)

        # Results Area
        self.results_area = QPlainTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setPlaceholderText("No results to display...")
        layout.addWidget(self.results_area)

        # Back Button
        self.back_button = QPushButton("RETURN TO WELCOME")
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.clicked.connect(self.on_back_clicked)
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_results(self, text: str):
        self.header.setText("INVESTIGATION RESULTS")
        self.results_area.setPlainText(text)

    def set_error(self, error_message: str):
        self.header.setText("INVESTIGATION FAILED")
        self.results_area.setPlainText(f"An error occurred during the investigation:\n\n{error_message}")

    def on_back_clicked(self):
        self.back_requested.emit()