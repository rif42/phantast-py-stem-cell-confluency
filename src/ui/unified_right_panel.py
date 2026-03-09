"""Unified Right Panel - Dynamic switching between image metadata and node properties."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QStackedWidget,
    QDoubleSpinBox,
    QSpinBox,
    QSizePolicy,
    QListWidget,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal


class UnifiedRightPanel(QFrame):
    """Right panel that switches between image metadata and node properties."""

    panel_changed = pyqtSignal(str)  # 'metadata' or 'properties'
    node_param_changed = pyqtSignal(str, str, object)  # node_id, param_name, value
    file_selected = pyqtSignal(str)  # file_path
    refresh_requested = pyqtSignal()  # Request to refresh folder

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMinimumWidth(280)
        self.setObjectName("rightPanel")

        self.current_node_id = None
        self.current_node_params = {}
        self.current_files = []  # Store current file list for refresh
        self._param_widgets = {}  # Map param_name -> widget for validation feedback

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create stacked widget for page switching
        self.stack = QStackedWidget(parent=self)

        # Page 0: Image Metadata Panel
        self.metadata_page = self._create_metadata_page()
        self.stack.addWidget(self.metadata_page)

        # Page 1: Node Properties Panel
        self.properties_page = self._create_properties_page()
        self.stack.addWidget(self.properties_page)

        layout.addWidget(self.stack)

        # Show metadata by default
        self.show_metadata()

    def _create_metadata_page(self):
        """Create the image metadata panel (Page 0)."""
        page = QFrame(parent=self)
        page.setObjectName("metadataPage")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # Header
        header = QLabel("PROPERTIES", parent=page)
        header.setObjectName("panelHeader")
        header.setStyleSheet("""
            color: #9AA0A6;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(header)

        layout.addSpacing(16)

        # Folder Explorer Section
        self.folder_header_widget = QWidget(parent=page)
        self.folder_header_widget.setObjectName("folderHeaderWidget")
        folder_header = QHBoxLayout(self.folder_header_widget)
        folder_header.setContentsMargins(0, 0, 0, 0)
        folder_header.setSpacing(8)

        folder_label = QLabel("📁 Folder Explorer", parent=self.folder_header_widget)
        folder_label.setObjectName("sectionHeader")
        folder_label.setStyleSheet(
            "color: #E8EAED; font-size: 14px; font-weight: bold;"
        )
        folder_header.addWidget(folder_label)

        folder_header.addStretch()

        self.refresh_btn = QPushButton("↻", parent=self.folder_header_widget)
        self.refresh_btn.setObjectName("refreshBtn")
        self.refresh_btn.setFixedSize(24, 24)
        self.refresh_btn.setToolTip("Refresh folder")
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        self.refresh_btn.setStyleSheet("""
            #refreshBtn {
                background-color: #2D3336;
                border: 1px solid #3D4448;
                border-radius: 4px;
                color: #9AA0A6;
                font-size: 12px;
            }
            #refreshBtn:hover {
                background-color: #3D4448;
                color: #E8EAED;
            }
        """)
        folder_header.addWidget(self.refresh_btn)

        layout.addWidget(self.folder_header_widget)

        layout.addSpacing(8)

        # File List
        self.file_list = QListWidget(parent=page)
        self.file_list.setObjectName("fileList")
        self.file_list.setUniformItemSizes(True)  # Performance optimization
        self.file_list.setLayoutMode(QListWidget.LayoutMode.Batched)
        self.file_list.setBatchSize(100)
        self.file_list.itemDoubleClicked.connect(self._on_file_double_clicked)
        layout.addWidget(self.file_list, stretch=1)

        # Empty state label (hidden by default)
        self.empty_label = QLabel("No images found", parent=page)
        self.empty_label.setObjectName("emptyLabel")
        self.empty_label.setStyleSheet(
            "color: #9AA0A6; font-size: 13px; padding: 20px;"
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.hide()
        layout.addWidget(self.empty_label)

        layout.addSpacing(16)

        # Metadata Section
        meta_label = QLabel("ⓘ Image Metadata", parent=page)
        meta_label.setObjectName("sectionHeader")
        meta_label.setStyleSheet("color: #E8EAED; font-size: 14px; font-weight: bold;")
        layout.addWidget(meta_label)

        layout.addSpacing(16)

        # File Info Box
        self.file_box = QFrame(parent=page)
        self.file_box.setObjectName("fileBox")
        self.file_box.setStyleSheet("""
            #fileBox {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                border-radius: 8px;
            }
        """)
        fb_layout = QVBoxLayout(self.file_box)
        fb_layout.setContentsMargins(12, 12, 12, 12)

        self.filename_label = QLabel("No image loaded", parent=self.file_box)
        self.filename_label.setObjectName("filenameLabel")
        self.filename_label.setStyleSheet(
            "color: #E8EAED; font-size: 13px; font-weight: 600;"
        )
        fb_layout.addWidget(self.filename_label)

        self.file_desc_label = QLabel("Source Input", parent=self.file_box)
        self.file_desc_label.setObjectName("fileDesc")
        self.file_desc_label.setStyleSheet("color: #9AA0A6; font-size: 11px;")
        fb_layout.addWidget(self.file_desc_label)

        layout.addWidget(self.file_box)

        layout.addSpacing(16)

        # Metadata rows
        self.row_dimensions = self._add_property_row(layout, "Dimensions", "-", page)
        self.row_bitdepth = self._add_property_row(layout, "Bit Depth", "-", page)
        self.row_channels = self._add_property_row(layout, "Channels", "-", page)
        self.row_filesize = self._add_property_row(layout, "File Size", "-", page)

        layout.addStretch()

        return page

    def _create_properties_page(self):
        """Create the node properties panel (Page 1)."""
        page = QFrame(parent=self)
        page.setObjectName("propertiesPage")

        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll_area = QScrollArea(parent=page)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")

        scroll_content = QWidget(parent=scroll_area)
        scroll_content.setStyleSheet("background-color: transparent;")

        self.properties_layout = QVBoxLayout(scroll_content)
        self.properties_layout.setContentsMargins(16, 16, 16, 16)

        # Header (will be updated dynamically)
        self.prop_header = QLabel("PROPERTIES", parent=scroll_content)
        self.prop_header.setObjectName("panelHeader")
        self.prop_header.setStyleSheet("""
            color: #9AA0A6;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        self.properties_layout.addWidget(self.prop_header)

        self.properties_layout.addSpacing(16)

        # Title container
        self.title_container = QWidget(parent=scroll_content)
        title_layout = QHBoxLayout(self.title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(1)

        self.node_title_label = QLabel("No node selected", parent=self.title_container)
        self.node_title_label.setObjectName("sectionHeader")
        self.node_title_label.setStyleSheet(
            "color: #E8EAED; font-size: 14px; font-weight: bold;"
        )
        title_layout.addWidget(self.node_title_label)
        title_layout.addStretch()

        self.properties_layout.addWidget(self.title_container)
        self.properties_layout.addSpacing(24)

        # Content area for parameters
        self.params_container = QWidget(parent=scroll_content)
        self.params_layout = QVBoxLayout(self.params_container)
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        self.params_layout.setSpacing(16)

        self.properties_layout.addWidget(self.params_container)
        self.properties_layout.addSpacing(8)

        self.properties_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        return page

    def _add_property_row(self, layout, label_text, value_text, parent):
        """Add a metadata property row."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 8, 0, 8)

        label = QLabel(label_text, parent=parent)
        label.setObjectName("propertyLabel")
        label.setStyleSheet("color: #9AA0A6; font-size: 13px;")

        value = QLabel(value_text, parent=parent)
        value.setObjectName("propertyValue")
        value.setStyleSheet("color: #E8EAED; font-size: 13px;")
        value.setAlignment(Qt.AlignmentFlag.AlignRight)

        row.addWidget(label)
        row.addWidget(value)
        layout.addLayout(row)

        return value

    def show_metadata(self, image_data=None):
        """Switch to metadata page and optionally update data.

        Args:
            image_data: Optional dict with keys:
                - filename: str
                - subtitle: str
                - dimensions: str
                - bitdepth: str
                - channels: str
                - filesize: str
        """
        if image_data:
            self._update_metadata_display(image_data)

        self.stack.setCurrentIndex(0)
        self.current_node_id = None
        self.panel_changed.emit("metadata")

    def _update_metadata_display(self, data):
        """Update metadata display with image data."""
        self.filename_label.setText(data.get("filename", "Unknown"))
        self.file_desc_label.setText(data.get("subtitle", "Source Input"))
        self.row_dimensions.setText(data.get("dimensions", "-"))
        self.row_bitdepth.setText(data.get("bitdepth", "-"))
        self.row_channels.setText(data.get("channels", "-"))
        self.row_filesize.setText(data.get("filesize", "-"))

    def show_properties(self, node_data, available_nodes=None):
        """Switch to properties page and show node parameters.

        Args:
            node_data: Dict with node info:
                - id: str
                - name: str
                - type: str
                - description: str
                - parameters: dict of current param values
            available_nodes: List of available node definitions for parameter schema
        """
        self.current_node_id = node_data.get("id")
        self.current_node_params = node_data.get("parameters", {})

        # Update title
        self.node_title_label.setText(node_data.get("name", "Node Properties"))

        # Clear previous params
        self._clear_params_layout()

        # Add description if available
        description = node_data.get("description", "")
        if description:
            desc_label = QLabel(description, parent=self.params_container)
            desc_label.setStyleSheet("color: #9AA0A6; font-size: 12px;")
            desc_label.setWordWrap(True)
            self.params_layout.addWidget(desc_label)

        # Find step definition for parameter schema
        node_type = node_data.get("type", "")
        step_def = None
        if available_nodes:
            step_def = next(
                (n for n in available_nodes if n.get("type") == node_type), None
            )

        # Generate parameter widgets
        if step_def and step_def.get("parameters"):
            for param in step_def["parameters"]:
                self._add_parameter_widget(param)
        elif self.current_node_params:
            # Fallback: show current params without schema
            for param_name, param_value in self.current_node_params.items():
                self._add_simple_param_widget(param_name, param_value)

        self.stack.setCurrentIndex(1)
        self.panel_changed.emit("properties")

    def _clear_params_layout(self):
        """Clear all widgets from params layout."""
        self._param_widgets.clear()
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _add_parameter_widget(self, param_def):
        """Add a parameter widget based on parameter definition."""
        param_name = param_def.get("name", "")
        param_type = param_def.get("type", "float")
        param_default = param_def.get("default", 0)
        param_min = param_def.get("min")
        param_max = param_def.get("max")
        param_step = param_def.get("step", 1)
        param_desc = param_def.get("description", "")

        # Get current value or use default
        current_value = self.current_node_params.get(param_name, param_default)

        # Create container
        container = QFrame(parent=self.params_container)
        container.setObjectName(f"param_container_{param_name}")
        container.setStyleSheet("margin-bottom: 16px;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Parameter name label with validation status
        name_label = QLabel(param_name.replace("_", " ").title(), parent=container)
        name_label.setObjectName(f"param_label_{param_name}")
        name_label.setStyleSheet("color: #E8EAED; font-size: 13px; font-weight: 500;")
        layout.addWidget(name_label)

        # Create appropriate widget based on type
        input_widget = None
        if param_type == "float":
            spinbox = QDoubleSpinBox(parent=container)
            spinbox.setObjectName(f"param_input_{param_name}")
            spinbox.setDecimals(2)
            if param_step:
                spinbox.setSingleStep(float(param_step))
            if param_min is not None:
                spinbox.setMinimum(float(param_min))
            if param_max is not None:
                spinbox.setMaximum(float(param_max))
            spinbox.setValue(float(current_value))
            spinbox.valueChanged.connect(
                lambda val, p=param_name, d=param_def: self._on_parameter_changed(
                    p, val, d
                )
            )
            spinbox.setStyleSheet(self._spinbox_style("QDoubleSpinBox", is_valid=True))
            layout.addWidget(spinbox)
            input_widget = spinbox
        elif param_type == "int":
            spinbox = QSpinBox(parent=container)
            spinbox.setObjectName(f"param_input_{param_name}")
            if param_step:
                spinbox.setSingleStep(int(param_step))
            if param_min is not None:
                spinbox.setMinimum(int(param_min))
            if param_max is not None:
                spinbox.setMaximum(int(param_max))
            spinbox.setValue(int(current_value))
            spinbox.valueChanged.connect(
                lambda val, p=param_name, d=param_def: self._on_parameter_changed(
                    p, val, d
                )
            )
            spinbox.setStyleSheet(self._spinbox_style("QSpinBox", is_valid=True))
            layout.addWidget(spinbox)
            input_widget = spinbox
        else:
            # Fallback for other types
            label = QLabel(str(current_value), parent=container)
            label.setStyleSheet("color: #FFFFFF;")
            layout.addWidget(label)

        # Store widget reference for validation feedback
        if input_widget:
            self._param_widgets[param_name] = {
                "widget": input_widget,
                "container": container,
                "label": name_label,
                "definition": param_def,
            }

        # Description text
        if param_desc:
            desc_label = QLabel(param_desc, parent=container)
            desc_label.setStyleSheet("color: #9AA0A6; font-size: 11px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        self.params_layout.addWidget(container)

    def _add_simple_param_widget(self, param_name, param_value):
        """Add a simple parameter widget without schema."""
        container = QFrame(parent=self.params_container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        name_label = QLabel(param_name.replace("_", " ").title(), parent=container)
        name_label.setStyleSheet("color: #E8EAED; font-size: 13px; font-weight: 500;")
        layout.addWidget(name_label)

        value_label = QLabel(str(param_value), parent=container)
        value_label.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(value_label)

        self.params_layout.addWidget(container)

    def _on_parameter_changed(self, param_name, value, param_def):
        """Handle parameter value change and auto-save to model.

        Args:
            param_name: Name of the parameter
            value: New value
            param_def: Parameter definition dict with validation rules
        """
        if not self.current_node_id:
            return

        # Validate value
        is_valid = self._validate_parameter(value, param_def)

        # Update visual feedback
        self._update_validation_feedback(param_name, is_valid)

        if is_valid:
            self.current_node_params[param_name] = value
            self.node_param_changed.emit(self.current_node_id, param_name, value)

    def _validate_parameter(self, value, param_def):
        """Validate a parameter value against its definition.

        Args:
            value: The value to validate
            param_def: Parameter definition with min/max constraints

        Returns:
            True if valid, False otherwise
        """
        param_type = param_def.get("type", "float")

        try:
            if param_type == "float":
                val = float(value)
                param_min = param_def.get("min")
                param_max = param_def.get("max")

                if param_min is not None and val < float(param_min):
                    return False
                if param_max is not None and val > float(param_max):
                    return False
                return True

            elif param_type == "int":
                val = int(value)
                param_min = param_def.get("min")
                param_max = param_def.get("max")

                if param_min is not None and val < int(param_min):
                    return False
                if param_max is not None and val > int(param_max):
                    return False
                return True

            else:
                return True  # Unknown types pass through
        except (ValueError, TypeError):
            return False

    def _spinbox_style(self, selector: str, is_valid: bool = True) -> str:
        """Return consistent spinbox styling with visible up/down arrow icons."""
        border = "1px solid #2D3336" if is_valid else "2px solid #FF5252"
        focus_border = "1px solid #00B884" if is_valid else "2px solid #FF5252"

        return f"""
            {selector} {{
                background-color: #121415;
                border: {border};
                border-radius: 4px;
                padding: 8px;
                color: #E8EAED;
            }}
            {selector}:focus {{
                border: {focus_border};
            }}
            {selector}::up-button,
            {selector}::down-button {{
                subcontrol-origin: border;
                width: 22px;
                border-left: 1px solid #2D3336;
                background: #2D3336;
            }}
            {selector}::up-button:hover,
            {selector}::down-button:hover {{
                background: #3D4448;
            }}
            {selector}::up-arrow {{
                image: none;
                width: 0px;
                height: 0px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 7px solid #C9D1D9;
            }}
            {selector}::down-arrow {{
                image: none;
                width: 0px;
                height: 0px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #C9D1D9;
            }}
        """

    def _update_validation_feedback(self, param_name, is_valid):
        """Update visual feedback for a parameter's validation state.

        Args:
            param_name: Name of the parameter
            is_valid: True if value is valid, False otherwise
        """
        if param_name not in self._param_widgets:
            return

        widget_info = self._param_widgets[param_name]
        input_widget = widget_info["widget"]
        param_def = widget_info["definition"]
        param_type = param_def.get("type", "float")

        if is_valid:
            # Valid: normal styling
            if param_type == "float":
                input_widget.setStyleSheet(
                    self._spinbox_style("QDoubleSpinBox", is_valid=True)
                )
            elif param_type == "int":
                input_widget.setStyleSheet(
                    self._spinbox_style("QSpinBox", is_valid=True)
                )
        else:
            # Invalid: red border
            if param_type == "float":
                input_widget.setStyleSheet(
                    self._spinbox_style("QDoubleSpinBox", is_valid=False)
                )
            elif param_type == "int":
                input_widget.setStyleSheet(
                    self._spinbox_style("QSpinBox", is_valid=False)
                )

    def get_current_page(self):
        """Get current page name."""
        return "metadata" if self.stack.currentIndex() == 0 else "properties"

    def update_file_list(self, files: list):
        """Update the folder explorer file list.

        Args:
            files: List of file paths to display
        """
        self.current_files = files
        self.file_list.clear()

        if not files:
            self.file_list.hide()
            self.empty_label.show()
            self.refresh_btn.setEnabled(False)
            return

        self.empty_label.hide()
        self.file_list.show()
        self.refresh_btn.setEnabled(True)

        for file_path in files:
            import os

            filename = os.path.basename(file_path)
            self.file_list.addItem(filename)

        # Select first item by default
        if self.file_list.count() > 0:
            self.file_list.setCurrentRow(0)

    def _on_file_double_clicked(self, item):
        """Handle double-click on file list item."""
        filename = item.text()
        self.file_selected.emit(filename)

    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        self.refresh_requested.emit()

    def clear(self):
        """Clear all data and reset to metadata page."""
        self.current_node_id = None
        self.current_node_params = {}

        # Reset metadata
        self.filename_label.setText("No image loaded")
        self.file_desc_label.setText("Source Input")
        self.row_dimensions.setText("-")
        self.row_bitdepth.setText("-")
        self.row_channels.setText("-")
        self.row_filesize.setText("-")

        # Clear properties
        self.node_title_label.setText("No node selected")
        self._clear_params_layout()

        self.show_metadata()

    def set_folder_explorer_visible(self, visible: bool):
        """Show or hide the folder explorer section.

        Args:
            visible: True to show folder explorer, False to hide
        """
        if visible:
            self.folder_header_widget.show()
            self.file_list.show()
            # Show empty label only if we have no files
            if self.file_list.count() == 0:
                self.empty_label.show()
            else:
                self.empty_label.hide()
        else:
            self.folder_header_widget.hide()
            self.file_list.hide()
            self.empty_label.hide()
