import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt

# Import our custom components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.ui.image_navigation import ImageNavigationWidget
from src.models.image_model import ImageSessionModel
from src.controllers.image_controller import ImageNavigationController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.resize(1300, 850)

        # Core Container
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        self.setup_header()

        self.load_views()

    def setup_header(self):
        header = QFrame()
        header.setObjectName("AppHeader")
        header.setFixedHeight(56)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        # Left side
        logo = QLabel("🔬")
        logo.setObjectName("appLogo")

        title = QLabel("Phantast Lab")
        title.setObjectName("appTitle")

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()

        # Right side -> Avatar
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setObjectName("appAvatar")
        layout.addWidget(avatar)

        self.main_layout.addWidget(header)

    def load_views(self):
        # Base paths for data
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../product/sections/")
        )

        # 1. Image Navigation MVC
        self.img_model = ImageSessionModel()
        self.view_img = ImageNavigationWidget()
        self.img_controller = ImageNavigationController(self.img_model, self.view_img)

        self.main_layout.addWidget(self.view_img)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
