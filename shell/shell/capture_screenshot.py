import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer
from src.shell.main_window import MainWindow

def capture():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    def grab_and_save():
        pixmap = window.grab()
        
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../product/shell"))
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "shell_integration.png")
        
        pixmap.save(out_path, "PNG")
        print(f"Screenshot saved to {out_path}")
        app.quit()

    QTimer.singleShot(500, grab_and_save)
    sys.exit(app.exec())

if __name__ == "__main__":
    capture()
