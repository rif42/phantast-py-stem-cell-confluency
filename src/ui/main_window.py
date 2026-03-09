"""Main Window - Combined Image Navigation and Pipeline Construction."""

import sys
import os

# Import our custom components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSplitter,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor

# Models
from src.models.image_model import ImageSessionModel
from src.models.pipeline_model import Pipeline, PipelineNode

# Views
from src.ui.pipeline_stack_widget import PipelineStackWidget
from src.ui.image_canvas import ImageCanvas
from src.ui.unified_right_panel import UnifiedRightPanel

# Controllers
from src.controllers.image_controller import ImageNavigationController
from src.controllers.pipeline_controller import PipelineController


class MainWindow(QMainWindow):
    """Main application window combining image navigation and pipeline features."""

    # Signals for ImageNavigationController compatibility
    open_single_image_requested = pyqtSignal(str)
    open_folder_requested = pyqtSignal(str)
    file_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.resize(1400, 900)

        # State
        self.current_image_path = None
        self.available_nodes = []

        # Core Container
        self.main_container = QWidget(parent=self)
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        self.setup_header()
        self.setup_models()
        self.setup_ui_components()
        self.setup_controllers()
        self.wire_signals()
        self.apply_styles()

    def setup_header(self):
        """Create the top header bar."""
        header = QFrame(parent=self.main_container)
        header.setObjectName("AppHeader")
        header.setFixedHeight(56)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        # Left side
        logo = QLabel("🔬", parent=header)
        logo.setObjectName("appLogo")

        title = QLabel("Phantast Lab", parent=header)
        title.setObjectName("appTitle")

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()

        # Right side -> Avatar
        avatar = QLabel(parent=header)
        avatar.setFixedSize(32, 32)
        avatar.setObjectName("appAvatar")
        layout.addWidget(avatar)

        self.main_layout.addWidget(header)

    def setup_models(self):
        """Initialize data models."""
        self.image_model = ImageSessionModel()
        self.pipeline_model = Pipeline()
        self._load_available_nodes()

    def _load_available_nodes(self):
        """Load available processing nodes from step registry."""
        try:
            from src.core.steps import STEP_REGISTRY

            self.available_nodes = []
            for step_name, step_meta in STEP_REGISTRY.items():
                node_info = {
                    "type": step_name,
                    "name": step_meta.description,
                    "description": step_meta.description,
                    "icon": step_meta.icon,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.type,
                            "default": p.default,
                            "min": p.min,
                            "max": p.max,
                            "step": p.step,
                            "description": p.description,
                        }
                        for p in step_meta.parameters
                    ],
                }
                self.available_nodes.append(node_info)
        except Exception:
            self.available_nodes = []

    def setup_ui_components(self):
        """Create and arrange the main UI components."""
        # Create a container for the 3-panel layout
        self.content_container = QWidget(parent=self.main_container)
        content_layout = QHBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Use QSplitter for resizable panels
        self.splitter = QSplitter(
            Qt.Orientation.Horizontal, parent=self.content_container
        )
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #2D3336; }")

        # === LEFT PANEL: Pipeline Stack ===
        self.pipeline_stack = PipelineStackWidget(parent=self.splitter)
        if self.pipeline_stack.add_button:
            self.pipeline_stack.add_button.setEnabled(
                False
            )  # Disabled until image loaded
            self.pipeline_stack.add_button.setToolTip("Load an image first")
        self.splitter.addWidget(self.pipeline_stack)

        # === CENTER PANEL: Image Canvas with Toolbar ===
        self.canvas_container = QWidget(parent=self.splitter)
        canvas_layout = QVBoxLayout(self.canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)

        # Floating toolbar
        toolbar_container = QWidget(parent=self.canvas_container)
        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QFrame(parent=toolbar_container)
        toolbar.setObjectName("floatingToolbar")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(12, 8, 12, 8)
        tb_layout.setSpacing(16)

        # Toolbar buttons
        self.btn_pan = QPushButton("🤚", parent=toolbar)
        self.btn_pan.setObjectName("toolBtn")
        self.btn_pan.setCheckable(True)
        self.btn_pan.clicked.connect(self.toggle_pan_mode)

        btn_measure = QPushButton("📏", parent=toolbar)
        btn_measure.setObjectName("toolBtn")

        btn_zoom_out = QPushButton("−", parent=toolbar)
        btn_zoom_out.setObjectName("toolBtn")
        btn_zoom_out.clicked.connect(self.action_zoom_out)

        self.lbl_zoom = QLabel("100%", parent=toolbar)
        self.lbl_zoom.setObjectName("toolLabel")
        self.lbl_zoom.setFixedWidth(45)
        self.lbl_zoom.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_zoom_in = QPushButton("+", parent=toolbar)
        btn_zoom_in.setObjectName("toolBtn")
        btn_zoom_in.clicked.connect(self.action_zoom_in)

        for w in [self.btn_pan, btn_measure, btn_zoom_out, self.lbl_zoom, btn_zoom_in]:
            tb_layout.addWidget(w)

        toolbar_layout.addStretch()
        toolbar_layout.addWidget(toolbar)
        toolbar_layout.addStretch()

        canvas_layout.addWidget(toolbar_container)

        # Image canvas
        self.image_canvas = ImageCanvas(parent=self.canvas_container)
        self.image_canvas.setObjectName("canvasImage")
        self.image_canvas.zoom_changed.connect(
            lambda pct: self.lbl_zoom.setText(f"{pct}%")
        )
        canvas_layout.addWidget(self.image_canvas)

        # Empty state overlay (shown when no image)
        self.empty_overlay = QWidget(parent=self.canvas_container)
        self.empty_overlay.setObjectName("emptyOverlay")
        overlay_layout = QVBoxLayout(self.empty_overlay)
        overlay_layout.setContentsMargins(16, 16, 16, 16)
        overlay_layout.setSpacing(0)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Dashed border container
        dashed_container = QFrame(parent=self.empty_overlay)
        dashed_container.setObjectName("emptyStateContainer")
        dashed_layout = QVBoxLayout(dashed_container)
        dashed_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dashed_layout.setContentsMargins(48, 48, 48, 48)
        dashed_layout.setSpacing(16)

        # Icon container with border
        icon_container = QFrame(parent=dashed_container)
        icon_container.setObjectName("iconContainer")
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(16, 16, 16, 16)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_icon = QLabel("🖼️", parent=icon_container)
        empty_icon.setObjectName("largeIcon")
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(empty_icon)
        dashed_layout.addWidget(icon_container, alignment=Qt.AlignmentFlag.AlignCenter)

        empty_title = QLabel("Select Input Image", parent=dashed_container)
        empty_title.setObjectName("sectionHeaderLarge")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dashed_layout.addWidget(empty_title)

        btn_open_img = QPushButton("Open an Image", parent=dashed_container)
        btn_open_img.setObjectName("primaryButton")
        btn_open_img.setFixedWidth(240)
        btn_open_img.clicked.connect(self.action_open_image)
        dashed_layout.addWidget(btn_open_img, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_open_folder = QPushButton("Open a Folder", parent=dashed_container)
        btn_open_folder.setObjectName("primaryButton")
        btn_open_folder.setFixedWidth(240)
        btn_open_folder.clicked.connect(self.action_open_folder)
        dashed_layout.addWidget(btn_open_folder, alignment=Qt.AlignmentFlag.AlignCenter)

        empty_subtitle = QLabel(
            "Supports JPG, PNG, TIFF & RAW formats up to 100MB",
            parent=dashed_container,
        )
        empty_subtitle.setObjectName("fileDesc")
        empty_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dashed_layout.addWidget(empty_subtitle)

        overlay_layout.addWidget(
            dashed_container, stretch=0, alignment=Qt.AlignmentFlag.AlignCenter
        )
        canvas_layout.addWidget(self.empty_overlay, stretch=1)
        self.empty_overlay.raise_()  # Keep on top

        self.splitter.addWidget(self.canvas_container)

        # === RIGHT PANEL: Unified Right Panel ===
        self.right_panel = UnifiedRightPanel(parent=self.splitter)
        self.splitter.addWidget(self.right_panel)

        # Set stretch factors (center gets more space)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 0)

        content_layout.addWidget(self.splitter)
        self.main_layout.addWidget(self.content_container)

        # Initialize with empty state
        self._update_empty_state()

    def setup_controllers(self):
        """Initialize controllers."""
        # Image controller - manages image loading
        self.image_controller = ImageNavigationController(self.image_model, self)

        # Pipeline controller - manages pipeline operations
        self.pipeline_controller = PipelineController()

    def wire_signals(self):
        """Wire up all signal/slot connections."""
        # Image model -> UI updates
        # (Handled by image controller calling our methods)

        # Pipeline stack signals -> Controller
        self.pipeline_stack.add_step_requested.connect(self.handle_add_step)
        self.pipeline_stack.toggle_node.connect(self.handle_toggle_node)
        self.pipeline_stack.delete_node.connect(self.handle_delete_node)
        self.pipeline_stack.node_reordered.connect(self.handle_node_reordered)
        self.pipeline_stack.run_pipeline.connect(self.handle_run_pipeline)
        self.pipeline_stack.node_selected.connect(self.handle_node_selected)

        # Right panel signals
        self.right_panel.node_param_changed.connect(self.handle_node_param_changed)
        self.right_panel.file_selected.connect(
            self.image_controller.handle_file_selected
        )

    def _update_empty_state(self):
        """Update UI based on whether an image is loaded."""
        has_image = self.current_image_path is not None

        # Toggle overlay visibility
        self.empty_overlay.setVisible(not has_image)

        # Enable/disable add button
        if self.pipeline_stack.add_button:
            self.pipeline_stack.add_button.setEnabled(has_image)
            if has_image:
                self.pipeline_stack.add_button.setToolTip("")
            else:
                self.pipeline_stack.add_button.setToolTip("Load an image first")

        # Update right panel
        if not has_image:
            self.right_panel.clear()

    # === Image Navigation Handlers ===

    def action_open_image(self):
        """Open single image dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input Image", "", "Images (*.png *.jpg *.jpeg *.tif *.tiff)"
        )
        if file_path:
            self.image_controller.handle_open_single_image(file_path)
            # Hide folder explorer in single image mode
            self.right_panel.set_folder_explorer_visible(False)
            # Create single image input node in pipeline
            self._create_single_image_node(file_path)

    def action_open_folder(self):
        """Open folder dialog."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder_path:
            self.image_controller.handle_open_folder(folder_path)
            # Show folder explorer in folder mode
            self.right_panel.set_folder_explorer_visible(True)

    def toggle_pan_mode(self, checked):
        """Toggle canvas pan mode."""
        if checked:
            self.btn_pan.setObjectName("toolBtnActive")
        else:
            self.btn_pan.setObjectName("toolBtn")

        # Force stylesheet update
        self.btn_pan.setStyleSheet(self.btn_pan.styleSheet())

        self.image_canvas.set_pan_mode(checked)

    def action_zoom_in(self):
        """Zoom in on canvas."""
        self.image_canvas.zoom_in()

    def action_zoom_out(self):
        """Zoom out on canvas."""
        self.image_canvas.zoom_out()

    # === Pipeline Handlers ===

    def handle_add_step(self, step_type):
        """Add a new pipeline step."""
        # Create a new node
        import uuid

        node = PipelineNode(
            id=str(uuid.uuid4()),
            type=step_type,
            name=step_type.replace("_", " ").title(),
            description=step_type.replace("_", " ").title(),
            icon="⚙️",
            status="idle",
            enabled=True,
            parameters={},
        )
        self.pipeline_controller.add_node(node)

        # Update the pipeline stack view
        self._refresh_pipeline_view()

    def _create_single_image_node(self, file_path: str):
        """Create a single image input node in the pipeline.

        Args:
            file_path: Path to the selected image file
        """
        import os
        import uuid

        # Remove any existing input nodes to avoid duplicates
        existing_input = None
        for node in self.pipeline_controller.pipeline.nodes:
            if node.type == "input_single_image":
                existing_input = node
                break

        if existing_input:
            self.pipeline_controller.remove_node(existing_input.id)

        # Create new input node
        filename = os.path.basename(file_path)
        node = PipelineNode(
            id=str(uuid.uuid4()),
            type="input_single_image",
            name="Single Image",
            description=f"Input: {filename}",
            icon="🖼️",
            status="idle",
            enabled=True,
            parameters={"file_path": file_path},
        )
        self.pipeline_controller.add_node(node)

        # Update the pipeline stack view
        self._refresh_pipeline_view()

    def handle_toggle_node(self, node_id, enabled):
        """Toggle node enabled state."""
        self.pipeline_controller.toggle_node(node_id, enabled)

    def handle_delete_node(self, node_id):
        """Delete a node."""
        self.pipeline_controller.remove_node(node_id)
        self._refresh_pipeline_view()

        # If we deleted the selected node, show metadata
        self.right_panel.show_metadata(self._get_current_metadata())

    def handle_node_reordered(self, new_order):
        """Handle node reordering."""
        # Reorder pipeline nodes based on new order
        id_to_node = {n.id: n for n in self.pipeline_controller.pipeline.nodes}
        reordered = [id_to_node[nid] for nid in new_order if nid in id_to_node]
        self.pipeline_controller.pipeline.nodes = reordered
        self.pipeline_controller.pipeline_changed.emit()

    def handle_node_selected(self, node_data):
        """Handle node selection - show properties."""
        self.right_panel.show_properties(node_data, self.available_nodes)

    def handle_node_param_changed(self, node_id, param_name, value):
        """Handle parameter change from properties panel and auto-save."""
        self.pipeline_controller.update_node_params(node_id, {param_name: value})

    def handle_run_pipeline(self):
        """Handle run pipeline button click."""
        self._execute_pipeline()

    def _refresh_pipeline_view(self):
        """Refresh the pipeline stack view from controller."""
        pipeline_data = {
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type,
                    "name": n.name,
                    "description": n.description,
                    "enabled": n.enabled,
                    "icon": n.icon or "⚙️",
                    "parameters": n.parameters,
                }
                for n in self.pipeline_controller.pipeline.nodes
            ]
        }
        self.pipeline_stack.set_pipeline(pipeline_data)

    def _execute_pipeline(self):
        """Execute the pipeline on the current image and update canvas.

        This is called when parameters are applied to refresh the preview.
        """
        if not self.current_image_path:
            return

        # TODO: Implement full pipeline execution
        # For now, just reload the original image to canvas
        # In a full implementation, this would:
        # 1. Load the image
        # 2. Run through pipeline nodes
        # 3. Update canvas with processed result
        self.image_canvas.load_image(self.current_image_path)

        # Emit signal for any listeners
        # self.pipeline_executed.emit()

    def _get_current_metadata(self):
        """Get metadata for currently loaded image."""
        if not self.current_image_path:
            return None

        return {
            "filename": os.path.basename(self.current_image_path),
            "subtitle": "Source Input",
            "dimensions": self._get_image_dimensions(),
            "bitdepth": "8-bit",
            "channels": "RGB (3)",
            "filesize": self._get_file_size_formatted(),
        }

    def _get_image_dimensions(self):
        """Get dimensions of current image."""
        if not self.current_image_path:
            return "-"

        from PyQt6.QtGui import QImageReader

        reader = QImageReader(self.current_image_path)
        size = reader.size()
        if size.isValid():
            return f"{size.width()} x {size.height()}"
        return "Unknown"

    def _get_file_size_formatted(self):
        """Get formatted file size."""
        if not self.current_image_path:
            return "-"

        try:
            size_bytes = os.path.getsize(self.current_image_path)
            for unit in ["B", "KB", "MB", "GB"]:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
        except:
            return "-"

    # === Public Methods for Controller ===

    def set_mode(self, mode):
        """Set the application mode (called by ImageNavigationController)."""
        # Update internal state if needed
        pass

    def update_file_list(self, files):
        """Update file list in right panel folder explorer."""
        self.right_panel.update_file_list(files)

    def update_metadata_display(
        self, filename, subtitle, dimensions, bitdepth, channels, filesize
    ):
        """Update metadata display (called by ImageNavigationController)."""
        metadata = {
            "filename": filename,
            "subtitle": subtitle,
            "dimensions": dimensions,
            "bitdepth": bitdepth,
            "channels": channels,
            "filesize": filesize,
        }
        self.right_panel.show_metadata(metadata)

    def load_image_to_canvas(self, filepath):
        """Load image to canvas (called by ImageNavigationController)."""
        self.current_image_path = filepath
        self.image_canvas.load_image(filepath)
        self._update_empty_state()

        # Update metadata
        metadata = self._get_current_metadata()
        if metadata:
            self.right_panel.show_metadata(metadata)

    def apply_styles(self):
        """Apply application-wide styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121415;
            }
            QWidget {
                background-color: #121415;
                color: #E8EAED;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            #AppHeader {
                background-color: #121415;
                border-bottom: 1px solid #2D3336;
            }
            #appTitle {
                color: #E8EAED;
                font-size: 16px;
                font-weight: 600;
            }
            #appLogo {
                font-size: 20px;
            }
            #appAvatar {
                background-color: #2D3336;
                border-radius: 16px;
            }
            #leftPanel {
                background-color: #121415;
                border-right: 1px solid #2D3336;
                min-width: 280px;
                max-width: 350px;
            }
            #rightPanel {
                background-color: #121415;
                border-left: 1px solid #2D3336;
                min-width: 280px;
                max-width: 350px;
            }
            #canvasArea {
                background-color: #0d0f10;
            }
            #panelHeader {
                color: #9AA0A6;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            #sectionHeader {
                color: #E8EAED;
                font-size: 14px;
                font-weight: bold;
            }
            #sectionHeaderLarge {
                color: #E8EAED;
                font-size: 20px;
                font-weight: 600;
                margin: 16px 0;
            }
            #primaryButton {
                background-color: #00B884;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                margin: 8px 0;
            }
            #primaryButton:hover {
                background-color: #00D69A;
            }
            #floatingToolbar {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                border-radius: 8px;
            }
            #toolBtn {
                background-color: transparent;
                color: #E8EAED;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 14px;
            }
            #toolBtn:hover {
                background-color: #2D3336;
            }
            #toolBtnActive {
                background-color: #00B884;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 14px;
            }
            #toolLabel {
                color: #9AA0A6;
                font-size: 12px;
            }
            #largeIcon {
                font-size: 48px;
            }
            #fileDesc {
                color: #9AA0A6;
                font-size: 13px;
                margin-top: 8px;
            }
            #emptyOverlay {
                background-color: transparent;
            }
            #emptyStateContainer {
                background-color: #15181a;
                border: 2px dashed #3a3f44;
                border-radius: 12px;
            }
            #iconContainer {
                background-color: #1a1f22;
                border: 1px solid #2a2e33;
                border-radius: 8px;
                min-width: 64px;
                min-height: 64px;
            }
            #fileList {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                border-radius: 4px;
                outline: none;
            }
            #fileList::item {
                color: #E8EAED;
                padding: 8px 12px;
                border: 2px solid transparent;
                border-radius: 4px;
            }
            #fileList::item:selected {
                background-color: #00B884;
                border: 2px solid #00d69a;
                color: #121415;
            }
            #fileList::item:hover {
                background-color: #2D3336;
            }
            #fileList::item:selected:hover {
                background-color: #00B884;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
