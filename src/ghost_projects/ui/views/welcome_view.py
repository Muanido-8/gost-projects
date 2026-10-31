from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QFileDialog, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path

class WelcomeView(QWidget):
    folder_selected = Signal(Path)

    def __init__(self):
        super().__init__()
        self.selected_path = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        # Card container
        card = QFrame()
        card.setFixedWidth(600)
        card.setObjectName("WelcomeCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Identity
        title = QLabel("GHOST PROJECTS")
        title.setObjectName("AppTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tagline = QLabel("Resurrecting the digital remains of forgotten software.")
        tagline.setObjectName("AppTagline")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Introduction
        intro = QLabel(
            "Ghost Projects is an AI-powered digital archaeology tool designed to investigate "
            "abandoned codebases. It explores forgotten architectures, reconstructs original "
            "development intentions, and generates a practical resurrection plan to bring "
            "lost software back to life."
        )
        intro.setObjectName("IntroText")
        intro.setWordWrap(True)
        intro.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Folder Selection Section
        self.select_button = QPushButton("SELECT PROJECT FOLDER")
        self.select_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_button.clicked.connect(self.on_select_folder)

        self.path_label = QLabel("No project selected")
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.path_label.setStyleSheet("color: #666666; font-size: 13px;")
        self.path_label.setWordWrap(True)

        # Action Button
        self.exorcise_button = QPushButton("EXORCISE PROJECT")
        self.exorcise_button.setObjectName("PrimaryButton")
        self.exorcise_button.setEnabled(False)
        self.exorcise_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Add to card
        card_layout.addWidget(title)
        card_layout.addWidget(tagline)
        card_layout.addSpacing(20)
        card_layout.addWidget(intro)
        card_layout.addSpacing(30)
        card_layout.addWidget(self.select_button)
        card_layout.addWidget(self.path_label)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.exorcise_button)

        layout.addWidget(card)

    def on_select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.selected_path = Path(folder)
            self.path_label.setText(f"Selected: {self.selected_path.name}\n{self.selected_path}")
            self.exorcise_button.setEnabled(True)
            self.folder_selected.emit(self.selected_path)
        else:
            # User cancelled
            pass

    def get_selected_path(self) -> Path:
        return self.selected_path