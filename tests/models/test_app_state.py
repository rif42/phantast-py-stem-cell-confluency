import pytest
from src.models.app_state import AppState, WorkflowPhase
from src.models.pipeline_model import Pipeline, PipelineNode
from src.models.image_model import ImageSessionModel


class TestWorkflowPhase:
    """Test WorkflowPhase enum."""

    def test_phase_values(self):
        """Test that phase enum has expected values."""
        assert WorkflowPhase.EMPTY is not None
        assert WorkflowPhase.IMAGE_LOADED is not None
        assert WorkflowPhase.EMPTY != WorkflowPhase.IMAGE_LOADED


class TestAppStateInitialization:
    """Test AppState initialization."""

    def test_default_initialization(self):
        """Test AppState initializes with correct defaults."""
        state = AppState()

        assert state.current_image is None
        assert state.pipeline is not None
        assert isinstance(state.pipeline, Pipeline)
        assert state.selected_node_id is None
        assert state.workflow_phase == WorkflowPhase.EMPTY

    def test_custom_initialization(self):
        """Test AppState can be initialized with custom values."""
        pipeline = Pipeline(name="Test Pipeline")
        image = ImageSessionModel()

        state = AppState(
            current_image=image,
            pipeline=pipeline,
            selected_node_id="node1",
            workflow_phase=WorkflowPhase.IMAGE_LOADED,
        )

        assert state.current_image is image
        assert state.pipeline is pipeline
        assert state.selected_node_id == "node1"
        assert state.workflow_phase == WorkflowPhase.IMAGE_LOADED


class TestWorkflowPhaseTransitions:
    """Test phase transition logic."""

    def test_empty_to_image_loaded_valid(self):
        """Test EMPTY -> IMAGE_LOADED is valid."""
        state = AppState(workflow_phase=WorkflowPhase.EMPTY)

        assert state.can_transition_to(WorkflowPhase.IMAGE_LOADED) is True

    def test_empty_to_image_loaded_transition(self):
        """Test EMPTY -> IMAGE_LOADED transition succeeds."""
        state = AppState(workflow_phase=WorkflowPhase.EMPTY)

        result = state.transition_to(WorkflowPhase.IMAGE_LOADED)

        assert result is True
        assert state.workflow_phase == WorkflowPhase.IMAGE_LOADED

    def test_image_loaded_to_empty_valid(self):
        """Test IMAGE_LOADED -> EMPTY is valid."""
        state = AppState(workflow_phase=WorkflowPhase.IMAGE_LOADED)

        assert state.can_transition_to(WorkflowPhase.EMPTY) is True

    def test_invalid_transition(self):
        """Test invalid transition is rejected."""
        state = AppState(workflow_phase=WorkflowPhase.IMAGE_LOADED)

        # Cannot transition to same phase (depending on implementation)
        # or to invalid phase
        result = state.transition_to(WorkflowPhase.IMAGE_LOADED)

        # Transition to same phase should fail
        assert result is False


class TestDefaultPipeline:
    """Test default pipeline creation."""

    def test_initialize_default_pipeline(self):
        """Test default pipeline has Input and Output nodes."""
        state = AppState()

        state.initialize_default_pipeline()

        assert len(state.pipeline.nodes) == 2

        # Input node
        input_node = state.pipeline.nodes[0]
        assert input_node.id == "input"
        assert input_node.type == "input"
        assert input_node.name == "Input"

        # Output node
        output_node = state.pipeline.nodes[1]
        assert output_node.id == "output"
        assert output_node.type == "output"
        assert output_node.name == "PHANTAST"


class TestNodeOperations:
    """Test node operations."""

    def test_get_node(self):
        """Test getting node by ID."""
        state = AppState()
        state.initialize_default_pipeline()

        node = state.get_node("input")
        assert node is not None
        assert node.id == "input"

        node = state.get_node("nonexistent")
        assert node is None

    def test_get_node_index(self):
        """Test getting node index."""
        state = AppState()
        state.initialize_default_pipeline()

        assert state.get_node_index("input") == 0
        assert state.get_node_index("output") == 1
        assert state.get_node_index("nonexistent") == -1

    def test_add_node(self):
        """Test adding a node to pipeline."""
        state = AppState()
        state.initialize_default_pipeline()

        new_node = PipelineNode(
            id="grayscale",
            type="processing",
            name="Grayscale",
            description="Convert to grayscale",
            icon="",
            status="ready",
            enabled=True,
        )

        result = state.add_node(new_node)

        assert result is True
        assert len(state.pipeline.nodes) == 3
        assert state.pipeline.nodes[1].id == "grayscale"

    def test_remove_node(self):
        """Test removing a node."""
        state = AppState()
        state.initialize_default_pipeline()

        # Add a middle node
        new_node = PipelineNode(
            id="grayscale",
            type="processing",
            name="Grayscale",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        state.add_node(new_node)

        # Remove it
        result = state.remove_node("grayscale")

        assert result is True
        assert len(state.pipeline.nodes) == 2
        assert state.get_node("grayscale") is None

    def test_remove_input_node_fails(self):
        """Test that Input node cannot be removed."""
        state = AppState()
        state.initialize_default_pipeline()

        result = state.remove_node("input")

        assert result is False
        assert len(state.pipeline.nodes) == 2

    def test_remove_output_node_fails(self):
        """Test that Output node cannot be removed."""
        state = AppState()
        state.initialize_default_pipeline()

        result = state.remove_node("output")

        assert result is False
        assert len(state.pipeline.nodes) == 2


class TestNodeMovement:
    """Test node movement with fixed Input/Output constraints."""

    def test_can_move_middle_node(self):
        """Test middle nodes can be moved."""
        state = AppState()
        state.initialize_default_pipeline()

        # Add two middle nodes
        node1 = PipelineNode(
            id="grayscale",
            type="processing",
            name="Grayscale",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        node2 = PipelineNode(
            id="blur",
            type="processing",
            name="Blur",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        state.add_node(node1)
        state.add_node(node2)

        # Should be able to move grayscale to position 2
        assert state.can_move_node("grayscale", 2) is True

    def test_cannot_move_input_node(self):
        """Test Input node cannot be moved."""
        state = AppState()
        state.initialize_default_pipeline()

        assert state.can_move_node("input", 1) is False
        assert state.can_move_node("input", 0) is False

    def test_cannot_move_output_node(self):
        """Test Output node cannot be moved."""
        state = AppState()
        state.initialize_default_pipeline()

        assert state.can_move_node("output", 0) is False
        assert state.can_move_node("output", 1) is False

    def test_cannot_move_before_input(self):
        """Test nodes cannot be placed before Input."""
        state = AppState()
        state.initialize_default_pipeline()

        node = PipelineNode(
            id="grayscale",
            type="processing",
            name="Grayscale",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        state.add_node(node)

        assert state.can_move_node("grayscale", 0) is False

    def test_cannot_move_after_output(self):
        """Test nodes cannot be placed after Output."""
        state = AppState()
        state.initialize_default_pipeline()

        node = PipelineNode(
            id="grayscale",
            type="processing",
            name="Grayscale",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        state.add_node(node)

        # Try to move to position after output (last index)
        assert state.can_move_node("grayscale", 2) is False

    def test_move_node_succeeds(self):
        """Test successful node movement."""
        state = AppState()
        state.initialize_default_pipeline()

        node1 = PipelineNode(
            id="grayscale",
            type="processing",
            name="Grayscale",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        node2 = PipelineNode(
            id="blur",
            type="processing",
            name="Blur",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        state.add_node(node1)
        state.add_node(node2)

        # Order: input, grayscale, blur, output
        # Move grayscale after blur
        result = state.move_node("grayscale", 2)

        assert result is True
        assert state.pipeline.nodes[1].id == "blur"
        assert state.pipeline.nodes[2].id == "grayscale"

    def test_move_node_fails_for_fixed(self):
        """Test moving fixed node fails."""
        state = AppState()
        state.initialize_default_pipeline()

        result = state.move_node("input", 1)

        assert result is False
        assert state.pipeline.nodes[0].id == "input"


class TestNodeSelection:
    """Test node selection operations."""

    def test_select_node(self):
        """Test selecting a node."""
        state = AppState()
        state.initialize_default_pipeline()

        result = state.select_node("input")

        assert result is True
        assert state.selected_node_id == "input"

    def test_select_nonexistent_node_fails(self):
        """Test selecting non-existent node fails."""
        state = AppState()
        state.initialize_default_pipeline()

        result = state.select_node("nonexistent")

        assert result is False
        assert state.selected_node_id is None

    def test_clear_selection(self):
        """Test clearing selection."""
        state = AppState()
        state.initialize_default_pipeline()
        state.select_node("input")

        result = state.clear_selection()

        assert result is True
        assert state.selected_node_id is None

    def test_get_selected_node(self):
        """Test getting selected node object."""
        state = AppState()
        state.initialize_default_pipeline()
        state.select_node("input")

        node = state.get_selected_node()

        assert node is not None
        assert node.id == "input"

    def test_is_node_selected(self):
        """Test checking if node is selected."""
        state = AppState()
        state.initialize_default_pipeline()
        state.select_node("input")

        assert state.is_node_selected("input") is True
        assert state.is_node_selected("output") is False

    def test_select_same_node_no_change(self):
        """Test selecting same node returns False (no change)."""
        state = AppState()
        state.initialize_default_pipeline()
        state.select_node("input")

        result = state.select_node("input")

        assert result is False


class TestNodeToggle:
    """Test node toggle operations."""

    def test_toggle_middle_node(self):
        """Test toggling middle node."""
        state = AppState()
        state.initialize_default_pipeline()

        node = PipelineNode(
            id="grayscale",
            type="processing",
            name="Grayscale",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        state.add_node(node)

        result = state.toggle_node("grayscale")

        assert result is False  # Now disabled
        assert state.get_node("grayscale").enabled is False

    def test_cannot_toggle_input_node(self):
        """Test Input node cannot be toggled."""
        state = AppState()
        state.initialize_default_pipeline()

        result = state.toggle_node("input")

        assert result is None
        assert state.get_node("input").enabled is True

    def test_cannot_toggle_output_node(self):
        """Test Output node cannot be toggled."""
        state = AppState()
        state.initialize_default_pipeline()

        result = state.toggle_node("output")

        assert result is None
        assert state.get_node("output").enabled is True

    def test_set_node_enabled(self):
        """Test explicitly setting node enabled state."""
        state = AppState()
        state.initialize_default_pipeline()

        node = PipelineNode(
            id="grayscale",
            type="processing",
            name="Grayscale",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        state.add_node(node)

        result = state.set_node_enabled("grayscale", False)

        assert result is True
        assert state.get_node("grayscale").enabled is False


class TestNodeParameters:
    """Test node parameter operations."""

    def test_update_node_parameter(self):
        """Test updating node parameter."""
        state = AppState()
        state.initialize_default_pipeline()

        node = PipelineNode(
            id="blur",
            type="processing",
            name="Blur",
            description="",
            icon="",
            status="ready",
            enabled=True,
            parameters={"sigma": 1.0},
        )
        state.add_node(node)

        result = state.update_node_parameter("blur", "sigma", 2.5)

        assert result is True
        assert state.get_node("blur").parameters["sigma"] == 2.5

    def test_update_nonexistent_node_fails(self):
        """Test updating parameter of non-existent node fails."""
        state = AppState()

        result = state.update_node_parameter("nonexistent", "param", 1)

        assert result is False

    def test_add_new_parameter(self):
        """Test adding new parameter to node."""
        state = AppState()
        state.initialize_default_pipeline()

        node = PipelineNode(
            id="blur",
            type="processing",
            name="Blur",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        state.add_node(node)

        state.update_node_parameter("blur", "kernel_size", 5)

        assert state.get_node("blur").parameters["kernel_size"] == 5


class TestSelectionOnRemove:
    """Test selection behavior when node is removed."""

    def test_selection_cleared_on_remove(self):
        """Test that selection is cleared when selected node is removed."""
        state = AppState()
        state.initialize_default_pipeline()

        node = PipelineNode(
            id="grayscale",
            type="processing",
            name="Grayscale",
            description="",
            icon="",
            status="ready",
            enabled=True,
        )
        state.add_node(node)
        state.select_node("grayscale")

        state.remove_node("grayscale")

        assert state.selected_node_id is None
