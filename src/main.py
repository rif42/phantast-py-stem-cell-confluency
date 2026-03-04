import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.models.image_model import ImageSessionModel
from src.controllers.image_controller import ImageNavigationController


def main():
    app = QApplication(sys.argv)

    # Create main window
    window = MainWindow()

    # Setup MVC for image navigation
    model = ImageSessionModel()
    controller = ImageNavigationController(model, window.image_nav_widget)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
