from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpacerItem, QSizePolicy, QFrame, QScrollArea, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
import json
import os

class ImageNavigationWidget(QWidget):
    """
    Main widget for Image Navigation & Inspection.
    Handles the central canvas, the floating toolbar, and properties panel.
    """
    
    # Signals
    image_selected = pyqtSignal(str) # Emits image ID
    mask_toggled = pyqtSignal(str, bool) # Emits image ID, visibility
    tool_activated = pyqtSignal(str) # Emits tool name

    def __init__(self, data_path: str = None):
        super().__init__()
        
        self.images = []
        self.active_image = None
        
        if data_path and os.path.exists(data_path):
            with open(data_path, 'r') as f:
                data = json.load(f)
                self.images = data.get('images', [])
                # Set active image if one is selected
                for img in self.images:
                    if img.get('selected'):
                        self.active_image = img
                        break

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # We need a layout that allows the floating toolbar to sit on top of the image canvas
        # We'll use a QVBoxLayout for the main structure, but the canvas will be a complex widget
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Panel (Folder Explorer / Pipeline Stack)
        self.left_panel = self.create_left_panel()
        main_layout.addWidget(self.left_panel)

        # 2. Central Canvas Area
        self.canvas_area = self.create_canvas_area()
        main_layout.addWidget(self.canvas_area, stretch=1)

        # 3. Right Panel (Properties)
        self.right_panel = self.create_right_panel()
        main_layout.addWidget(self.right_panel)


    def create_left_panel(self):
        panel = QFrame()
        panel.setFixedWidth(280)
        panel.setObjectName("leftPanel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header = QLabel("PIPELINE STACK")
        header.setObjectName("panelHeader")
        layout.addWidget(header)
        
        # Add Step Button
        add_step_btn = QPushButton("Add Step")
        add_step_btn.setObjectName("primaryButton")
        layout.addWidget(add_step_btn)
        
        layout.addStretch()
        
        # Run Pipeline Button
        run_btn = QPushButton("Run Pipeline")
        run_btn.setObjectName("primaryButton")
        layout.addWidget(run_btn)
        
        return panel

    def create_canvas_area(self):
        area = QFrame()
        area.setObjectName("canvasArea")
        
        # We use a layout but position the floating toolbar manually or via a nested layout
        layout = QVBoxLayout(area)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container for the image and the floating elements
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tool Bar (Floating top center)
        toolbar_container = QHBoxLayout()
        toolbar_container.setContentsMargins(0, 16, 0, 0)
        
        toolbar = QFrame()
        toolbar.setObjectName("floatingToolbar")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(12, 8, 12, 8)
        tb_layout.setSpacing(16)
        
        # Toolbar buttons (Pan, Measure, Zoom out, Zoom label, Zoom in)
        btn_pan = QPushButton("🤚") # Placeholder icon
        btn_pan.setObjectName("toolBtnActive")
        btn_measure = QPushButton("📏")
        btn_measure.setObjectName("toolBtn")
        btn_zoom_out = QPushButton("−")
        btn_zoom_out.setObjectName("toolBtn")
        lbl_zoom = QLabel("100%")
        lbl_zoom.setObjectName("toolLabel")
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setObjectName("toolBtn")

        for w in [btn_pan, btn_measure, btn_zoom_out, lbl_zoom, btn_zoom_in]:
            tb_layout.addWidget(w)
            
        toolbar_container.addStretch()
        toolbar_container.addWidget(toolbar)
        toolbar_container.addStretch()
        
        # Main Canvas Image
        self.image_label = QLabel()
        self.image_label.setObjectName("canvasImage")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.active_image:
           self.image_label.setText(f"Displaying {self.active_image.get('filename')}\nProvide zoom/pan functionality here.")
        else:
           self.image_label.setText("Select an Image from the Pipeline Stack")
        
        # Add to container
        container_layout.addLayout(toolbar_container)
        container_layout.addWidget(self.image_label, stretch=1)
        
        # Bottom controls (Mask toggle placeholder)
        if self.active_image and self.active_image.get('confluencyResult'):
            bottom_controls = QHBoxLayout()
            bottom_controls.setContentsMargins(16, 0, 16, 16)
            bottom_controls.addStretch()
            
            mask_toggle = QPushButton("Toggle Mask")
            mask_toggle.setObjectName("secondaryButton")
            mask_toggle.setCheckable(True)
            mask_toggle.setChecked(self.active_image['confluencyResult'].get('maskVisible', False))
            bottom_controls.addWidget(mask_toggle)
            container_layout.addLayout(bottom_controls)
        
        layout.addWidget(container)
        return area

    def create_right_panel(self):
        panel = QFrame()
        panel.setFixedWidth(300)
        panel.setObjectName("rightPanel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header = QLabel("PROPERTIES")
        header.setObjectName("panelHeader")
        layout.addWidget(header)
        
        if self.active_image:
            # File Info Box
            file_box = QFrame()
            file_box.setObjectName("fileBox")
            fb_layout = QVBoxLayout(file_box)
            fb_layout.setContentsMargins(12, 12, 12, 12)
            
            filename = QLabel(self.active_image.get('filename', ''))
            filename.setObjectName("filenameLabel")
            fb_layout.addWidget(filename)
            
            file_desc = QLabel("Source Input" if self.active_image.get('status') != 'processed' else "Processed Output")
            file_desc.setObjectName("fileDesc")
            fb_layout.addWidget(file_desc)
            
            layout.addWidget(file_box)
            
            # Metadata Section
            meta_label = QLabel("Image Metadata")
            meta_label.setObjectName("sectionHeader")
            layout.addWidget(meta_label)
            
            self.add_property_row(layout, "Dimensions", self.active_image.get('dimensions', ''))
            self.add_property_row(layout, "Bit Depth", self.active_image.get('bitDepth', ''))
            self.add_property_row(layout, "Channels", self.active_image.get('channels', ''))
            self.add_property_row(layout, "File Size", self.active_image.get('fileSize', ''))
            
            if self.active_image.get('confluencyResult'):
               layout.addSpacing(16)
               res_label = QLabel("Analysis Results")
               res_label.setObjectName("sectionHeader")
               layout.addWidget(res_label)
               
               confluency = self.active_image['confluencyResult'].get('percentage', 0)
               self.add_property_row(layout, "Confluency", f"{confluency}%")
               self.add_property_row(layout, "Cell Count", str(self.active_image['confluencyResult'].get('totalCells', 0)))
        else:
            # Empty State
            empty_icon = QLabel("📊") # Placeholder for empty icon
            empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_icon.setStyleSheet("font-size: 32px; color: #2D3336; margin-top: 40px;")
            layout.addWidget(empty_icon)
            
            empty_label = QLabel("No Selection\nSelect an element or import an image to view properties.")
            empty_label.setObjectName("emptyLabel")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setWordWrap(True)
            layout.addWidget(empty_label)
            
        layout.addStretch()
        return panel

    def add_property_row(self, layout, label_text, value_text):
        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 4)
        label = QLabel(label_text)
        label.setObjectName("propertyLabel")
        value = QLabel(value_text)
        value.setObjectName("propertyValue")
        value.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        row.addWidget(label)
        row.addWidget(value)
        layout.addLayout(row)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121415;
                color: #E8EAED;
                font-family: 'Inter';
            }
            #leftPanel, #rightPanel {
                background-color: #121415;
                border-left: 1px solid #2D3336;
                border-right: 1px solid #2D3336;
            }
            #canvasArea {
                background-color: #0d0f10;
            }
            #canvasImage {
                color: #9AA0A6;
                font-size: 14px;
            }
            #floatingToolbar {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                border-radius: 6px;
            }
            #toolBtn {
                background-color: transparent;
                color: #9AA0A6;
                border: none;
                font-size: 16px;
                padding: 4px;
            }
            #toolBtn:hover {
                color: #E8EAED;
            }
            #toolBtnActive {
                background-color: #2D3336;
                color: #E8EAED;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                padding: 4px;
            }
            #toolLabel {
                color: #9AA0A6;
                font-size: 12px;
                font-family: 'JetBrains Mono';
            }
            #panelHeader {
                color: #9AA0A6;
                font-size: 11px;
                font-weight: bold;
                margin-bottom: 16px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            #sectionHeader {
                color: #E8EAED;
                font-size: 13px;
                font-weight: 600;
                margin-top: 16px;
                margin-bottom: 12px;
            }
            #propertyLabel {
                color: #9AA0A6;
                font-size: 12px;
            }
            #propertyValue {
                color: #FFFFFF;
                font-family: 'JetBrains Mono';
                font-size: 12px;
            }
            #fileBox {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                border-radius: 6px;
                margin-bottom: 8px;
            }
            #filenameLabel {
                font-weight: 600;
                font-size: 13px;
                color: #FFFFFF;
            }
            #fileDesc {
                font-size: 11px;
                color: #9AA0A6;
                margin-top: 2px;
            }
            #emptyLabel {
                color: #9AA0A6;
                font-size: 12px;
                line-height: 1.4;
                margin-top: 16px;
            }
            #primaryButton {
                background-color: #00B884;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            #primaryButton:hover {
                background-color: #00C890;
            }
            #secondaryButton {
                background-color: #1E2224;
                color: #E8EAED;
                border: 1px solid #2D3336;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 12px;
            }
            #secondaryButton:checked {
                background-color: rgba(0, 184, 132, 0.15);
                color: #00B884;
                border: 1px solid #00B884;
            }
        """)
