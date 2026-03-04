import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
)
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    """Main application window with dark theme header and content area."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.resize(1300, 850)

        self.apply_stylesheet()

        # Core Container
        self.main_container = QWidget()
        self.main_container.setObjectName("mainContainer")
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        self.setup_header()
        self.setup_content()

    def apply_stylesheet(self):
        """Apply dark theme stylesheet."""
        style = """
        QMainWindow, QWidget#mainContainer {
            background-color: #121415;
            color: #E8EAED;
            font-family: "Inter", "Segoe UI", sans-serif;
            font-size: 13px;
        }
        
        /* HEADER */
        QFrame#AppHeader {
            background-color: #121415;
            border-bottom: 1px solid #2D3336;
        }
        
        /* LOGO */
        QLabel#logoLabel {
            font-size: 20px;
            color: #00B884;
        }
        
        /* TITLE */
        QLabel#titleLabel {
            font-size: 15px;
            font-weight: bold;
            color: #E8EAED;
        }
        
        /* AVATAR */
        QLabel#avatarLabel {
            background-color: #E8A317;
            border-radius: 16px;
        }
        
        /* CONTENT PLACEHOLDER */
        QLabel#placeholderLabel {
            color: #9AA0A6;
            font-size: 14px;
        }
        """
        self.setStyleSheet(style)

    def setup_header(self):
        """Create the header bar with logo, title, and avatar."""
        header = QFrame()
        header.setObjectName("AppHeader")
        header.setFixedHeight(56)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        # Left side: Logo
        logo = QLabel("🔬")
        logo.setObjectName("logoLabel")

        # Title
        title = QLabel("Phantast Lab")
        title.setObjectName("titleLabel")

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()

        # Right side: Avatar placeholder
        avatar = QLabel()
        avatar.setObjectName("avatarLabel")
        avatar.setFixedSize(32, 32)
        layout.addWidget(avatar)

        self.main_layout.addWidget(header)

    def setup_content(self):
        """Create the content area (placeholder for now)."""
        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Placeholder text
        placeholder = QLabel("Content Area - Phase 2 implementation")
        placeholder.setObjectName("placeholderLabel")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(placeholder)
        self.main_layout.addWidget(content, 1)  # Stretch to fill remaining space


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
