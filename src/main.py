import sys
import os

# Append the project root to sys.path so that absolute imports work dynamically
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.styles import Styles


def main():
    app = QApplication(sys.argv)

    # Apply global stylesheet - ensures consistent styling across all widgets
    app.setStyleSheet(Styles.get_global_stylesheet())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
