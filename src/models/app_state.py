from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, Any, List

from .pipeline_model import Pipeline, PipelineNode
from .image_model import ImageSessionModel


class WorkflowPhase(Enum):
    """Application workflow phases."""

    EMPTY = auto()  # No image loaded
    IMAGE_LOADED = auto()  # Image loaded, can build pipeline


@dataclass
class AppState:
    """
    Central application state - observable by all UI components.

    This is a pure data class with no Qt dependencies for testability.
    Use AppStateManager (QObject wrapper) for signals.
    """

    # Current image session
    current_image: Optional[ImageSessionModel] = None

    # Pipeline configuration
    pipeline: Pipeline = field(default_factory=Pipeline)

    # UI selection state
    selected_node_id: Optional[str] = None

    # Workflow phase
    workflow_phase: WorkflowPhase = WorkflowPhase.EMPTY

    def can_transition_to(self, target_phase: WorkflowPhase) -> bool:
        """Check if transition to target phase is valid."""
        transitions = {
            WorkflowPhase.EMPTY: [WorkflowPhase.IMAGE_LOADED],
            WorkflowPhase.IMAGE_LOADED: [WorkflowPhase.EMPTY],
        }
        return target_phase in transitions.get(self.workflow_phase, [])

    def transition_to(self, target_phase: WorkflowPhase) -> bool:
        """
        Transition to target phase if valid.

        Returns True if transition succeeded, False otherwise.
        """
        if self.can_transition_to(target_phase):
            self.workflow_phase = target_phase
            return True
        return False

    def get_node(self, node_id: str) -> Optional[PipelineNode]:
        """Get node by ID."""
        for node in self.pipeline.nodes:
            if node.id == node_id:
                return node
        return None

    def get_selected_node(self) -> Optional[PipelineNode]:
        """Get currently selected node."""
        if self.selected_node_id:
            return self.get_node(self.selected_node_id)
        return None

    def is_node_selected(self, node_id: str) -> bool:
        """Check if given node is selected."""
        return self.selected_node_id == node_id

    def select_node(self, node_id: Optional[str]) -> bool:
        """
        Select a node by ID.

        Returns True if selection changed.
        """
        if node_id is None:
            if self.selected_node_id is not None:
                self.selected_node_id = None
                return True
            return False

        # Verify node exists
        if self.get_node(node_id):
            if self.selected_node_id != node_id:
                self.selected_node_id = node_id
                return True
        return False

    def clear_selection(self) -> bool:
        """Clear node selection. Returns True if was selected."""
        return self.select_node(None)

    def initialize_default_pipeline(self) -> None:
        """Create default pipeline with Input and Output nodes."""
        input_node = PipelineNode(
            id="input",
            type="input",
            name="Input",
            description="Input image",
            icon="📷",
            status="ready",
            enabled=True,
        )

        output_node = PipelineNode(
            id="output",
            type="output",
            name="PHANTAST",
            description="Cell detection and analysis",
            icon="🔬",
            status="ready",
            enabled=True,
        )

        self.pipeline.nodes = [input_node, output_node]
        self.pipeline.name = "Default Pipeline"

    def get_node_index(self, node_id: str) -> int:
        """Get index of node in pipeline. Returns -1 if not found."""
        for i, node in enumerate(self.pipeline.nodes):
            if node.id == node_id:
                return i
        return -1

    def can_move_node(self, node_id: str, new_index: int) -> bool:
        """
        Check if node can be moved to new index.

        Input (index 0) and Output (last index) are fixed and cannot move.
        Middle nodes can only be placed between the fixed nodes.
        """
        current_index = self.get_node_index(node_id)
        if current_index == -1:
            return False

        node = self.pipeline.nodes[current_index]

        # Fixed nodes cannot move
        if node.type in ("input", "output"):
            return False

        # Must have at least 2 nodes (input + output)
        if len(self.pipeline.nodes) < 2:
            return False

        # Valid range is between input (0) and output (len-1)
        min_index = 1  # After input
        max_index = len(self.pipeline.nodes) - 2  # Before output

        return min_index <= new_index <= max_index

    def move_node(self, node_id: str, new_index: int) -> bool:
        """
        Move node to new index.

        Returns True if move succeeded.
        """
        if not self.can_move_node(node_id, new_index):
            return False

        current_index = self.get_node_index(node_id)
        if current_index == -1:
            return False

        node = self.pipeline.nodes.pop(current_index)
        self.pipeline.nodes.insert(new_index, node)
        return True

    def insert_node_between(self, node: PipelineNode, after_node_id: str) -> bool:
        """
        Insert a new node after the specified node.

        Returns True if insertion succeeded.
        """
        after_index = self.get_node_index(after_node_id)
        if after_index == -1:
            return False

        # Insert after the target node
        insert_index = after_index + 1

        # Make sure we're not inserting after output
        if insert_index >= len(self.pipeline.nodes):
            return False

        self.pipeline.nodes.insert(insert_index, node)
        return True

    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the pipeline.

        Input and Output nodes cannot be removed.
        Returns True if removal succeeded.
        """
        index = self.get_node_index(node_id)
        if index == -1:
            return False

        node = self.pipeline.nodes[index]

        # Fixed nodes cannot be removed
        if node.type in ("input", "output"):
            return False

        self.pipeline.nodes.pop(index)

        # Clear selection if removed node was selected
        if self.selected_node_id == node_id:
            self.selected_node_id = None

        return True

    def add_node(self, node: PipelineNode) -> bool:
        """
        Add a node to the pipeline.

        Node is inserted before the output node.
        Returns True if addition succeeded.
        """
        if len(self.pipeline.nodes) < 2:
            return False

        # Insert before output (last node)
        output_index = len(self.pipeline.nodes) - 1
        self.pipeline.nodes.insert(output_index, node)
        return True

    def update_node_parameter(self, node_id: str, param_name: str, value: Any) -> bool:
        """
        Update a parameter value for a node.

        Returns True if update succeeded.
        """
        node = self.get_node(node_id)
        if node is None:
            return False

        node.parameters[param_name] = value
        return True

    def toggle_node(self, node_id: str) -> bool:
        """
        Toggle node enabled state.

        Input and Output nodes cannot be toggled.
        Returns new enabled state, or None if failed.
        """
        node = self.get_node(node_id)
        if node is None:
            return None

        # Fixed nodes cannot be toggled
        if node.type in ("input", "output"):
            return None

        node.enabled = not node.enabled
        return node.enabled

    def set_node_enabled(self, node_id: str, enabled: bool) -> bool:
        """
        Set node enabled state explicitly.

        Returns True if change succeeded.
        """
        node = self.get_node(node_id)
        if node is None:
            return False

        # Fixed nodes cannot be changed
        if node.type in ("input", "output"):
            return False

        node.enabled = enabled
        return True
