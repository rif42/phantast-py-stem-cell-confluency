import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt

# Import our custom components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.sections.image_navigation_inspection.views.image_navigation import ImageNavigationWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.resize(1300, 850)

        self.apply_stylesheet()

        # Core Container
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        self.setup_header()
        
        self.load_views()

    def apply_stylesheet(self):
        style = """
        QMainWindow, QWidget {
            background-color: #121415;
            color: #E8EAED;
            font-family: "Inter", "Segoe UI", sans-serif;
            font-size: 13px;
        }
        
        /* HEADER */
        #AppHeader {
            background-color: #121415;
            border-bottom: 1px solid #2D3336;
        }
        """
        self.setStyleSheet(style)

    def setup_header(self):
        header = QFrame()
        header.setObjectName("AppHeader")
        header.setFixedHeight(56)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)
        
        # Left side
        logo = QLabel("🔬")
        logo.setStyleSheet("font-size: 20px; color: #00B884;")
        
        title = QLabel("Phantast Lab")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #E8EAED;")
        
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()
        
        # Right side -> Avatar
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet("background-color: #E8A317; border-radius: 16px;")
        layout.addWidget(avatar)
        
        self.main_layout.addWidget(header)

    def load_views(self):
        # Base paths for data
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../product/sections/"))
        
        # 1. Image Navigation View
        data_path_img = os.path.join(base_dir, "image-navigation-inspection/data.json")
        self.view_img = ImageNavigationWidget(data_path_img)
        self.main_layout.addWidget(self.view_img)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
