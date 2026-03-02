import sys
import os
import json
from PyQt6.QtWidgets import QApplication

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.sections.image_navigation_inspection.views.image_navigation import ImageNavigationWidget

# Setup path and load sample data
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../product/sections/image-navigation-inspection/data.json"))
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../product/sections/image-navigation-inspection/image_navigation-design.png"))

app = QApplication(sys.argv)
window = ImageNavigationWidget(data_path)
window.resize(1280, 800) # Give it a good default size for the screenshot
window.show()

# Process events to ensure the widget renders fully before grabbing
app.processEvents()

# Capture screenshot
pixmap = window.grab()
pixmap.save(output_path)

print(f"Screenshot saved to {output_path}")
sys.exit()
