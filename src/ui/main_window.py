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
    QStackedWidget,
    QPushButton,
    QButtonGroup,
    QMessageBox,
    QFileDialog,
    QProgressBar,
    QStatusBar,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QFont

from .image_navigation import ImageNavigationWidget
from .pipeline_view import PipelineConstructionWidget
from .batch_execution_view import BatchExecutionIntegrationWidget


class MainWindow(QMainWindow):
    """Main application window with view navigation, status bar, and keyboard shortcuts."""

    # Signals for inter-view communication
    pipeline_config_changed = pyqtSignal(dict)  # Pipeline config dict
    request_run_pipeline = pyqtSignal()  # Request to switch to batch execution
    status_message = pyqtSignal(str, int)  # message, timeout_ms

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.resize(1300, 850)

        # Shared state
        self._current_pipeline_config = {}
        self._selected_images = []

        self.apply_stylesheet()

        # Core Container
        self.main_container = QWidget()
        self.main_container.setObjectName("mainContainer")
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        self.setup_header()
        self.setup_content()
        self.setup_status_bar()
        self.setup_shortcuts()

        # Navigation setup
        self.nav_group.idClicked.connect(self.switch_view)

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
        
        /* NAVIGATION BUTTONS */
        QPushButton#navBtn {
            border: none;
            color: #9AA0A6;
            font-size: 13px;
            font-weight: 500;
            padding: 8px 16px;
            background-color: transparent;
        }
        QPushButton#navBtn:hover {
            color: #E8EAED;
        }
        QPushButton#navBtn:checked {
            color: #00B884;
            font-weight: bold;
            border-bottom: 2px solid #00B884;
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
        """
        self.setStyleSheet(style)

    def setup_header(self):
        """Create the header bar with logo, title, navigation, and avatar."""
        header = QFrame()
        header.setObjectName("AppHeader")
        header.setFixedHeight(56)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        # Left side: Logo
        logo = QLabel("🔬")
        logo.setObjectName("logoLabel")

        # Title
        title = QLabel("Phantast Lab")
        title.setObjectName("titleLabel")

        layout.addWidget(logo)
        layout.addWidget(title)

        # Navigation Tabs
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(32, 0, 0, 0)
        self.nav_group = QButtonGroup(self)

        self.btn_img = QPushButton("Image Loading")
        self.btn_img.setObjectName("navBtn")
        self.btn_img.setCheckable(True)
        self.btn_img.setChecked(True)
        self.nav_group.addButton(self.btn_img, 0)

        self.btn_pipe = QPushButton("Pipeline Construction")
        self.btn_pipe.setObjectName("navBtn")
        self.btn_pipe.setCheckable(True)
        self.nav_group.addButton(self.btn_pipe, 1)

        self.btn_exec = QPushButton("Batch Execution")
        self.btn_exec.setObjectName("navBtn")
        self.btn_exec.setCheckable(True)
        self.nav_group.addButton(self.btn_exec, 2)

        nav_layout.addWidget(self.btn_img)
        nav_layout.addWidget(self.btn_pipe)
        nav_layout.addWidget(self.btn_exec)

        layout.addLayout(nav_layout)
        layout.addStretch()

        # Right side: Avatar placeholder
        avatar = QLabel()
        avatar.setObjectName("avatarLabel")
        avatar.setFixedSize(32, 32)
        layout.addWidget(avatar)

        self.main_layout.addWidget(header)

    def setup_content(self):
        """Create the content area with QStackedWidget for view switching."""
        # Navigation Stack
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget, 1)

        self.load_views()

    def load_views(self):
        """Load all three main views into the stacked widget."""
        # 1. Image Navigation View (Index 0)
        self.image_nav_widget = ImageNavigationWidget()
        self.stacked_widget.addWidget(self.image_nav_widget)

        # 2. Pipeline Construction View (Index 1)
        self.pipeline_view = PipelineConstructionWidget()
        # Connect pipeline signals
        self.pipeline_view.run_pipeline.connect(self.jump_to_execution)
        self.stacked_widget.addWidget(self.pipeline_view)

        # 3. Batch Execution View (Index 2)
        self.batch_view = BatchExecutionIntegrationWidget()
        self.stacked_widget.addWidget(self.batch_view)

        # Connect view signals for state synchronization
        self._connect_view_signals()

    def _connect_view_signals(self):
        """Connect signals between views for state synchronization."""
        # Pipeline construction sends config to batch execution
        self.pipeline_view.run_pipeline.connect(self._sync_pipeline_to_batch)

        # Image navigation signals for opening files
        self.image_nav_widget.open_single_image_requested.connect(
            self._handle_image_opened
        )
        self.image_nav_widget.open_folder_requested.connect(self._handle_folder_opened)

    def _sync_pipeline_to_batch(self):
        """Synchronize pipeline configuration to batch execution view."""
        # Extract pipeline config from pipeline view
        self._current_pipeline_config = self._get_pipeline_config()
        self.status_message.emit(
            "Pipeline configuration ready for batch execution", 3000
        )

    def _get_pipeline_config(self) -> dict:
        """Extract current pipeline configuration."""
        config = {
            "nodes": self.pipeline_view.pipeline.get("nodes", []),
            "active_node_id": self.pipeline_view.active_node_id,
        }
        return config

    def _handle_image_opened(self, filepath: str):
        """Handle image opened signal - update status."""
        filename = os.path.basename(filepath)
        self.status_message.emit(f"Opened: {filename}", 3000)

    def _handle_folder_opened(self, folderpath: str):
        """Handle folder opened signal - update status."""
        folder_name = os.path.basename(folderpath)
        self.status_message.emit(f"Opened folder: {folder_name}", 3000)

    def switch_view(self, index):
        """Switch to the specified view index."""
        self.stacked_widget.setCurrentIndex(index)

    def jump_to_execution(self):
        """Switch to batch execution view (called from pipeline view)."""
        self.btn_exec.setChecked(True)
        self.switch_view(2)
        self.status_message.emit("Running batch execution...", 3000)

    def setup_status_bar(self):
        """Setup the status bar with progress and info widgets."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Ready status
        self.status_bar.showMessage("Ready")

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

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        # File menu actions
        self._setup_file_shortcuts()
        # View navigation shortcuts
        self._setup_navigation_shortcuts()
        # Help shortcut
        self._setup_help_shortcut()

    def _setup_file_shortcuts(self):
        """Setup file-related keyboard shortcuts."""
        # Ctrl+O: Open Image
        open_action = QAction("Open Image", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self._shortcut_open_image)
        self.addAction(open_action)

        # Ctrl+Shift+O: Open Folder
        open_folder_action = QAction("Open Folder", self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_folder_action.triggered.connect(self._shortcut_open_folder)
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

    def _setup_navigation_shortcuts(self):
        """Setup view navigation shortcuts."""
        # F1: Image Loading View
        view1_action = QAction("Image Loading", self)
        view1_action.setShortcut(QKeySequence("F1"))
        view1_action.triggered.connect(lambda: self._switch_to_view(0))
        self.addAction(view1_action)

        # F2: Pipeline Construction View
        view2_action = QAction("Pipeline Construction", self)
        view2_action.setShortcut(QKeySequence("F2"))
        view2_action.triggered.connect(lambda: self._switch_to_view(1))
        self.addAction(view2_action)

        # F3: Batch Execution View
        view3_action = QAction("Batch Execution", self)
        view3_action.setShortcut(QKeySequence("F3"))
        view3_action.triggered.connect(lambda: self._switch_to_view(2))
        self.addAction(view3_action)

    def _setup_help_shortcut(self):
        """Setup help shortcut."""
        # F12 or Ctrl+?: Show shortcuts help
        help_action = QAction("Help", self)
        help_action.setShortcut(QKeySequence("F12"))
        help_action.triggered.connect(self._show_shortcuts_help)
        self.addAction(help_action)

    def _switch_to_view(self, index: int):
        """Switch to view by index and update nav button state."""
        button_map = {0: self.btn_img, 1: self.btn_pipe, 2: self.btn_exec}
        if index in button_map:
            button_map[index].setChecked(True)
            self.switch_view(index)

    def _shortcut_open_image(self):
        """Handle Ctrl+O shortcut - open image dialog."""
        # Only works in Image Navigation view
        if self.stacked_widget.currentIndex() == 0:
            self.image_nav_widget.action_open_image()
        else:
            # Switch to image view first
            self._switch_to_view(0)
            QTimer.singleShot(100, self.image_nav_widget.action_open_image)

    def _shortcut_open_folder(self):
        """Handle Ctrl+Shift+O shortcut - open folder dialog."""
        if self.stacked_widget.currentIndex() == 0:
            self.image_nav_widget.action_open_folder()
        else:
            self._switch_to_view(0)
            QTimer.singleShot(100, self.image_nav_widget.action_open_folder)

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
        <h3>Navigation</h3>
        <ul>
            <li><b>F1</b> - Image Loading View</li>
            <li><b>F2</b> - Pipeline Construction View</li>
            <li><b>F3</b> - Batch Execution View</li>
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
