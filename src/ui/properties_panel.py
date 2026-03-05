from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal
import os


class FileListItem(QWidget):
    """Custom widget for file list items with FILE/SIZE/STATUS columns."""

    clicked = pyqtSignal(str)

    def __init__(self, filename: str, file_size: str, parent=None):
        super().__init__(parent)
        self.filename = filename
        self._is_selected = False

        self._setup_ui(file_size)

    def _setup_ui(self, file_size: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # File icon and name
        self.icon_label = QLabel("📄")
        self.icon_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.icon_label)

        self.filename_label = QLabel(self.filename)
        self.filename_label.setObjectName("filenameLabel")
        self.filename_label.setStyleSheet("color: #E8EAED; font-size: 12px;")
        layout.addWidget(self.filename_label, stretch=3)

        # Size
        self.size_label = QLabel(file_size)
        self.size_label.setObjectName("sizeLabel")
        self.size_label.setStyleSheet(
            "color: #9AA0A6; font-size: 11px; font-family: 'JetBrains Mono';"
        )
        layout.addWidget(self.size_label, stretch=1)

        # Status
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setStyleSheet("""
            color: #00B884;
            font-weight: bold;
            font-size: 10px;
            background-color: rgba(0, 184, 132, 0.2);
            padding: 2px 8px;
            border-radius: 4px;
        """)
        layout.addWidget(self.status_label, stretch=1)

        # Make clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            FileListItem {
                background-color: transparent;
                border-bottom: 1px solid #2D3336;
            }
            FileListItem:hover {
                background-color: #1E2224;
            }
        """)

    def set_selected(self, selected: bool):
        """Update selection state."""
        self._is_selected = selected
        if selected:
            self.setStyleSheet("""
                FileListItem {
                    background-color: rgba(0, 184, 132, 0.15);
                    border-left: 3px solid #00B884;
                }
                FileListItem:hover {
                    background-color: rgba(0, 184, 132, 0.2);
                }
            """)
        else:
            self.setStyleSheet("""
                FileListItem {
                    background-color: transparent;
                    border-bottom: 1px solid #2D3336;
                }
                FileListItem:hover {
                    background-color: #1E2224;
                }
            """)

    def set_status(self, status: str):
        """Set status text (e.g., 'VIEWING')."""
        self.status_label.setText(status)

    def mousePressEvent(self, event):
        """Handle click to select file."""
        self.clicked.emit(self.filename)
        super().mousePressEvent(event)


class PropertiesPanel(QWidget):
    """
    Right panel widget for displaying image metadata and properties.
    """

    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setObjectName("rightPanel")

        # File list tracking
        self.file_item_widgets = {}
        self.current_files = []
        self.current_folder_path = ""
        self.current_index = -1

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

        # Folder Explorer section (hidden by default)
        self._setup_folder_explorer()

    def _setup_folder_explorer(self):
        """Setup folder explorer UI section."""
        # Folder Explorer Header
        self.folder_explorer_header = QLabel("Folder Explorer")
        self.folder_explorer_header.setObjectName("sectionHeader")
        self.folder_explorer_header.setStyleSheet("""
            color: #E8EAED;
            font-size: 13px;
            font-weight: 600;
            margin-top: 16px;
            margin-bottom: 8px;
        """)
        self.folder_explorer_header.hide()
        self.content_layout.addWidget(self.folder_explorer_header)

        # Column headers
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(12, 4, 12, 4)
        header_layout.setSpacing(8)

        file_header = QLabel("FILE")
        file_header.setStyleSheet(
            "color: #9AA0A6; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        header_layout.addWidget(file_header, stretch=3)

        size_header = QLabel("SIZE")
        size_header.setStyleSheet(
            "color: #9AA0A6; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        header_layout.addWidget(size_header, stretch=1)

        status_header = QLabel("STATUS")
        status_header.setStyleSheet(
            "color: #9AA0A6; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        header_layout.addWidget(status_header, stretch=1)

        header_widget.hide()
        self.folder_explorer_header_header = header_widget
        self.content_layout.addWidget(header_widget)

        # File list scroll area
        self.file_list_scroll = QScrollArea()
        self.file_list_scroll.setWidgetResizable(True)
        self.file_list_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.file_list_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.file_list_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )
        self.file_list_scroll.setMaximumHeight(200)
        self.file_list_scroll.hide()

        self.file_list_container = QWidget()
        self.file_list_layout = QVBoxLayout(self.file_list_container)
        self.file_list_layout.setContentsMargins(0, 0, 0, 0)
        self.file_list_layout.setSpacing(0)
        self.file_list_layout.addStretch()

        self.file_list_scroll.setWidget(self.file_list_container)
        self.content_layout.addWidget(self.file_list_scroll)

        # Navigation controls
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 8, 0, 0)
        nav_layout.setSpacing(8)

        self.btn_prev = QPushButton("‹ Previous")
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                color: #E8EAED;
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2D3336; }
            QPushButton:disabled { background-color: #121415; color: #5A6366; }
        """)
        self.btn_prev.setFixedHeight(28)
        self.btn_prev.clicked.connect(self.select_previous_file)

        self.lbl_counter = QLabel("0 / 0")
        self.lbl_counter.setStyleSheet(
            "color: #9AA0A6; font-family: 'JetBrains Mono'; font-size: 12px; font-weight: 600;"
        )
        self.lbl_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_next = QPushButton("Next ›")
        self.btn_next.setStyleSheet("""
            QPushButton {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                color: #E8EAED;
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2D3336; }
            QPushButton:disabled { background-color: #121415; color: #5A6366; }
        """)
        self.btn_next.setFixedHeight(28)
        self.btn_next.clicked.connect(self.select_next_file)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.lbl_counter, stretch=1)
        nav_layout.addWidget(self.btn_next)

        nav_widget.hide()
        self.folder_explorer_nav = nav_widget
        self.content_layout.addWidget(nav_widget)

    def update_file_list(self, files: list, folder_path: str = ""):
        """Update file list with custom FileListItem widgets."""
        # Clear existing widgets
        self._clear_file_list()

        if not files:
            # Hide folder explorer
            self.folder_explorer_header.hide()
            self.folder_explorer_header_header.hide()
            self.file_list_scroll.hide()
            self.folder_explorer_nav.hide()
            return

        self.current_files = files
        self.current_folder_path = folder_path
        self.current_index = -1

        # Show folder explorer
        self.folder_explorer_header.show()
        self.folder_explorer_header_header.show()
        self.file_list_scroll.show()
        self.folder_explorer_nav.show()

        # Create FileListItem for each file
        for filename in files:
            filepath = os.path.join(folder_path, filename) if folder_path else filename
            file_size = self._get_file_size(filepath)

            item = FileListItem(filename, file_size)
            item.clicked.connect(self._on_file_clicked)

            # Insert before the stretch
            self.file_list_layout.insertWidget(self.file_list_layout.count() - 1, item)
            self.file_item_widgets[filename] = item

        # Update counter
        self._update_counter()

    def _clear_file_list(self):
        """Clear all file list widgets."""
        self.file_item_widgets.clear()
        # Remove all widgets except the stretch
        while self.file_list_layout.count() > 1:
            item = self.file_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _get_file_size(self, filepath: str) -> str:
        """Get formatted file size."""
        try:
            size_bytes = os.path.getsize(filepath)
            if size_bytes > 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / 1024:.0f} KB"
        except:
            return "-"

    def _on_file_clicked(self, filename: str):
        """Handle file click."""
        self.file_selected.emit(filename)

    def set_active_file(self, filename: str):
        """Update UI to show which file is being viewed."""
        if filename not in self.file_item_widgets:
            return

        # Update current index
        if filename in self.current_files:
            self.current_index = self.current_files.index(filename)

        # Update VIEWING status for all items
        for name, widget in self.file_item_widgets.items():
            is_active = name == filename
            widget.set_status("VIEWING" if is_active else "")
            widget.set_selected(is_active)

        # Update counter
        self._update_counter()

        # Scroll to active item
        if filename in self.file_item_widgets:
            self.file_list_scroll.ensureWidgetVisible(self.file_item_widgets[filename])

    def _update_counter(self):
        """Update the file counter label."""
        total = len(self.current_files)
        current = self.current_index + 1 if self.current_index >= 0 else 0
        self.lbl_counter.setText(f"{current} / {total}")

        # Enable/disable nav buttons
        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < total - 1)

    def select_previous_file(self):
        """Select the previous file in the list."""
        if not self.current_files or self.current_index <= 0:
            return
        self.current_index -= 1
        filename = self.current_files[self.current_index]
        self._on_file_clicked(filename)

    def select_next_file(self):
        """Select the next file in the list."""
        if not self.current_files or self.current_index >= len(self.current_files) - 1:
            return
        self.current_index += 1
        filename = self.current_files[self.current_index]
        self._on_file_clicked(filename)

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
