import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QProgressBar,
    QStatusBar,
    QSplitter,
    QStackedWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QFont

from ..controllers.main_controller import MainController
from .unified_main_widget import UnifiedMainWidget
from .pipeline_stack_widget import PipelineStackWidget
from .node_property_editor import NodePropertyEditor


class MainWindow(QMainWindow):
    """
    Main application window with unified interface.

    Features:
    - Single unified view (no view switching)
    - Pipeline stack in left panel
    - Image canvas in center
    - Properties/node editor in right panel
    - Status bar with messages and progress
    - Keyboard shortcuts
    """

    status_message = pyqtSignal(str, int)  # message, timeout_ms

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.resize(1400, 900)

        # Initialize controller
        self.controller = MainController()

        self.apply_stylesheet()

        # Setup UI components
        self._setup_central_widget()
        self._setup_header()
        self._setup_status_bar()
        self._setup_shortcuts()

        # Connect signals
        self._connect_signals()

    def apply_stylesheet(self):
        """Apply dark theme stylesheet."""
        style = """
        QMainWindow, QWidget#mainContainer {
            background-color: #121415;
            color: #E8EAED;
            font-family: "Inter", "Segoe UI", sans-serif;
            font-size: 13px;
        }
        
        /* HEADER */
        QFrame#AppHeader {
            background-color: #121415;
            border-bottom: 1px solid #2D3336;
        }
        
        /* LOGO */
        QLabel#logoLabel {
            font-size: 20px;
            color: #00B884;
        }
        
        /* TITLE */
        QLabel#titleLabel {
            font-size: 15px;
            font-weight: bold;
            color: #E8EAED;
        }
        
        /* AVATAR */
        QLabel#avatarLabel {
            background-color: #E8A317;
            border-radius: 16px;
        }
        
        /* STATUS BAR */
        QStatusBar {
            background-color: #1E2224;
            color: #9AA0A6;
            border-top: 1px solid #2D3336;
        }
        QStatusBar::item {
            border: none;
        }
        
        /* PROGRESS BAR */
        QProgressBar {
            border: 1px solid #2D3336;
            border-radius: 2px;
            background-color: #121415;
            height: 12px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #00B884;
            border-radius: 2px;
        }
        
        /* NODE PROPERTY EDITOR */
        QWidget#nodePropertyEditor {
            background-color: #121415;
        }
        QLabel#panelHeader {
            color: #9AA0A6;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        QFrame#infoBox {
            background-color: #1E2224;
            border: 1px solid #2D3336;
            border-radius: 6px;
        }
        QLabel#nodeNameLabel {
            color: #E8EAED;
            font-weight: 600;
            font-size: 14px;
        }
        QLabel#nodeTypeLabel {
            color: #9AA0A6;
            font-size: 11px;
            text-transform: uppercase;
        }
        QLabel#nodeDescLabel {
            color: #9AA0A6;
            font-size: 12px;
            margin-top: 8px;
        }
        QLabel#sectionHeader {
            color: #E8EAED;
            font-size: 13px;
            font-weight: 600;
        }
        QFrame#paramEditor {
            background-color: transparent;
        }
        QLabel#paramLabel {
            color: #E8EAED;
            font-size: 12px;
            font-weight: 500;
        }
        QLabel#paramDesc {
            color: #9AA0A6;
            font-size: 11px;
        }
        QSpinBox, QDoubleSpinBox {
            background-color: #121415;
            border: 1px solid #2D3336;
            border-radius: 4px;
            padding: 6px;
            color: #E8EAED;
        }
        QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #00B884;
        }
        """
        self.setStyleSheet(style)

    def _setup_central_widget(self):
        """Setup the central widget with unified interface."""
        # Create unified main widget
        self.unified_widget = UnifiedMainWidget(self.controller, self)

        # Create and set pipeline widget
        self.pipeline_widget = PipelineStackWidget(self.controller, self.unified_widget)
        self.unified_widget.set_pipeline_widget(self.pipeline_widget)

        # Create and set node property editor
        self.property_editor = NodePropertyEditor(self.controller, self.unified_widget)
        self.unified_widget.set_node_properties_widget(self.property_editor)

        self.setCentralWidget(self.unified_widget)

    def _setup_header(self):
        """Create the header bar with logo and title."""
        # Create header as a widget that floats above
        self.header = QFrame()
        self.header.setObjectName("AppHeader")
        self.header.setFixedHeight(56)

        layout = QHBoxLayout(self.header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        # Logo
        logo = QLabel("🔬")
        logo.setObjectName("logoLabel")

        # Title
        title = QLabel("Phantast Lab")
        title.setObjectName("titleLabel")

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()

        # Right side: Open buttons
        open_img_btn = QPushButton("Open Image")
        open_img_btn.setObjectName("openBtn")
        open_img_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #00B884;
                border: 1px solid #00B884;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 184, 132, 0.1);
            }
        """)
        open_img_btn.clicked.connect(self._on_open_image)

        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.setObjectName("openBtn")
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #00B884;
                border: 1px solid #00B884;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 184, 132, 0.1);
            }
        """)
        open_folder_btn.clicked.connect(self._on_open_folder)

        layout.addWidget(open_img_btn)
        layout.addWidget(open_folder_btn)

        layout.addSpacing(16)

        # Run Pipeline button
        run_btn = QPushButton("▶ Run")
        run_btn.setObjectName("runBtn")
        run_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B884;
                color: #121415;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00D494;
            }
            QPushButton:disabled {
                background-color: #2D3336;
                color: #5A6066;
            }
        """)
        run_btn.clicked.connect(self._on_run_pipeline)
        run_btn.setEnabled(False)  # Disabled until image is loaded
        self.run_button = run_btn  # Store reference for enabling/disabling
        layout.addWidget(run_btn)

        layout.addSpacing(16)

        # Avatar placeholder
        avatar = QLabel()
        avatar.setObjectName("avatarLabel")
        avatar.setFixedSize(32, 32)
        layout.addWidget(avatar)

        # Add header to the unified widget's layout
        # The unified_widget has a main_layout (QHBoxLayout from QSplitter)
        # We need to wrap it in a vertical layout with the header

        # Create a container widget to hold header + unified widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self.header)

        # Reparent unified_widget to container
        self.unified_widget.setParent(container)
        container_layout.addWidget(self.unified_widget, 1)

        # Set container as central widget
        self.setCentralWidget(container)

    def _connect_signals(self):
        """Connect controller signals to UI updates."""
        # Status messages
        self.controller.preview_started.connect(
            lambda: self.status_message.emit("Processing preview...", 2000)
        )
        self.controller.preview_completed.connect(
            lambda: self.status_message.emit("Preview updated", 2000)
        )

        # Enable/disable run button based on image state
        self.controller.image_loaded.connect(lambda _: self.run_button.setEnabled(True))
        self.controller.image_cleared.connect(lambda: self.run_button.setEnabled(False))

        # Image operations
        self.controller.image_loaded.connect(
            lambda path: self.status_message.emit(
                f"Loaded: {os.path.basename(path)}", 3000
            )
        )

        # Node operations
        self.controller.node_added.connect(
            lambda node_id: self.status_message.emit("Node added", 2000)
        )
        self.controller.node_removed.connect(
            lambda node_id: self.status_message.emit("Node removed", 2000)
        )

    def _setup_status_bar(self):
        """Setup the status bar with progress and info widgets."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Ready status
        self.status_bar.showMessage("Ready - Open an image to start")

        # Connect status message signal
        self.status_message.connect(self._show_status_message)

    def _show_status_message(self, message: str, timeout_ms: int = 3000):
        """Show a status message in the status bar."""
        self.status_bar.showMessage(message, timeout_ms)

    def show_progress(self, value: int, maximum: int = 100):
        """Show progress bar with current value."""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)

    def hide_progress(self):
        """Hide the progress bar."""
        self.progress_bar.setVisible(False)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        # File menu actions
        self._setup_file_shortcuts()
        # Help shortcut
        self._setup_help_shortcut()

    def _setup_file_shortcuts(self):
        """Setup file-related keyboard shortcuts."""
        # Ctrl+O: Open Image
        open_action = QAction("Open Image", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self._on_open_image)
        self.addAction(open_action)

        # Ctrl+Shift+O: Open Folder
        open_folder_action = QAction("Open Folder", self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_folder_action.triggered.connect(self._on_open_folder)
        self.addAction(open_folder_action)

        # Ctrl+S: Save
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self._shortcut_save)
        self.addAction(save_action)

        # Ctrl+Q: Quit
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        self.addAction(quit_action)

    def _setup_help_shortcut(self):
        """Setup help shortcut."""
        help_action = QAction("Help", self)
        help_action.setShortcut(QKeySequence("F12"))
        help_action.triggered.connect(self._show_shortcuts_help)
        self.addAction(help_action)

    def _on_open_image(self):
        """Handle open image action."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.tiff *.tif *.png *.jpg *.jpeg *.bmp)"
        )
        if filepath:
            self.controller.load_image(filepath)

    def _on_open_folder(self):
        """Handle open folder action."""
        folderpath = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folderpath:
            self.controller.load_folder(folderpath)

    def _on_run_pipeline(self):
        """Handle run pipeline action."""
        if not self.controller.has_image:
            self.status_message.emit("No image loaded", 3000)
            return

        # Trigger immediate preview execution
        self.controller.request_immediate_preview()
        self.status_message.emit("Running pipeline...", 2000)

    def _shortcut_save(self):
        """Handle Ctrl+S shortcut - save current state."""
        self.status_message.emit("Save functionality not yet implemented", 3000)

    def _show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog."""
        shortcuts_text = """
        <h2>Keyboard Shortcuts</h2>
        <h3>File</h3>
        <ul>
            <li><b>Ctrl+O</b> - Open Image</li>
            <li><b>Ctrl+Shift+O</b> - Open Folder</li>
            <li><b>Ctrl+S</b> - Save</li>
            <li><b>Ctrl+Q</b> - Quit</li>
        </ul>
        <h3>Help</h3>
        <ul>
            <li><b>F12</b> - Show this help</li>
        </ul>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Keyboard Shortcuts")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(shortcuts_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def show_error_dialog(self, title: str, message: str):
        """Show an error dialog to the user."""
        error_box = QMessageBox(self)
        error_box.setWindowTitle(title)
        error_box.setText(message)
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_box.exec()

    def show_warning_dialog(self, title: str, message: str):
        """Show a warning dialog to the user."""
        warning_box = QMessageBox(self)
        warning_box.setWindowTitle(title)
        warning_box.setText(message)
        warning_box.setIcon(QMessageBox.Icon.Warning)
        warning_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        warning_box.exec()

    def show_info_dialog(self, title: str, message: str):
        """Show an info dialog to the user."""
        info_box = QMessageBox(self)
        info_box.setWindowTitle(title)
        info_box.setText(message)
        info_box.setIcon(QMessageBox.Icon.Information)
        info_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        info_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
