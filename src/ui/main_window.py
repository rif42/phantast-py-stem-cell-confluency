"""Main Window - Combined Image Navigation and Pipeline Construction."""

import sys
import os
import logging
from typing import Optional

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
    QProgressBar,
    QMessageBox,
    QStatusBar,
    QDialog,
)
from PyQt6.QtCore import Qt, QObject, QThread, QTimer, pyqtSignal

# Models
from src.models.image_model import ImageSessionModel
from src.models.pipeline_model import Pipeline, PipelineNode

# Views
from src.ui.pipeline_stack_widget import PipelineStackWidget
from src.ui.image_canvas import ImageCanvas
from src.ui.comparison_controls import ComparisonControls
from src.ui.unified_right_panel import UnifiedRightPanel

# Controllers
from src.controllers.image_controller import ImageNavigationController
from src.controllers.pipeline_controller import PipelineController
from src.core.steps import STEP_REGISTRY
from src.core.pipeline_worker import PipelineWorker


logger = logging.getLogger(__name__)


class PipelineExecutor(QObject):
    """Manage PipelineWorker lifecycle and background thread cleanup."""

    started = pyqtSignal()
    progress = pyqtSignal(str, int)
    step_completed = pyqtSignal(str, object)
    mask_saved = pyqtSignal(str, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    execute_requested = pyqtSignal(str, str, object, object)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._thread = None
        self._worker = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.isRunning()

    def start(self, input_path: str, output_path: str, nodes, step_registry) -> bool:
        """Start background pipeline execution.

        Returns:
            True if execution started, otherwise False.
        """
        if self.is_running():
            return False

        self._thread = QThread(parent=self)
        self._worker = PipelineWorker()
        worker = self._worker
        worker.moveToThread(self._thread)

        self._thread.started.connect(
            lambda: self.execute_requested.emit(
                input_path,
                output_path,
                list(nodes),
                step_registry,
            )
        )
        # Marshal worker input via a signal so `process_pipeline` runs on the worker thread.
        self.execute_requested.connect(worker.process_pipeline)

        worker.started.connect(self.started.emit)
        worker.progress.connect(self.progress.emit)
        worker.step_completed.connect(self.step_completed.emit)
        worker.mask_saved.connect(self.mask_saved.emit)
        worker.finished.connect(self.finished.emit)
        worker.error.connect(self.error.emit)

        worker.finished.connect(self._finalize)
        worker.error.connect(self._finalize)

        self._thread.start()
        return True

    def _finalize(self, _payload=None):
        """Stop and clean up worker thread resources."""
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait(3000)
            self._thread.deleteLater()
            self._thread = None

        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None


class ProcessingDialog(QDialog):
    """Modal dialog shown during pipeline processing."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spinner_label = QLabel("🔬", parent=self)
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(self.spinner_label)

        self.text_label = QLabel("Processing...", parent=self)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet("font-size: 16px; color: #E8EAED;")
        layout.addWidget(self.text_label)

        if parent is not None:
            self.move(parent.frameGeometry().center() - self.rect().center())


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
        self._original_image_path: Optional[str] = None
        self._processed_image_path: Optional[str] = None
        self._mask_image_path: Optional[str] = None
        self._batch_input_snapshot: list[str] = []
        self._batch_queue: list[str] = []
        self._batch_current_index: int = -1
        self._batch_success_count: int = 0
        self._batch_failure_count: int = 0
        self.processing_dialog: Optional[ProcessingDialog] = None

        # Core Container
        self.main_container = QWidget(parent=self)
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        self.setup_header()
        self.setup_models()
        self.setup_ui_components()
        self.setup_status_bar()
        self.setup_controllers()
        self.wire_signals()
        self.apply_styles()

    def setup_status_bar(self):
        """Create status bar widgets for pipeline processing feedback."""
        status_bar = self.statusBar()
        if status_bar is None:
            status_bar = QStatusBar(parent=self)
            self.setStatusBar(status_bar)
        status_bar.setSizeGripEnabled(False)

        self.status_label = QLabel("Ready", parent=status_bar)
        self.status_progress = QProgressBar(parent=status_bar)
        self.status_progress.setRange(0, 100)
        self.status_progress.setValue(0)
        self.status_progress.setFixedWidth(220)
        self.status_progress.setVisible(False)

        status_bar.addWidget(self.status_label)
        status_bar.addPermanentWidget(self.status_progress)

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
        self.center_layout = QVBoxLayout(self.canvas_container)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)

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

        self.center_layout.addWidget(toolbar_container)

        # Image canvas
        self.image_canvas = ImageCanvas(parent=self.canvas_container)
        self.image_canvas.setObjectName("canvasImage")
        self.image_canvas.zoom_changed.connect(
            lambda pct: self.lbl_zoom.setText(f"{pct}%")
        )
        self.center_layout.addWidget(self.image_canvas)

        self.comparison_controls = ComparisonControls(parent=self.canvas_container)
        self.comparison_controls.hide()
        self.comparison_controls.view_mode_changed.connect(self._on_view_mode_changed)
        self.comparison_controls.mask_visibility_changed.connect(
            self._on_mask_visibility_changed
        )
        self.center_layout.addWidget(self.comparison_controls)

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
        self.center_layout.addWidget(self.empty_overlay, stretch=1)
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

        # Pipeline executor - manages async worker/thread lifecycle
        self.pipeline_executor = PipelineExecutor(parent=self)

    def wire_signals(self):
        """Wire up all signal/slot connections."""
        # Image model -> UI updates
        # (Handled by image controller calling our methods)

        # Pipeline stack signals -> Controller
        self.pipeline_stack.add_step_requested.connect(self.handle_add_step)
        self.pipeline_stack.toggle_node.connect(self.handle_toggle_node)
        self.pipeline_stack.delete_node.connect(self.handle_delete_node)
        self.pipeline_stack.node_reordered.connect(self.handle_node_reordered)
        self.pipeline_stack.node_selected.connect(self.handle_node_selected)
        self.pipeline_stack.run_pipeline.connect(self.handle_run_pipeline)

        # Pipeline executor signals -> UI updates
        self.pipeline_executor.started.connect(self._handle_pipeline_started)
        self.pipeline_executor.progress.connect(self._handle_pipeline_progress)
        self.pipeline_executor.step_completed.connect(self._handle_step_completed)
        self.pipeline_executor.mask_saved.connect(self._on_mask_saved)
        self.pipeline_executor.finished.connect(self._handle_pipeline_finished)
        self.pipeline_executor.error.connect(self._handle_pipeline_error)

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

        self._update_run_button_state()

        # Update right panel
        if not has_image:
            self.right_panel.clear()

    @staticmethod
    def _is_generated_artifact_filename(filename: str) -> bool:
        """Return True when a file name matches generated output artifacts."""
        lowered = filename.lower()
        return "_processed" in lowered or "_mask" in lowered

    def _collect_folder_batch_input_snapshot(
        self, folder_path: Optional[str] = None
    ) -> list[str]:
        """Collect deterministic, filtered folder-mode inputs as absolute paths."""
        selected_folder = folder_path or self.image_model.current_folder
        if not selected_folder:
            return []

        absolute_folder = os.path.abspath(selected_folder)
        if not os.path.isdir(absolute_folder):
            return []

        valid_extensions = tuple(
            ext.lower()
            for ext in getattr(
                self.image_model,
                "valid_extensions",
                (".png", ".jpg", ".jpeg", ".tif", ".tiff"),
            )
        )

        snapshot: list[str] = []
        for filename in sorted(
            list(self.image_model.files), key=lambda value: str(value).lower()
        ):
            if not isinstance(filename, str):
                continue

            lowered_name = filename.lower()
            if not lowered_name.endswith(valid_extensions):
                continue
            if self._is_generated_artifact_filename(lowered_name):
                continue

            absolute_path = os.path.abspath(os.path.join(absolute_folder, filename))
            if os.path.isfile(absolute_path):
                snapshot.append(absolute_path)

        return list(snapshot)

    @staticmethod
    def _has_enabled_executable_nodes(nodes) -> bool:
        """Return True if at least one enabled non-input node exists."""
        return any(
            node.enabled
            and node.type not in {"input_single_image", "input_image_folder"}
            for node in nodes
        )

    def _update_run_button_state(self):
        """Enable run button only when image and pipeline steps are available."""
        pipeline_controller = getattr(self, "pipeline_controller", None)
        nodes = (
            list(pipeline_controller.pipeline.nodes)
            if pipeline_controller is not None
            else []
        )
        folder_node = next(
            (node for node in nodes if node.type == "input_image_folder"),
            None,
        )

        executor = getattr(self, "pipeline_executor", None)
        is_running = executor is not None and executor.is_running()

        if folder_node is not None:
            folder_path = str(folder_node.parameters.get("folder_path", ""))
            batch_snapshot = self._collect_folder_batch_input_snapshot(folder_path)
            has_eligible_inputs = len(batch_snapshot) > 0
            has_executable_nodes = self._has_enabled_executable_nodes(nodes)
            is_enabled = has_eligible_inputs and has_executable_nodes and not is_running
            disabled_tooltip = (
                "Select a folder with eligible images and add processing steps"
            )
        else:
            has_image = self.current_image_path is not None
            has_nodes = len(nodes) > 0
            is_enabled = has_image and has_nodes and not is_running
            disabled_tooltip = "Load an image and add processing steps"

        self.pipeline_stack.run_button.setEnabled(is_enabled)
        if is_enabled:
            self.pipeline_stack.run_button.setToolTip("")
        else:
            self.pipeline_stack.run_button.setToolTip(disabled_tooltip)

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
            absolute_folder_path = os.path.abspath(folder_path)
            self.image_controller.handle_open_folder(absolute_folder_path)
            # Show folder explorer in folder mode
            self.right_panel.set_folder_explorer_visible(True)
            # Create folder input node in pipeline
            self._create_image_folder_node(absolute_folder_path)

    def _create_image_folder_node(self, folder_path: str):
        """Create an image folder input node in the pipeline.

        Args:
            folder_path: Path to the selected input folder
        """
        import uuid

        absolute_folder_path = os.path.abspath(folder_path)

        # Remove existing single-image input nodes to avoid stale inputs
        existing_single_nodes = [
            node
            for node in list(self.pipeline_controller.pipeline.nodes)
            if node.type == "input_single_image"
        ]
        for node in existing_single_nodes:
            self.pipeline_controller.remove_node(node.id)

        existing_folder_nodes = [
            node
            for node in list(self.pipeline_controller.pipeline.nodes)
            if node.type == "input_image_folder"
        ]

        if existing_folder_nodes:
            active_folder_node = existing_folder_nodes[0]
            for duplicate_node in existing_folder_nodes[1:]:
                self.pipeline_controller.remove_node(duplicate_node.id)

            active_folder_node.name = "Image Folder"
            active_folder_node.description = f"Input folder: {absolute_folder_path}"
            active_folder_node.icon = "📁"
            active_folder_node.status = "idle"
            active_folder_node.enabled = True
            active_folder_node.parameters = {"folder_path": absolute_folder_path}
            self.pipeline_controller.pipeline_changed.emit()
        else:
            node = PipelineNode(
                id=str(uuid.uuid4()),
                type="input_image_folder",
                name="Image Folder",
                description=f"Input folder: {absolute_folder_path}",
                icon="📁",
                status="idle",
                enabled=True,
                parameters={"folder_path": absolute_folder_path},
            )
            self.pipeline_controller.add_node(node)

        # Update the pipeline stack view
        self._refresh_pipeline_view()
        self._update_run_button_state()

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
        if str(step_type).lower() == "phantast":
            existing_phantast = [
                node
                for node in self.pipeline_controller.pipeline.nodes
                if str(node.type).lower() == "phantast"
            ]
            if existing_phantast:
                QMessageBox.warning(
                    self,
                    "Cannot Add Step",
                    "Only one PHANTAST node is allowed.",
                )
                return

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
        self._update_run_button_state()

    def _create_single_image_node(self, file_path: str):
        """Create a single image input node in the pipeline.

        Args:
            file_path: Path to the selected image file
        """
        import os
        import uuid

        # Remove existing folder/image input nodes to avoid stale inputs
        existing_input_nodes = [
            node
            for node in list(self.pipeline_controller.pipeline.nodes)
            if node.type in {"input_single_image", "input_image_folder"}
        ]

        for node in existing_input_nodes:
            self.pipeline_controller.remove_node(node.id)

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
        self._update_run_button_state()

    def handle_toggle_node(self, node_id, enabled):
        """Toggle node enabled state."""
        self.pipeline_controller.toggle_node(node_id, enabled)

    def handle_delete_node(self, node_id):
        """Delete a node."""
        self.pipeline_controller.remove_node(node_id)
        self._refresh_pipeline_view()
        self._update_run_button_state()

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
        """Handle node selection - show properties or folder explorer."""
        node_type = node_data.get("type", "")

        if node_type == "input_image_folder":
            # For image folder node, show folder explorer and current image metadata
            self.right_panel.set_folder_explorer_visible(True)
            self.right_panel.show_metadata(self._get_current_metadata())
        else:
            # For other nodes, show properties panel
            self.right_panel.show_properties(node_data, self.available_nodes)

    def handle_node_param_changed(self, node_id, param_name, value):
        """Handle parameter change from properties panel and auto-save."""
        self.pipeline_controller.update_node_params(node_id, {param_name: value})

    def handle_run_pipeline(self):
        """Handle run pipeline button click."""
        if self.pipeline_executor.is_running():
            return

        nodes = list(self.pipeline_controller.pipeline.nodes)
        folder_node = next(
            (node for node in nodes if node.type == "input_image_folder"),
            None,
        )

        if folder_node is not None:
            folder_path = str(folder_node.parameters.get("folder_path", ""))
            folder_snapshot = self._collect_folder_batch_input_snapshot(folder_path)
            self._batch_input_snapshot = list(folder_snapshot)

            if not self._batch_input_snapshot:
                return
            if not self._has_enabled_executable_nodes(nodes):
                return

            self._batch_queue = list(self._batch_input_snapshot)
            self._batch_current_index = 0
            self._batch_success_count = 0
            self._batch_failure_count = 0
            started = self._start_batch_item(self._batch_current_index)
            if not started:
                self._set_processing_state(False)
                self._reset_batch_run_state()
            return
        else:
            if not self.current_image_path:
                return

            input_path = os.path.abspath(self.current_image_path)
            self._batch_input_snapshot = [input_path]
            self._reset_batch_run_state()

        output_path = self._generate_output_path(input_path)
        self._set_processing_state(True, "Processing started...", 0)

        started = self.pipeline_executor.start(
            input_path,
            output_path,
            self.pipeline_controller.pipeline.nodes,
            STEP_REGISTRY,
        )
        if not started:
            self._set_processing_state(False)

    def _reset_batch_run_state(self):
        """Reset folder batch orchestration state."""
        self._batch_queue = []
        self._batch_current_index = -1
        self._batch_success_count = 0
        self._batch_failure_count = 0

    def _is_batch_run_active(self) -> bool:
        """Return True when folder batch orchestration is active."""
        return len(self._batch_queue) > 0 and 0 <= self._batch_current_index < len(
            self._batch_queue
        )

    def _start_batch_item(self, item_index: int) -> bool:
        """Start pipeline execution for a single queued batch item."""
        if item_index < 0 or item_index >= len(self._batch_queue):
            return False

        queued_input_path = os.path.abspath(self._batch_queue[item_index])
        output_path = self._generate_output_path(queued_input_path)
        total = len(self._batch_queue)
        self._set_processing_state(
            True,
            f"Processing batch item {item_index + 1}/{total}...",
            0,
        )

        return self.pipeline_executor.start(
            queued_input_path,
            output_path,
            self.pipeline_controller.pipeline.nodes,
            STEP_REGISTRY,
        )

    def _queue_next_batch_item_or_complete(self):
        """Continue with next queued item or emit aggregate completion summary."""
        if not self._is_batch_run_active():
            return

        next_index = self._batch_current_index + 1
        if next_index < len(self._batch_queue):
            self._batch_current_index = next_index
            if self.pipeline_executor.is_running():
                QTimer.singleShot(0, self._queue_next_batch_item_or_complete)
                return
            started = self._start_batch_item(self._batch_current_index)
            if not started:
                if self.pipeline_executor.is_running():
                    QTimer.singleShot(0, self._queue_next_batch_item_or_complete)
                    return
                self._batch_failure_count += 1
                QTimer.singleShot(0, self._queue_next_batch_item_or_complete)
            return

        total = len(self._batch_queue)
        success_count = self._batch_success_count
        failure_count = self._batch_failure_count
        self.status_label.setText(
            f"Batch complete: {success_count} succeeded, {failure_count} failed"
        )
        self.right_panel.show_metadata(
            {
                "filename": f"{total} item(s)",
                "subtitle": (
                    f"Batch run complete: {success_count} succeeded, {failure_count} failed"
                ),
                "dimensions": "-",
                "bitdepth": "-",
                "channels": "-",
                "filesize": "-",
            }
        )
        self._update_run_button_state()
        self._reset_batch_run_state()

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

    def _handle_pipeline_started(self):
        """Handle worker started signal in the main thread."""
        self._show_processing_dialog()

        # Cursor already set in handle_run_pipeline, just update status
        self.status_label.setText("Processing started...")
        self.status_progress.setValue(0)

    def _handle_pipeline_progress(self, step_name: str, percent: int):
        """Handle pipeline progress updates from worker thread."""
        readable_name = step_name.replace("_", " ").title()
        self.status_label.setText(f"Processing: {readable_name}...")
        self.status_progress.setValue(max(0, min(100, percent)))

    def _handle_step_completed(self, step_name: str, _result_array):
        """Handle step completion from worker thread."""
        logger.debug("Pipeline step completed: %s", step_name)

    def _handle_pipeline_finished(self, output_path: str):
        """Apply successful pipeline output and restore UI state."""
        self._close_processing_dialog()

        output_filename = os.path.basename(output_path)
        self.image_model.active_image = {
            "filename": output_filename,
            "filepath": output_path,
        }

        if (
            self.image_model.mode == "FOLDER"
            and self.image_model.current_folder
            and os.path.abspath(self.image_model.current_folder)
            == os.path.abspath(os.path.dirname(output_path))
        ):
            if output_filename not in self.image_model.files:
                self.image_model.files.append(output_filename)
                self.image_model.files.sort()
            self.update_file_list(self.image_model.files)
        else:
            self.image_model.mode = "SINGLE"
            self.image_model.current_folder = None
            self.image_model.files = []

        self.current_image_path = output_path
        self._processed_image_path = output_path
        self.image_canvas.load_image(output_path)

        if self._mask_image_path:
            self.image_canvas.set_overlay_image(self._mask_image_path)
        self.comparison_controls.show()
        self.comparison_controls.set_view_mode("processed")

        metadata = self._get_current_metadata()
        if metadata:
            self.right_panel.show_metadata(metadata)

        self.status_label.setText("Processing complete")
        self.status_progress.setValue(100)
        self._set_processing_state(False)
        self._update_run_button_state()

        if self._is_batch_run_active():
            self._batch_success_count += 1
            self._queue_next_batch_item_or_complete()

    def _handle_pipeline_error(self, error_message: str):
        """Handle worker errors and restore UI state."""
        self._close_processing_dialog()

        logger.error("Pipeline execution failed: %s", error_message)

        if self._is_batch_run_active():
            self.status_label.setText("Batch item failed; continuing...")
            self._set_processing_state(False)
            self._update_run_button_state()
            self._batch_failure_count += 1
            self._queue_next_batch_item_or_complete()
            return

        self.status_label.setText("Processing failed")
        self._set_processing_state(False)
        self._update_run_button_state()
        self.right_panel.show_metadata(
            {
                "filename": os.path.basename(self.current_image_path)
                if self.current_image_path
                else "-",
                "subtitle": "Pipeline execution failed",
                "dimensions": "-",
                "bitdepth": "-",
                "channels": "-",
                "filesize": "-",
            }
        )
        self._show_error_dialog(error_message)

    def _set_processing_state(
        self, is_processing: bool, message: Optional[str] = None, percent: int = 0
    ):
        """Update status bar, cursor, and run button during execution."""
        if is_processing:
            self.status_label.setText(message or "Processing started...")
            self.status_progress.setVisible(True)
            self.status_progress.setValue(max(0, min(100, percent)))
            self.pipeline_stack.run_button.setEnabled(False)
            self.pipeline_stack.run_button.setText("Run Pipeline")
            self.pipeline_stack.run_button.setToolTip("Pipeline is running")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            return

        self.status_progress.setVisible(False)
        self.pipeline_stack.run_button.setText("Run Pipeline")
        if QApplication.overrideCursor() is not None:
            QApplication.restoreOverrideCursor()

    def _show_error_dialog(self, message: str):
        """Show error details for failed pipeline execution."""
        QMessageBox.critical(self, "Pipeline Error", message)

    def _show_processing_dialog(self):
        """Show modal processing dialog."""
        if self.processing_dialog is not None:
            self.processing_dialog.close()
            self.processing_dialog.deleteLater()
        self.processing_dialog = ProcessingDialog(parent=self)
        self.processing_dialog.show()

    def _close_processing_dialog(self):
        """Close and clean up processing dialog if open."""
        if self.processing_dialog is not None:
            self.processing_dialog.close()
            self.processing_dialog.deleteLater()
            self.processing_dialog = None

    def _on_mask_saved(self, _source_path: str, mask_path: str):
        """Handle mask save completion from worker."""
        self._mask_image_path = mask_path
        self.comparison_controls.set_mask_available(True)
        self._restore_overlay_if_needed()

    def _on_view_mode_changed(self, mode: str):
        """Handle Original/Processed toggle."""
        if mode == "original" and self._original_image_path:
            self.current_image_path = self._original_image_path
            self.image_canvas.load_image(self._original_image_path)
            self._restore_overlay_if_needed()
        elif mode == "processed" and self._processed_image_path:
            self.current_image_path = self._processed_image_path
            self.image_canvas.load_image(self._processed_image_path)
            self._restore_overlay_if_needed()

    def _on_mask_visibility_changed(self, visible: bool):
        """Handle Show Mask toggle."""
        if visible and self._mask_image_path:
            self.image_canvas.set_overlay_image(self._mask_image_path)
        self.image_canvas.show_overlay(visible)

    def _restore_overlay_if_needed(self):
        """Restore overlay after base image changes when mask is available."""
        if not self._mask_image_path:
            return

        self.image_canvas.set_overlay_image(self._mask_image_path)
        self.image_canvas.show_overlay(self.comparison_controls.mask_toggle.isChecked())

    def _generate_output_path(self, input_path: str) -> str:
        """Generate a non-conflicting processed output path for an input image."""
        abs_input_path = os.path.abspath(input_path)
        directory = os.path.dirname(abs_input_path)

        filename = os.path.basename(abs_input_path)
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = ".png"

        base_name = name if name.endswith("_processed") else f"{name}_processed"
        counter = 1 if name.endswith("_processed") else 0

        candidate_name = base_name if counter == 0 else f"{base_name}_{counter}"
        candidate_path = os.path.abspath(
            os.path.join(directory, f"{candidate_name}{ext}")
        )

        while os.path.exists(candidate_path):
            counter = 1 if counter == 0 else counter + 1
            candidate_name = f"{base_name}_{counter}"
            candidate_path = os.path.abspath(
                os.path.join(directory, f"{candidate_name}{ext}")
            )

        return candidate_path

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
        except OSError:
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
        self._original_image_path = filepath
        self._processed_image_path = None
        self._mask_image_path = None

        self.current_image_path = filepath
        self.comparison_controls.reset()
        self.image_canvas.load_image(filepath)
        self._update_empty_state()

        # Auto-discover existing processed and mask images
        self._discover_existing_variants(filepath)

        # Update metadata
        metadata = self._get_current_metadata()
        if metadata:
            self.right_panel.show_metadata(metadata)

    def _discover_existing_variants(self, filepath: str):
        """Search for existing _processed and _mask variants of the image."""
        directory = os.path.dirname(filepath)
        basename = os.path.splitext(os.path.basename(filepath))[0]
        ext = os.path.splitext(filepath)[1].lower()

        processed_path = os.path.join(directory, f"{basename}_processed{ext}")
        mask_path = os.path.join(directory, f"{basename}_mask.png")

        found_any = False

        if os.path.exists(processed_path):
            self._processed_image_path = processed_path
            found_any = True

        if os.path.exists(mask_path):
            self._mask_image_path = mask_path
            self.image_canvas.set_overlay_image(mask_path)
            self.comparison_controls.set_mask_available(True)
            found_any = True

        if found_any:
            self.comparison_controls.show()
            if self._processed_image_path:
                self.comparison_controls.set_view_mode("processed")
                self.image_canvas.load_image(self._processed_image_path)
                self.current_image_path = self._processed_image_path
            else:
                self.comparison_controls.set_view_mode("original")

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
