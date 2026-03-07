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
)
from PyQt6.QtCore import Qt, pyqtSignal


class UnifiedRightPanel(QFrame):
    """Right panel that switches between image metadata and node properties."""

    panel_changed = pyqtSignal(str)  # 'metadata' or 'properties'
    node_param_changed = pyqtSignal(str, str, object)  # node_id, param_name, value

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMinimumWidth(280)
        self.setObjectName("rightPanel")

        self.current_node_id = None
        self.current_node_params = {}

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
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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
        container.setStyleSheet("margin-bottom: 16px;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Parameter name label
        name_label = QLabel(param_name.replace("_", " ").title(), parent=container)
        name_label.setStyleSheet("color: #E8EAED; font-size: 13px; font-weight: 500;")
        layout.addWidget(name_label)

        # Create appropriate widget based on type
        if param_type == "float":
            spinbox = QDoubleSpinBox(parent=container)
            spinbox.setDecimals(1)
            if param_step:
                spinbox.setSingleStep(float(param_step))
            if param_min is not None:
                spinbox.setMinimum(float(param_min))
            if param_max is not None:
                spinbox.setMaximum(float(param_max))
            spinbox.setValue(float(current_value))
            spinbox.valueChanged.connect(
                lambda val, p=param_name: self._on_parameter_changed(p, val)
            )
            spinbox.setStyleSheet("""
                QDoubleSpinBox {
                    background-color: #121415;
                    border: 1px solid #2D3336;
                    border-radius: 4px;
                    padding: 8px;
                    color: #E8EAED;
                }
            """)
            layout.addWidget(spinbox)
        elif param_type == "int":
            spinbox = QSpinBox(parent=container)
            if param_step:
                spinbox.setSingleStep(int(param_step))
            if param_min is not None:
                spinbox.setMinimum(int(param_min))
            if param_max is not None:
                spinbox.setMaximum(int(param_max))
            spinbox.setValue(int(current_value))
            spinbox.valueChanged.connect(
                lambda val, p=param_name: self._on_parameter_changed(p, val)
            )
            spinbox.setStyleSheet("""
                QSpinBox {
                    background-color: #121415;
                    border: 1px solid #2D3336;
                    border-radius: 4px;
                    padding: 8px;
                    color: #E8EAED;
                }
            """)
            layout.addWidget(spinbox)
        else:
            # Fallback for other types
            label = QLabel(str(current_value), parent=container)
            label.setStyleSheet("color: #FFFFFF;")
            layout.addWidget(label)

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

    def _on_parameter_changed(self, param_name, value):
        """Handle parameter value change."""
        if self.current_node_id:
            self.current_node_params[param_name] = value
            self.node_param_changed.emit(self.current_node_id, param_name, value)

    def get_current_page(self):
        """Get current page name."""
        return "metadata" if self.stack.currentIndex() == 0 else "properties"

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
