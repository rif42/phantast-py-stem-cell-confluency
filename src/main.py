import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    """
    Main entry point for PhantastLab application.

    The MainWindow now contains its own MainController and UnifiedMainWidget,
    so no external MVC setup is needed.
    """
    app = QApplication(sys.argv)

    # Create main window (includes controller and unified UI)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
