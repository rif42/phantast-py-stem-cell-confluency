import logging
from typing import Optional, Callable

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QLabel,
    QStackedWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..controllers.main_controller import MainController
from ..models.app_state import WorkflowPhase
from .image_canvas import ImageCanvas
from .properties_panel import PropertiesPanel


logger = logging.getLogger(__name__)


class UnifiedMainWidget(QWidget):
    """
    Unified main widget with 3-panel adaptive layout.

    Layout:
    - Left: Pipeline stack (hidden in EMPTY phase)
    - Center: ImageCanvas (always visible)
    - Right: Properties panel (adapts to selection)
    """

    # Forwarded signals
    node_selected = pyqtSignal(str)  # node_id
    node_double_clicked = pyqtSignal(str)  # node_id

    def __init__(self, controller: MainController, parent=None):
        super().__init__(parent)

        self.controller = controller

        # Panel state
        self._left_panel_visible = False
        self._right_panel_visible = False

        self._setup_ui()
        self._connect_signals()

        logger.info("UnifiedMainWidget initialized")

    def _setup_ui(self):
        """Setup the 3-panel UI."""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Main splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # === LEFT PANEL (Pipeline Stack) ===
        self.left_panel_container = QWidget()
        self.left_panel_layout = QVBoxLayout(self.left_panel_container)
        self.left_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.left_panel_layout.setSpacing(0)

        # Stacked widget for left panel states
        self.left_stack = QStackedWidget()
        self.left_panel_layout.addWidget(self.left_stack)

        # Page 0: Hidden/Empty placeholder
        self.left_empty_widget = self._create_empty_placeholder("Pipeline")
        self.left_stack.addWidget(self.left_empty_widget)

        # Page 1: Pipeline stack (will be set later)
        self.pipeline_widget: Optional[QWidget] = None

        # Initially hidden
        self.left_panel_container.setVisible(False)
        self.splitter.addWidget(self.left_panel_container)

        # === CENTER PANEL (Image Canvas) ===
        self.center_panel = QWidget()
        self.center_layout = QVBoxLayout(self.center_panel)
        self.center_layout.setContentsMargins(0, 0, 0, 0)

        # Image canvas
        self.canvas = ImageCanvas(self.center_panel)
        self.center_layout.addWidget(self.canvas)

        self.splitter.addWidget(self.center_panel)

        # === RIGHT PANEL (Properties) ===
        self.right_panel_container = QWidget()
        self.right_panel_layout = QVBoxLayout(self.right_panel_container)
        self.right_panel_layout.setContentsMargins(0, 0, 0, 0)

        # Stacked widget for right panel states
        self.right_stack = QStackedWidget()
        self.right_panel_layout.addWidget(self.right_stack)

        # Page 0: Empty/Hidden placeholder
        self.right_empty_widget = self._create_empty_placeholder("Properties")
        self.right_stack.addWidget(self.right_empty_widget)

        # Page 1: Image properties (metadata)
        self.properties_panel = PropertiesPanel()
        self.right_stack.addWidget(self.properties_panel)

        # Page 2: Node properties editor (will be set later)
        self.node_properties_widget: Optional[QWidget] = None

        # Initially show properties panel
        self.right_stack.setCurrentIndex(1)  # Show properties
        self.splitter.addWidget(self.right_panel_container)

        # Set splitter sizes (proportions)
        self.splitter.setSizes([250, 700, 300])

        # Set stretch factors
        self.splitter.setStretchFactor(0, 0)  # Left: fixed
        self.splitter.setStretchFactor(1, 1)  # Center: expands
        self.splitter.setStretchFactor(2, 0)  # Right: fixed

    def _create_empty_placeholder(self, name: str) -> QWidget:
        """Create a placeholder widget for hidden panels."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)

        label = QLabel(f"{name}\n(No content)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #5A6066; font-size: 12px;")
        layout.addWidget(label)
        layout.addStretch()

        return widget

    def _connect_signals(self):
        """Connect to controller signals."""
        # Phase changes
        self.controller.phase_changed.connect(self._on_phase_changed)

        # Image operations
        self.controller.image_loaded.connect(self._on_image_loaded)
        self.controller.image_cleared.connect(self._on_image_cleared)

        # Pipeline operations
        self.controller.pipeline_changed.connect(self._on_pipeline_changed)
        self.controller.node_selected.connect(self._on_node_selected)

        # Preview execution
        self.controller.preview_image_ready.connect(self._on_preview_image_ready)

        # Canvas zoom
        self.canvas.zoom_changed.connect(self._on_zoom_changed)

        # Properties panel file selection
        self.properties_panel.file_selected.connect(self._on_file_selected_from_panel)

    # =========================================================================
    # Signal Handlers
    # =========================================================================

    def _on_phase_changed(self, phase: WorkflowPhase):
        """Handle workflow phase change."""
        logger.debug(f"Phase changed to {phase}")

        if phase == WorkflowPhase.EMPTY:
            # Hide left panel, show properties panel
            self._show_left_panel(False)
            self._show_right_panel_content(1)  # Properties

        elif phase == WorkflowPhase.IMAGE_LOADED:
            # Show left panel (pipeline), show properties
            self._show_left_panel(True)
            self._show_right_panel_content(1)  # Properties
            self._update_properties_from_image()

    def _on_image_loaded(self, filepath: str):
        """Handle image loaded."""
        self.canvas.load_image(filepath)
        self._update_properties_from_image()

    def _on_file_selected_from_panel(self, filename: str):
        """Handle file selection from properties panel folder explorer."""
        if not self.controller.has_image:
            return

        image = self.controller.state.current_image
        if not image or getattr(image, "mode", "") != "FOLDER":
            return

        # Set active image in model
        try:
            image.set_active_image(filename)
            # Update canvas
            if image.active_image:
                self.canvas.load_image(image.active_image["filepath"])
                # Update properties
                self._update_properties_from_image()
        except Exception as e:
            logger.error(f"Error selecting file: {e}")

    def _on_image_cleared(self):
        """Handle image cleared."""
        # Clear canvas
        self.canvas.clear_image()
        self.properties_panel.update_metadata()  # Reset to empty

    def _on_pipeline_changed(self):
        """Handle pipeline structure change."""
        # Update left panel if needed
        pass  # Will be handled by PipelineWidget

    def _on_node_selected(self, node_id: Optional[str]):
        """Handle node selection change."""
        if node_id is None:
            # Show image properties
            self._show_right_panel_content(1)  # Properties
        else:
            # Show node properties
            self._show_node_properties(node_id)

    def _on_zoom_changed(self, percentage: int):
        """Handle canvas zoom change."""
        # Could update status bar here
        pass

    def _on_preview_image_ready(self, image):
        """Handle preview image ready from pipeline execution."""
        import numpy as np
        from PyQt6.QtGui import QImage, QPixmap

        if image is None:
            return

        try:
            # Convert numpy array to QPixmap and display
            if len(image.shape) == 2:
                # Grayscale
                height, width = image.shape
                bytes_per_line = width
                q_image = QImage(
                    image.data,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format.Format_Grayscale8,
                )
            elif len(image.shape) == 3:
                # Color (RGB)
                height, width, channels = image.shape
                if channels == 3:
                    bytes_per_line = 3 * width
                    q_image = QImage(
                        image.data,
                        width,
                        height,
                        bytes_per_line,
                        QImage.Format.Format_RGB888,
                    )
                elif channels == 4:
                    bytes_per_line = 4 * width
                    q_image = QImage(
                        image.data,
                        width,
                        height,
                        bytes_per_line,
                        QImage.Format.Format_RGBA8888,
                    )
                else:
                    logger.warning(f"Unsupported channel count: {channels}")
                    return
            else:
                logger.warning(f"Unsupported image shape: {image.shape}")
                return

            pixmap = QPixmap.fromImage(q_image)
            self.canvas.display_image(pixmap)
            logger.debug("Preview image displayed on canvas")

        except Exception as e:
            logger.error(f"Failed to display preview image: {e}")

    # =========================================================================
    # Panel Visibility
    # =========================================================================

    def _show_left_panel(self, visible: bool):
        """Show or hide left panel."""
        self.left_panel_container.setVisible(visible)
        self._left_panel_visible = visible

        if visible and self.pipeline_widget:
            self.left_stack.setCurrentWidget(self.pipeline_widget)

    def _show_right_panel_content(self, index: int):
        """Switch right panel content."""
        self.right_stack.setCurrentIndex(index)
        self._right_panel_visible = index > 0

    def _show_node_properties(self, node_id: str):
        """Show properties for selected node."""
        # For now, just show the properties panel
        # In Wave 4, this will show the node editor
        self._show_right_panel_content(1)

    # =========================================================================
    # Properties Update
    # =========================================================================

    def _update_properties_from_image(self):
        """Update properties panel from current image."""
        if not self.controller.has_image:
            self.properties_panel.update_metadata()
            return

        image = self.controller.state.current_image
        if image is None:
            self.properties_panel.update_metadata()
            return

        mode = getattr(image, "mode", "EMPTY")

        if mode == "SINGLE":
            active_image = getattr(image, "active_image", {}) or {}
            metadata = getattr(image, "metadata", {}) or {}
            self.properties_panel.update_metadata(
                filename=active_image.get("filename", "-"),
                subtitle="Single Image",
                dimensions=metadata.get("dimensions", "-"),
                bitdepth=metadata.get("bit_depth", "-"),
                channels=metadata.get("channels", "-"),
                filesize=metadata.get("file_size", "-"),
            )
        elif mode == "FOLDER":
            current_folder = getattr(image, "current_folder", "") or ""
            files = getattr(image, "files", []) or []
            active_image = getattr(image, "active_image", {}) or {}
            folder_name = (
                current_folder.split("/")[-1]
                if "/" in current_folder
                else current_folder
            )

            # Update metadata
            metadata = getattr(image, "metadata", {}) or {}
            self.properties_panel.update_metadata(
                filename=active_image.get("filename", folder_name),
                subtitle=f"{len(files)} images",
                dimensions=metadata.get("dimensions", "-"),
                bitdepth=metadata.get("bit_depth", "-"),
                channels=metadata.get("channels", "-"),
                filesize=metadata.get("file_size", "-"),
            )

            # Update file list
            self.properties_panel.update_file_list(files, current_folder)

            # Set active file
            if active_image:
                self.properties_panel.set_active_file(active_image.get("filename", ""))
        else:
            self.properties_panel.update_metadata()

    # =========================================================================
    # Public API
    # =========================================================================

    def set_pipeline_widget(self, widget: QWidget):
        """Set the pipeline widget for left panel."""
        if self.pipeline_widget:
            self.left_stack.removeWidget(self.pipeline_widget)

        self.pipeline_widget = widget
        self.left_stack.addWidget(widget)

        if self._left_panel_visible:
            self.left_stack.setCurrentWidget(widget)

    def set_node_properties_widget(self, widget: QWidget):
        """Set the node properties widget for right panel."""
        if self.node_properties_widget:
            self.right_stack.removeWidget(self.node_properties_widget)

        self.node_properties_widget = widget
        self.right_stack.addWidget(widget)

    def show_node_properties(self, node_id: str):
        """Show properties for a specific node."""
        self._show_node_properties(node_id)

    def show_image_properties(self):
        """Show image metadata properties."""
        self._show_right_panel_content(1)
        self._update_properties_from_image()

    def get_canvas(self) -> ImageCanvas:
        """Get the image canvas."""
        return self.canvas

    def refresh(self):
        """Refresh all panels from current state."""
        self._on_phase_changed(self.controller.current_phase)
