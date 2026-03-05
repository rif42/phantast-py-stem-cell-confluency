import logging
from typing import Optional, Any
from uuid import uuid4

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from ..models.app_state import AppState, WorkflowPhase
from ..models.image_model import ImageSessionModel
from ..models.pipeline_model import PipelineNode
from ..core.parameter_schemas import (
    get_node_spec,
    create_default_node_parameters,
    get_available_processing_nodes,
)
from ..core.preview_pipeline import PreviewPipeline, PreviewResult


logger = logging.getLogger(__name__)


class MainController(QObject):
    """
    Central controller for the unified PhantastLab interface.

    Manages application state, workflow phases, and coordinates between
    UI components. All state changes flow through this controller.
    """

    # Phase transitions
    phase_changed = pyqtSignal(WorkflowPhase)  # New phase

    # Image operations
    image_loaded = pyqtSignal(str)  # filepath
    image_cleared = pyqtSignal()

    # Pipeline operations
    pipeline_changed = pyqtSignal()  # Any pipeline change
    node_added = pyqtSignal(str)  # node_id
    node_removed = pyqtSignal(str)  # node_id
    node_moved = pyqtSignal(str, int)  # node_id, new_index
    node_toggled = pyqtSignal(str, bool)  # node_id, enabled
    node_parameter_changed = pyqtSignal(str, str, Any)  # node_id, param, value

    # Selection
    node_selected = pyqtSignal(object)  # node_id (None = deselect)

    # Preview execution
    preview_requested = pyqtSignal()  # Emitted when preview should run
    preview_started = pyqtSignal()
    preview_completed = pyqtSignal(object)  # PreviewResult
    preview_image_ready = pyqtSignal(object)  # np.ndarray result image

    def __init__(self):
        super().__init__()

        self.state = AppState()
        self.preview_pipeline = PreviewPipeline()

        # Debounce timer for preview execution
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._execute_preview)

        # Connect preview pipeline signals
        self.preview_pipeline.execution_started.connect(self.preview_started.emit)
        self.preview_pipeline.execution_completed.connect(self._on_preview_completed)
        self.preview_pipeline.execution_failed.connect(self._on_preview_failed)

        logger.info("MainController initialized")

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def current_phase(self) -> WorkflowPhase:
        """Get current workflow phase."""
        return self.state.workflow_phase

    @property
    def has_image(self) -> bool:
        """Check if an image is currently loaded."""
        return self.state.current_image is not None

    @property
    def selected_node_id(self) -> Optional[str]:
        """Get ID of currently selected node."""
        return self.state.selected_node_id

    # =========================================================================
    # Phase Transitions
    # =========================================================================

    def load_image(self, filepath: str) -> bool:
        """
        Load an image and transition to IMAGE_LOADED phase.

        Args:
            filepath: Path to image file

        Returns:
            True if successful
        """
        try:
            # Create image session
            image_session = ImageSessionModel()
            image_session.set_single_image(filepath)

            # Update state
            self.state.current_image = image_session
            self.state.initialize_default_pipeline()

            # Transition phase
            success = self.state.transition_to(WorkflowPhase.IMAGE_LOADED)
            if success:
                self.phase_changed.emit(WorkflowPhase.IMAGE_LOADED)
                self.image_loaded.emit(filepath)
                self.pipeline_changed.emit()
                logger.info(f"Image loaded: {filepath}")

            return success

        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return False

    def load_folder(self, folderpath: str) -> bool:
        """
        Load a folder and transition to IMAGE_LOADED phase.

        Args:
            folderpath: Path to folder

        Returns:
            True if successful
        """
        try:
            # Create image session
            image_session = ImageSessionModel()
            image_session.set_folder(folderpath)

            # Update state
            self.state.current_image = image_session
            self.state.initialize_default_pipeline()

            # Transition phase
            success = self.state.transition_to(WorkflowPhase.IMAGE_LOADED)
            if success:
                self.phase_changed.emit(WorkflowPhase.IMAGE_LOADED)
                self.image_loaded.emit(folderpath)
                self.pipeline_changed.emit()
                logger.info(f"Folder loaded: {folderpath}")

            return success

        except Exception as e:
            logger.error(f"Failed to load folder: {e}")
            return False

    def clear_image(self) -> bool:
        """
        Clear current image and return to EMPTY phase.

        Returns:
            True if successful
        """
        success = self.state.transition_to(WorkflowPhase.EMPTY)
        if success:
            self.state.current_image = None
            self.state.pipeline.nodes = []
            self.state.clear_selection()

            self.phase_changed.emit(WorkflowPhase.EMPTY)
            self.image_cleared.emit()
            self.pipeline_changed.emit()
            self.node_selected.emit(None)
            logger.info("Image cleared")

        return success

    # =========================================================================
    # Node Operations
    # =========================================================================

    def add_node(
        self, node_type: str, after_node_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Add a new node to the pipeline.

        Args:
            node_type: Type of node to add (grayscale, gaussian_blur, clahe)
            after_node_id: Node to insert after (default: before output)

        Returns:
            ID of new node, or None if failed
        """
        if self.current_phase != WorkflowPhase.IMAGE_LOADED:
            logger.warning("Cannot add node: no image loaded")
            return None

        # Get node specification
        spec = get_node_spec(node_type)
        if spec is None:
            logger.error(f"Unknown node type: {node_type}")
            return None

        # Create node
        node_id = f"{node_type}_{uuid4().hex[:8]}"
        node = PipelineNode(
            id=node_id,
            type=node_type,
            name=spec.name,
            description=spec.description,
            icon=spec.icon,
            status="ready",
            enabled=True,
            parameters=create_default_node_parameters(node_type),
        )

        # Add to pipeline
        if after_node_id:
            success = self.state.insert_node_between(node, after_node_id)
        else:
            success = self.state.add_node(node)

        if success:
            self.node_added.emit(node_id)
            self.pipeline_changed.emit()
            self._trigger_preview_debounce()
            logger.info(f"Node added: {node_id} ({node_type})")
            return node_id

        return None

    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the pipeline.

        Args:
            node_id: ID of node to remove

        Returns:
            True if removed successfully
        """
        success = self.state.remove_node(node_id)

        if success:
            self.node_removed.emit(node_id)
            self.pipeline_changed.emit()
            self._trigger_preview_debounce()
            logger.info(f"Node removed: {node_id}")

        return success

    def move_node(self, node_id: str, new_index: int) -> bool:
        """
        Move a node to a new position.

        Args:
            node_id: ID of node to move
            new_index: Target index

        Returns:
            True if moved successfully
        """
        success = self.state.move_node(node_id, new_index)

        if success:
            self.node_moved.emit(node_id, new_index)
            self.pipeline_changed.emit()
            self._trigger_preview_debounce()
            logger.info(f"Node moved: {node_id} to index {new_index}")

        return success

    def toggle_node(self, node_id: str) -> Optional[bool]:
        """
        Toggle node enabled state.

        Args:
            node_id: ID of node to toggle

        Returns:
            New enabled state, or None if failed
        """
        result = self.state.toggle_node(node_id)

        if result is not None:
            self.node_toggled.emit(node_id, result)
            self.pipeline_changed.emit()
            self._trigger_preview_debounce()
            logger.info(f"Node toggled: {node_id} = {result}")

        return result

    def set_node_enabled(self, node_id: str, enabled: bool) -> bool:
        """
        Set node enabled state explicitly.

        Args:
            node_id: ID of node
            enabled: New enabled state

        Returns:
            True if changed successfully
        """
        success = self.state.set_node_enabled(node_id, enabled)

        if success:
            self.node_toggled.emit(node_id, enabled)
            self.pipeline_changed.emit()
            self._trigger_preview_debounce()
            logger.info(f"Node enabled set: {node_id} = {enabled}")

        return success

    def update_node_parameter(self, node_id: str, param_name: str, value: Any) -> bool:
        """
        Update a node parameter.

        Args:
            node_id: ID of node
            param_name: Parameter name
            value: New value

        Returns:
            True if updated successfully
        """
        success = self.state.update_node_parameter(node_id, param_name, value)

        if success:
            self.node_parameter_changed.emit(node_id, param_name, value)
            self.pipeline_changed.emit()
            self._trigger_preview_debounce()
            logger.debug(f"Parameter updated: {node_id}.{param_name} = {value}")

        return success

    # =========================================================================
    # Selection
    # =========================================================================

    def select_node(self, node_id: Optional[str]) -> bool:
        """
        Select a node (or clear selection).

        Args:
            node_id: Node ID to select, or None to clear

        Returns:
            True if selection changed
        """
        changed = self.state.select_node(node_id)

        if changed:
            self.node_selected.emit(node_id)
            logger.debug(f"Node selected: {node_id}")

        return changed

    def clear_selection(self) -> bool:
        """Clear node selection."""
        return self.select_node(None)

    # =========================================================================
    # Preview Execution
    # =========================================================================

    def _trigger_preview_debounce(self):
        """Trigger preview execution with 200ms debounce."""
        self._preview_timer.stop()
        self._preview_timer.start(200)
        logger.debug("Preview debounce triggered")

    def _execute_preview(self):
        """
        Execute pipeline preview on current image.

        Runs the pipeline through all enabled nodes and emits the result.
        """
        if not self.has_image:
            logger.debug("Cannot execute preview: no image loaded")
            return

        # Get the current image
        image = self.state.current_image
        if image is None or image.mode != "SINGLE":
            logger.debug("Cannot execute preview: no single image loaded")
            return

        # Get image data
        img_data = image.active_image.get("data")
        if img_data is None:
            logger.error("Cannot execute preview: image data not available")
            return

        # Execute preview
        self.preview_requested.emit()
        result = self.preview_pipeline.execute(img_data, self.state)

        # Result will be emitted through signals
        logger.debug(f"Preview execution completed: success={result.success}")

    def _on_preview_completed(self, result: PreviewResult):
        """Handle preview completion."""
        if result.success and result.image is not None:
            self.preview_image_ready.emit(result.image)
            self.preview_completed.emit(result)
            logger.info(f"Preview completed in {result.execution_time_ms:.1f}ms")
        else:
            logger.error(f"Preview failed: {result.error_message}")

    def _on_preview_failed(self, error_message: str):
        """Handle preview failure."""
        logger.error(f"Preview execution failed: {error_message}")

    def request_immediate_preview(self):
        """Request immediate preview (bypass debounce)."""
        self._preview_timer.stop()
        self._execute_preview()

    # =========================================================================
    # Utility
    # =========================================================================

    def get_available_node_types(self) -> list:
        """Get list of available node types for UI."""
        return get_available_processing_nodes()

    def get_node_info(self, node_id: str) -> Optional[dict]:
        """Get information about a node."""
        node = self.state.get_node(node_id)
        if node is None:
            return None

        return {
            "id": node.id,
            "type": node.type,
            "name": node.name,
            "description": node.description,
            "enabled": node.enabled,
            "parameters": node.parameters.copy(),
            "is_fixed": node.type in ("input", "output"),
        }

    def is_node_fixed(self, node_id: str) -> bool:
        """Check if a node is fixed (input/output)."""
        node = self.state.get_node(node_id)
        if node is None:
            return False
        return node.type in ("input", "output")
