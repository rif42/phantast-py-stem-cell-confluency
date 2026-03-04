from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class PropertiesPanel(QWidget):
    """
    Right panel widget for displaying image metadata and properties.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setObjectName("rightPanel")

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)

        # Header
        header = QLabel("PROPERTIES")
        header.setObjectName("panelHeader")
        self.layout.addWidget(header)

        # Content container
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)

        self._show_empty_state()

        self.layout.addWidget(self.content)
        self.layout.addStretch()

    def _show_empty_state(self):
        """Show empty state when no image selected."""
        # Clear content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Empty icon
        empty_icon = QLabel("📊")
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon.setStyleSheet("font-size: 32px; color: #2D3336; margin-top: 40px;")
        self.content_layout.addWidget(empty_icon)

        # Empty text
        empty_text = QLabel("No Selection\nSelect an image to view properties.")
        empty_text.setObjectName("emptyLabel")
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_text.setWordWrap(True)
        self.content_layout.addWidget(empty_text)

    def _show_properties(self, filename: str, subtitle: str, metadata: dict):
        """Show properties for selected image."""
        # Clear content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # File info box
        file_box = QFrame()
        file_box.setObjectName("fileBox")
        fb_layout = QVBoxLayout(file_box)
        fb_layout.setContentsMargins(12, 12, 12, 12)

        filename_label = QLabel(filename)
        filename_label.setObjectName("filenameLabel")
        fb_layout.addWidget(filename_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("fileDesc")
        fb_layout.addWidget(subtitle_label)

        self.content_layout.addWidget(file_box)

        # Metadata section
        if metadata:
            meta_header = QLabel("Image Metadata")
            meta_header.setObjectName("sectionHeader")
            self.content_layout.addWidget(meta_header)

            for key, value in metadata.items():
                self._add_property_row(key, value)

    def _add_property_row(self, label: str, value: str):
        """Add a property row."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 4)

        label_widget = QLabel(label)
        label_widget.setObjectName("propertyLabel")

        value_widget = QLabel(value)
        value_widget.setObjectName("propertyValue")
        value_widget.setAlignment(Qt.AlignmentFlag.AlignRight)

        row.addWidget(label_widget)
        row.addWidget(value_widget)

        # Add to a widget to insert in layout
        row_widget = QWidget()
        row_widget.setLayout(row)
        self.content_layout.addWidget(row_widget)

    def update_metadata(
        self,
        filename: str = "-",
        subtitle: str = "-",
        dimensions: str = "-",
        bitdepth: str = "-",
        channels: str = "-",
        filesize: str = "-",
    ):
        """Update metadata display."""
        if filename == "-":
            self._show_empty_state()
        else:
            metadata = {
                "Dimensions": dimensions,
                "Bit Depth": bitdepth,
                "Channels": channels,
                "File Size": filesize,
            }
            self._show_properties(filename, subtitle, metadata)

    def _apply_styles(self):
        """Apply dark theme styles."""
        self.setStyleSheet("""
            QWidget#rightPanel {
                background-color: #121415;
                border-left: 1px solid #2D3336;
            }
            QLabel#panelHeader {
                color: #9AA0A6;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QLabel#emptyLabel {
                color: #9AA0A6;
                font-size: 12px;
                line-height: 1.4;
                margin-top: 16px;
            }
            QFrame#fileBox {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                border-radius: 6px;
                margin-bottom: 8px;
            }
            QLabel#filenameLabel {
                font-weight: 600;
                font-size: 13px;
                color: #FFFFFF;
            }
            QLabel#fileDesc {
                font-size: 11px;
                color: #9AA0A6;
                margin-top: 2px;
            }
            QLabel#sectionHeader {
                color: #E8EAED;
                font-size: 13px;
                font-weight: 600;
                margin-top: 16px;
                margin-bottom: 12px;
            }
            QLabel#propertyLabel {
                color: #9AA0A6;
                font-size: 12px;
            }
            QLabel#propertyValue {
                color: #FFFFFF;
                font-family: 'JetBrains Mono', monospace;
                font-size: 12px;
            }
        """)
