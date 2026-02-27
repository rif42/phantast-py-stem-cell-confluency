import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from PyQt6.QtWidgets import QApplication
from src.sections.image_navigation_inspection.views.image_navigation import ImageNavigationWidget

# Load sample data
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../product/sections/image-navigation-inspection/data.json"))

app = QApplication(sys.argv)
# Create widget with the first image selected (if any)
window = ImageNavigationWidget(data_path)
window.resize(1024, 768)
window.setWindowTitle("Image Navigation Preview")
window.show()

sys.exit(app.exec())
