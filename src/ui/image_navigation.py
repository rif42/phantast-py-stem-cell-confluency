from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpacerItem, QSizePolicy, QFrame, QScrollArea, QListWidget, QListWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor

from .image_canvas import ImageCanvas

class ImageNavigationWidget(QWidget):
    """
    Main widget for Image Navigation & Inspection.
    Handles the central canvas, the floating toolbar, and properties panel.
    """
    
    # Signals for Controller
    open_single_image_requested = pyqtSignal(str)
    open_folder_requested = pyqtSignal(str)
    file_selected = pyqtSignal(str)
    
    # Tool Signals
    mask_toggled = pyqtSignal(bool)
    tool_activated = pyqtSignal(str) 

    def __init__(self):
        super().__init__()
        
        self.mode = "EMPTY" # EMPTY, SINGLE, FOLDER
        
        self.init_ui()
        self.apply_styles()
        self.set_mode("EMPTY")

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
        
        # Header & Add Step
        header_layout = QHBoxLayout()
        header = QLabel("PIPELINE STACK")
        header.setObjectName("panelHeader")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        add_step_btn = QPushButton("Add")
        add_step_btn.setObjectName("primaryButton")
        add_step_btn.setFixedSize(60, 24)
        header_layout.addWidget(add_step_btn)
        
        layout.addLayout(header_layout)
        
        # Container for the dynamic nodes
        self.pipeline_nodes_container = QWidget()
        self.pipeline_nodes_layout = QVBoxLayout(self.pipeline_nodes_container)
        self.pipeline_nodes_layout.setContentsMargins(0, 0, 0, 0)
        self.pipeline_nodes_layout.setSpacing(12)
        
        # Input Node (Dynamic Text)
        self.input_node = QFrame()
        self.input_node.setObjectName("nodeWidget")
        in_layout = QHBoxLayout(self.input_node)
        in_layout.setContentsMargins(12, 12, 12, 12)
        in_icon = QLabel("📁")
        in_icon.setStyleSheet("font-size: 20px;")
        in_layout.addWidget(in_icon)
        
        in_text_layout = QVBoxLayout()
        self.input_node_title = QLabel("Original")
        self.input_node_title.setObjectName("filenameLabel")
        self.input_node_subtitle = QLabel("1 File")
        self.input_node_subtitle.setObjectName("fileDesc")
        in_text_layout.addWidget(self.input_node_title)
        in_text_layout.addWidget(self.input_node_subtitle)
        in_layout.addLayout(in_text_layout)
        in_layout.addStretch()
        
        in_badge = QLabel("INPUT")
        in_badge.setObjectName("badgeInput")
        in_layout.addWidget(in_badge)
        self.pipeline_nodes_layout.addWidget(self.input_node)
        
        # Down Arrow
        arrow = QLabel("↓")
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow.setStyleSheet("color: #2D3336; font-weight: bold;")
        self.pipeline_nodes_layout.addWidget(arrow)
        
        # Output Node (PHANTAST)
        self.output_node = QFrame()
        self.output_node.setObjectName("nodeWidgetOutput")
        out_layout = QHBoxLayout(self.output_node)
        out_layout.setContentsMargins(12, 12, 12, 12)
        out_icon = QLabel("📥")
        out_icon.setStyleSheet("font-size: 20px;")
        out_layout.addWidget(out_icon)
        
        out_text_layout = QVBoxLayout()
        out_title = QLabel("PHANTAST")
        out_title.setObjectName("filenameLabel")
        out_subtitle = QLabel("Sigma: 1.4 | Epsilon: 0.03")
        out_subtitle.setObjectName("fileDesc")
        out_text_layout.addWidget(out_title)
        out_text_layout.addWidget(out_subtitle)
        out_layout.addLayout(out_text_layout)
        out_layout.addStretch()
        
        out_badge = QLabel("OUTPUT")
        out_badge.setObjectName("badgeOutput")
        out_layout.addWidget(out_badge)
        self.pipeline_nodes_layout.addWidget(self.output_node)
        
        layout.addWidget(self.pipeline_nodes_container)
        layout.addStretch()
        
        # Run Pipeline Button
        self.run_btn = QPushButton("Run Pipeline")
        self.run_btn.setObjectName("primaryButton")
        self.run_btn.setFixedHeight(40)
        layout.addWidget(self.run_btn)
        
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
        
        # Wrap toolbar in a widget so we can hide/show it easily
        self.toolbar_container_widget = QWidget()
        toolbar_container_layout = QHBoxLayout(self.toolbar_container_widget)
        toolbar_container_layout.setContentsMargins(0, 16, 0, 0)
        
        toolbar = QFrame()
        toolbar.setObjectName("floatingToolbar")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(12, 8, 12, 8)
        tb_layout.setSpacing(16)
        
        # Toolbar buttons (Pan, Measure, Zoom out, Zoom label, Zoom in)
        self.btn_pan = QPushButton("🤚") # Placeholder icon
        self.btn_pan.setObjectName("toolBtn") # Default state
        self.btn_pan.setCheckable(True)
        self.btn_pan.clicked.connect(self.toggle_pan_mode)
        
        btn_measure = QPushButton("📏")
        btn_measure.setObjectName("toolBtn")
        
        btn_zoom_out = QPushButton("−")
        btn_zoom_out.setObjectName("toolBtn")
        btn_zoom_out.clicked.connect(self.action_zoom_out)
        
        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setObjectName("toolLabel")
        self.lbl_zoom.setFixedWidth(45)
        self.lbl_zoom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setObjectName("toolBtn")
        btn_zoom_in.clicked.connect(self.action_zoom_in)

        for w in [self.btn_pan, btn_measure, btn_zoom_out, self.lbl_zoom, btn_zoom_in]:
            tb_layout.addWidget(w)
            
        toolbar_container_layout.addStretch()
        toolbar_container_layout.addWidget(toolbar)
        toolbar_container_layout.addStretch()
        
        # Main Canvas Image
        self.image_canvas = ImageCanvas()
        self.image_canvas.setObjectName("canvasImage")
        self.image_canvas.zoom_changed.connect(lambda pct: self.lbl_zoom.setText(f"{pct}%"))
        
        # Center Empty State Overlay
        self.empty_overlay = QWidget()
        overlay_layout = QVBoxLayout(self.empty_overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_icon = QLabel("🖼️") # Placeholder icon
        empty_icon.setStyleSheet("font-size: 48px;")
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(empty_icon)
        
        empty_title = QLabel("Select Input Image")
        empty_title.setObjectName("sectionHeader")
        empty_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(empty_title)
        
        self.btn_open_img = QPushButton("Open an Image")
        self.btn_open_img.setObjectName("primaryButton")
        self.btn_open_img.setFixedWidth(240)
        self.btn_open_img.clicked.connect(self.action_open_image)
        overlay_layout.addWidget(self.btn_open_img, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.btn_open_folder = QPushButton("Open a Folder")
        self.btn_open_folder.setObjectName("primaryButton")
        self.btn_open_folder.setFixedWidth(240)
        self.btn_open_folder.clicked.connect(self.action_open_folder)
        overlay_layout.addWidget(self.btn_open_folder, alignment=Qt.AlignmentFlag.AlignCenter)
        
        empty_subtitle = QLabel("Supports JPG, PNG, TIFF & RAW formats up to 100MB")
        empty_subtitle.setObjectName("fileDesc")
        empty_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(empty_subtitle)
        
        # Add to container
        container_layout.addWidget(self.empty_overlay)
        container_layout.addWidget(self.toolbar_container_widget)
        container_layout.addWidget(self.image_canvas, stretch=1)
        
        # Bottom controls (Mask toggle placeholder)
        self.mask_toggle_widget = QWidget()
        bottom_controls = QHBoxLayout(self.mask_toggle_widget)
        bottom_controls.setContentsMargins(16, 0, 16, 16)
        bottom_controls.addStretch()
        
        self.btn_mask_toggle = QPushButton("Toggle Mask")
        self.btn_mask_toggle.setObjectName("secondaryButton")
        self.btn_mask_toggle.setCheckable(True)
        self.btn_mask_toggle.setChecked(False)  # Default
        # Connect to custom signal
        self.btn_mask_toggle.toggled.connect(self.mask_toggled.emit)
        bottom_controls.addWidget(self.btn_mask_toggle)
        
        # Hide it by default until a valid image with mask is loaded
        self.mask_toggle_widget.hide()
        
        container_layout.addWidget(self.mask_toggle_widget)
        
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
        
        # Folder Explorer Area (Hidden in SINGLE mode)
        self.folder_explorer_widget = QWidget()
        fe_layout = QVBoxLayout(self.folder_explorer_widget)
        fe_layout.setContentsMargins(0, 0, 0, 0)
        
        fe_header = QLabel("📁 Folder Explorer")
        fe_header.setObjectName("sectionHeader")
        fe_layout.addWidget(fe_header)
        
        self.file_list = QListWidget()
        self.file_list.setObjectName("fileList")
        self.file_list.itemClicked.connect(self.on_file_selected)
        fe_layout.addWidget(self.file_list, stretch=1)
        
        layout.addWidget(self.folder_explorer_widget, stretch=1)
        
        # Spacer for SINGLE mode
        self.spacer_widget = QWidget()
        self.spacer_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.spacer_widget)
        
        # Metadata Section
        self.metadata_widget = QWidget()
        md_layout = QVBoxLayout(self.metadata_widget)
        md_layout.setContentsMargins(0, 0, 0, 0)
        
        meta_label = QLabel("ⓘ Image Metadata")
        meta_label.setObjectName("sectionHeader")
        md_layout.addWidget(meta_label)
        
        # File Info Box
        self.file_box = QFrame()
        self.file_box.setObjectName("fileBox")
        fb_layout = QVBoxLayout(self.file_box)
        fb_layout.setContentsMargins(12, 12, 12, 12)
        
        self.filename_label = QLabel()
        self.filename_label.setObjectName("filenameLabel")
        fb_layout.addWidget(self.filename_label)
        
        self.file_desc_label = QLabel("Source Input")
        self.file_desc_label.setObjectName("fileDesc")
        fb_layout.addWidget(self.file_desc_label)
        
        md_layout.addWidget(self.file_box)
        
        self.row_dimensions = self.add_property_row(md_layout, "Dimensions", "")
        self.row_bitdepth = self.add_property_row(md_layout, "Bit Depth", "")
        self.row_channels = self.add_property_row(md_layout, "Channels", "Grayscale (1)")
        self.row_filesize = self.add_property_row(md_layout, "File Size", "")
        
        layout.addWidget(self.metadata_widget)
        
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
        return value

    def on_file_selected(self, item):
        filename = item.text()
        self.file_selected.emit(filename)

    def action_open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Input Image", "", "Images (*.png *.jpg *.jpeg *.tif *.tiff)")
        if file_path:
            self.open_single_image_requested.emit(file_path)

    def action_open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder_path:
            self.open_folder_requested.emit(folder_path)

    def set_mode(self, mode: str):
        self.mode = mode
        self._update_visibility()
        
    def _update_visibility(self):
        if self.mode == "EMPTY":
            self.left_panel.hide()
            self.right_panel.hide()
            self.empty_overlay.show()
            self.toolbar_container_widget.hide()
            self.image_canvas.hide()
        else: # SINGLE or FOLDER
            self.left_panel.show()
            self.right_panel.show()
            self.empty_overlay.hide()
            self.toolbar_container_widget.show()
            self.image_canvas.show()
            
    def update_file_list(self, files: list):
        self.file_list.clear()
        for f in files:
            self.file_list.addItem(f)
            
        if files:
            self.file_list.setCurrentRow(0)

    def update_metadata_display(self, filename: str, subtitle: str, dimensions: str, bitdepth: str, channels: str, filesize: str):
        # Left Panel Updates
        if self.mode == "SINGLE":
            self.input_node_title.setText("Original")
            self.input_node_subtitle.setText(filename)
            self.folder_explorer_widget.hide()
            self.spacer_widget.show()
        elif self.mode == "FOLDER":
            self.input_node_title.setText("Sample Data")
            self.input_node_subtitle.setText(subtitle)
            self.folder_explorer_widget.show()
            self.spacer_widget.hide()
            
        # Right Panel Metadata Updates
        self.filename_label.setText(filename)
        self.row_dimensions.setText(dimensions)
        self.row_bitdepth.setText(bitdepth)
        self.row_channels.setText(channels)
        self.row_filesize.setText(filesize)

    def load_image_to_canvas(self, filepath: str):
        self.image_canvas.load_image(filepath)
        self.update_zoom_label()

    # --- Interaction Handlers ---
    def toggle_pan_mode(self, checked):
        if checked:
            self.btn_pan.setObjectName("toolBtnActive")
        else:
            self.btn_pan.setObjectName("toolBtn")
        
        # Force stylesheet update
        self.btn_pan.style().unpolish(self.btn_pan)
        self.btn_pan.style().polish(self.btn_pan)
        
        self.image_canvas.set_pan_mode(checked)

    def action_zoom_in(self):
        self.image_canvas.zoom_in()
        self.update_zoom_label()

    def action_zoom_out(self):
        self.image_canvas.zoom_out()
        self.update_zoom_label()
        
    def update_zoom_label(self):
        pct = self.image_canvas.get_current_zoom_percentage()
        self.lbl_zoom.setText(f"{pct}%")

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
                background-color: #121415;
                border-radius: 4px;
                color: #9AA0A6;
                font-size: 12px;
                font-family: 'JetBrains Mono';
                padding: 4px 0px;
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
            #nodeWidget {
                background-color: #1E2224;
                border: 1px solid #0078D4; /* Blue for input */
                border-radius: 6px;
            }
            #nodeWidgetOutput {
                background-color: #1E2224;
                border: 1px solid #E8A317; /* Yellow for output */
                border-radius: 6px;
            }
            #badgeInput {
                background-color: #0078D4;
                color: white;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
            }
            #badgeOutput {
                background-color: #E8A317;
                color: #121415;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
            }
            #fileList {
                background-color: #121415;
                border: none;
                color: #E8EAED;
                outline: none;
            }
            #fileList::item {
                padding: 8px;
                border-bottom: 1px solid #2D3336;
            }
            #fileList::item:selected {
                background-color: #1E2224;
            }
        """)
