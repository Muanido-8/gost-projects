STYLESHEET = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    color: #E0E0E0;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
}

QLabel#AppTitle {
    color: #00FFC8;
    font-size: 32px;
    font-weight: bold;
    letter-spacing: 2px;
}

QLabel#AppTagline {
    color: #888888;
    font-size: 14px;
    font-style: italic;
}

QLabel#IntroText {
    color: #B0B0B0;
    font-size: 16px;
    line-height: 1.5;
}

QPushButton {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 6px;
    color: #E0E0E0;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #252525;
    border: 1px solid #00FFC8;
    color: #00FFC8;
}

QPushButton:pressed {
    background-color: #1A1A1A;
}

QPushButton:disabled {
    color: #555555;
    background-color: #121212;
    border: 1px solid #222222;
}

QPushButton#PrimaryButton {
    background-color: #004D40;
    border: 1px solid #00FFC8;
    color: #00FFC8;
    font-weight: bold;
}

QPushButton#PrimaryButton:hover {
    background-color: #00695C;
}

QPushButton#PrimaryButton:disabled {
    background-color: #121212;
    border: 1px solid #222222;
    color: #444444;
}

QPlainTextEdit {
    background-color: #0A0A0A;
    border: 1px solid #222222;
    border-radius: 4px;
    color: #00FFC8;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    padding: 10px;
}

QFileDialog {
    color: #E0E0E0;
}
"""