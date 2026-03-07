# Restore Image Navigation to Main Window

## Problem
The main_window.py was overwritten to show only the pipeline view. The image navigation functionality (center canvas with "Open Folder"/"Open Images" buttons, folder explorer in right sidebar, image properties) needs to be restored.

## Solution
Restore main_window.py to use ImageNavigationWidget instead of PipelineConstructionWidget.

## Changes Required

### File: src/ui/main_window.py

Replace the entire file with the version that uses ImageNavigationWidget:

```python
"""
Phantast Lab - Main Application Window
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from PyQt6.QtGui import QFont, QFontDatabase

from src.ui.image_navigation import ImageNavigationWidget
from src.controllers.image_controller import ImageNavigationController
from src.models.image_model import ImageSessionModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        self.setup_fonts()
        self.init_ui()
        self.apply_stylesheet()

    def setup_fonts(self):
        # Load Inter font if available
        font_db = QFontDatabase()
        font_path = os.path.join(os.path.dirname(__file__), "../assets/fonts/Inter-Regular.ttf")
        if os.path.exists(font_path):
            font_db.addApplicationFont(font_path)

    def init_ui(self):
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main Layout
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Header
        self.header = self.create_header()
        self.main_layout.addWidget(self.header)

        # 2. Main Content Area
        self.load_views()

    def create_header(self):
        header = QFrame()
        header.setObjectName("appHeader")
        header.setFixedHeight(48)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(16)

        # Logo / App Name
        app_name = QLabel("Phantast Lab")
        app_name.setObjectName("appName")
        layout.addWidget(app_name)

        layout.addStretch()

        # Avatar placeholder
        avatar = QLabel("👤")
        avatar.setObjectName("avatar")
        layout.addWidget(avatar)

        return header

    def load_views(self):
        # Create Image Navigation MVC
        self.img_model = ImageSessionModel()
        self.view_img = ImageNavigationWidget()
        self.img_controller = ImageNavigationController(self.img_model, self.view_img)

        self.main_layout.addWidget(self.view_img)

    def apply_stylesheet(self):
        """Apply the global dark theme stylesheet."""
        self.setStyleSheet("""
            /* === Main Window & General === */
            QMainWindow {
                background-color: #121415;
            }
            QWidget {
                background-color: #121415;
                color: #E8EAED;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 13px;
            }

            /* === Header === */
            #appHeader {
                background-color: #121415;
                border-bottom: 1px solid #2A2E33;
            }
            #appName {
                font-size: 16px;
                font-weight: 600;
                color: #E8EAED;
            }
            #avatar {
                font-size: 20px;
            }

            /* === Panels === */
            #leftPanel, #rightPanel {
                background-color: #121415;
                border: none;
            }
            #rightPanel {
                border-left: 1px solid #2A2E33;
            }
            #leftPanel {
                border-right: 1px solid #2A2E33;
            }

            #panelHeader {
                font-family: 'JetBrains Mono', monospace;
                font-size: 10px;
                color: #9AA0A6;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            /* === Node Widgets === */
            #nodeWidget {
                background-color: #1A1D21;
                border: 1px solid #2A2E33;
                border-radius: 8px;
            }
            #nodeWidgetOutput {
                background-color: #1A1D21;
                border: 1px solid #00B884;
                border-radius: 8px;
            }
            #badgeInput {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 9px;
                font-weight: bold;
            }
            #badgeOutput {
                background-color: #FF9800;
                color: black;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 9px;
                font-weight: bold;
            }
            #nodeArrow {
                color: #5F6368;
                font-size: 14px;
            }

            /* === Canvas Area === */
            #canvasArea {
                background-color: #0D0E0F;
                border: none;
            }
            #canvasImage {
                background-color: transparent;
                border: 1px solid #2A2E33;
            }

            /* === Toolbar === */
            #floatingToolbar {
                background-color: #1A1D21;
                border: 1px solid #2A2E33;
                border-radius: 8px;
            }
            #toolBtn {
                background-color: transparent;
                color: #9AA0A6;
                border: none;
                padding: 4px 8px;
                font-size: 14px;
                min-width: 32px;
                min-height: 32px;
                border-radius: 4px;
            }
            #toolBtn:hover {
                background-color: #2A2E33;
            }
            #toolBtn:checked {
                background-color: #2A2E33;
                color: #FFFFFF;
            }
            #toolLabel {
                color: #9AA0A6;
                font-size: 11px;
            }

            /* === Buttons === */
            #primaryButton {
                background-color: #00B884;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            #primaryButton:hover {
                background-color: #00D69A;
            }
            #secondaryButton {
                background-color: #2A2E33;
                color: #E8EAED;
                border: 1px solid #5F6368;
                border-radius: 6px;
                padding: 8px 16px;
            }
            #secondaryButton:checked {
                background-color: #00B884;
                border-color: #00B884;
                color: white;
            }

            /* === Typography === */
            #sectionHeader {
                font-size: 11px;
                font-weight: 600;
                color: #9AA0A6;
                text-transform: uppercase;
            }
            #sectionHeaderLarge {
                font-size: 18px;
                font-weight: 600;
                color: #E8EAED;
            }
            #filenameLabel {
                font-weight: 600;
                color: #E8EAED;
            }
            #fileDesc {
                color: #9AA0A6;
                font-size: 11px;
            }
            #largeIcon {
                font-size: 48px;
                color: #5F6368;
            }

            /* === File List === */
            #fileList {
                background-color: #1A1D21;
                border: 1px solid #2A2E33;
                border-radius: 6px;
                outline: none;
            }
            #fileList::item {
                padding: 8px;
                border-bottom: 1px solid #2A2E33;
            }
            #fileList::item:selected {
                background-color: #2A2E33;
                color: #E8EAED;
            }
            #fileList::item:hover {
                background-color: #2A2E33;
            }

            /* === Metadata Box === */
            #fileBox {
                background-color: #1A1D21;
                border: 1px solid #2A2E33;
                border-radius: 8px;
            }

            /* === Sliders === */
            QSlider::groove:horizontal {
                height: 4px;
                background: #2A2E33;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #00B884;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #00B884;
                border-radius: 2px;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

## What This Restores

1. **Center Canvas**: Shows "Open an Image" and "Open a Folder" buttons when no image loaded
2. **Right Sidebar**: 
   - Folder Explorer (when folder opened)
   - Image Metadata (when image selected)
3. **Image Selection**: User can select images from folder explorer to display in canvas
4. **All existing functionality**: Zoom, pan, mask toggle, etc.

## QA
Run `python src/main.py` and verify:
- [ ] Center canvas shows "Open an Image" and "Open a Folder" buttons
- [ ] Clicking "Open Folder" shows folder explorer in right sidebar
- [ ] Selecting image from folder shows it in canvas
- [ ] Image metadata displays in right sidebar
- [ ] Clicking "Open Image" opens single image with metadata
