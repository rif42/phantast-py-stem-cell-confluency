import pytest
from PyQt6.QtCore import QCoreApplication
from src.controllers.main_controller import MainController
from src.models.app_state import WorkflowPhase


class TestMainControllerInitialization:
    """Test MainController initialization."""

    def test_controller_creates_with_app_state(self):
        """Test controller initializes with AppState."""
        controller = MainController()

        assert controller.state is not None
        assert controller.current_phase == WorkflowPhase.EMPTY
        assert controller.has_image is False

    def test_initial_signals_not_connected(self, qtbot):
        """Test signals exist and can be connected."""
        controller = MainController()

        # Should be able to connect to signals
        with qtbot.waitSignal(controller.phase_changed, timeout=100, raising=False):
            pass  # Just test connection works


class TestPhaseTransitions:
    """Test phase transition methods."""

    def test_load_image_transitions_phase(self, qtbot):
        """Test load_image transitions EMPTY -> IMAGE_LOADED."""
        controller = MainController()

        # Create a test image file path (won't actually load)
        # Use a real image from fixtures
        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        # Skip if no test image available
        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        with qtbot.waitSignal(controller.phase_changed) as blocker:
            controller.load_image(test_image)

        assert blocker.args[0] == WorkflowPhase.IMAGE_LOADED
        assert controller.current_phase == WorkflowPhase.IMAGE_LOADED
        assert controller.has_image is True

    def test_clear_image_transitions_back(self, qtbot):
        """Test clear_image transitions back to EMPTY."""
        controller = MainController()

        # First load an image
        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)

        # Then clear
        with qtbot.waitSignal(controller.phase_changed) as blocker:
            controller.clear_image()

        assert blocker.args[0] == WorkflowPhase.EMPTY
        assert controller.current_phase == WorkflowPhase.EMPTY
        assert controller.has_image is False


class TestNodeOperations:
    """Test node CRUD operations."""

    def test_add_node_requires_image(self, qtbot):
        """Test add_node fails without image loaded."""
        controller = MainController()

        result = controller.add_node("grayscale")

        assert result is None

    def test_add_node_with_image(self, qtbot):
        """Test add_node succeeds with image loaded."""
        controller = MainController()

        # Load image first
        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)

        # Add node
        with qtbot.waitSignal(controller.node_added) as blocker:
            node_id = controller.add_node("grayscale")

        assert node_id is not None
        assert node_id.startswith("grayscale_")
        assert blocker.args[0] == node_id
        assert len(controller.state.pipeline.nodes) == 3  # input + grayscale + output

    def test_remove_node(self, qtbot):
        """Test remove_node removes middle node."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)
        node_id = controller.add_node("grayscale")

        with qtbot.waitSignal(controller.node_removed) as blocker:
            result = controller.remove_node(node_id)

        assert result is True
        assert blocker.args[0] == node_id
        assert len(controller.state.pipeline.nodes) == 2  # back to input + output

    def test_remove_fixed_node_fails(self, qtbot):
        """Test cannot remove fixed input/output nodes."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)

        # Try to remove input node
        result = controller.remove_node("input")
        assert result is False

        # Try to remove output node
        result = controller.remove_node("output")
        assert result is False

    def test_move_node(self, qtbot):
        """Test move_node reorders nodes."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)

        # Add two nodes
        node1_id = controller.add_node("grayscale")
        node2_id = controller.add_node("blur")

        # Order: input, grayscale, blur, output
        # Move grayscale after blur
        with qtbot.waitSignal(controller.node_moved) as blocker:
            result = controller.move_node(node1_id, 2)

        assert result is True
        assert blocker.args[0] == node1_id
        assert blocker.args[1] == 2

        # Verify order: input, blur, grayscale, output
        assert controller.state.pipeline.nodes[1].id == node2_id
        assert controller.state.pipeline.nodes[2].id == node1_id

    def test_move_fixed_node_fails(self, qtbot):
        """Test cannot move fixed nodes."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)

        # Try to move input node
        result = controller.move_node("input", 1)
        assert result is False

        # Try to move output node
        result = controller.move_node("output", 0)
        assert result is False


class TestNodeToggle:
    """Test node toggle operations."""

    def test_toggle_middle_node(self, qtbot):
        """Test toggling middle node."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)
        node_id = controller.add_node("grayscale")

        with qtbot.waitSignal(controller.node_toggled) as blocker:
            result = controller.toggle_node(node_id)

        assert result is False  # Now disabled
        assert blocker.args[0] == node_id
        assert blocker.args[1] is False

    def test_toggle_fixed_node_fails(self, qtbot):
        """Test cannot toggle fixed nodes."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)

        result = controller.toggle_node("input")
        assert result is None

        result = controller.toggle_node("output")
        assert result is None


class TestNodeSelection:
    """Test node selection."""

    def test_select_node(self, qtbot):
        """Test selecting a node."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)

        with qtbot.waitSignal(controller.node_selected) as blocker:
            result = controller.select_node("input")

        assert result is True
        assert blocker.args[0] == "input"
        assert controller.selected_node_id == "input"

    def test_clear_selection(self, qtbot):
        """Test clearing selection."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)
        controller.select_node("input")

        with qtbot.waitSignal(controller.node_selected) as blocker:
            result = controller.clear_selection()

        assert result is True
        assert blocker.args[0] is None
        assert controller.selected_node_id is None


class TestParameterUpdates:
    """Test parameter update operations."""

    def test_update_node_parameter(self, qtbot):
        """Test updating node parameter."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)
        node_id = controller.add_node("gaussian_blur")

        with qtbot.waitSignal(controller.node_parameter_changed) as blocker:
            result = controller.update_node_parameter(node_id, "sigma", 2.5)

        assert result is True
        assert blocker.args[0] == node_id
        assert blocker.args[1] == "sigma"
        assert blocker.args[2] == 2.5

        # Verify state updated
        node = controller.state.get_node(node_id)
        assert node.parameters["sigma"] == 2.5


class TestPreviewDebouncing:
    """Test preview execution debouncing."""

    def test_preview_debounce_triggered(self, qtbot):
        """Test that changes trigger preview debounce."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)

        # Add a node - should trigger debounce
        with qtbot.waitSignal(controller.preview_started, timeout=500):
            controller.add_node("grayscale")
            # Wait for debounce timer
            qtbot.wait(250)

    def test_immediate_preview_bypasses_debounce(self, qtbot):
        """Test immediate preview bypasses debounce."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)

        # Request immediate preview
        with qtbot.waitSignal(controller.preview_started):
            controller.request_immediate_preview()


class TestUtilityMethods:
    """Test utility methods."""

    def test_get_available_node_types(self):
        """Test getting available node types."""
        controller = MainController()

        types = controller.get_available_node_types()

        assert len(types) == 3  # grayscale, gaussian_blur, clahe
        type_ids = [t["type_id"] for t in types]
        assert "grayscale" in type_ids
        assert "gaussian_blur" in type_ids
        assert "clahe" in type_ids

    def test_get_node_info(self):
        """Test getting node info."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)

        info = controller.get_node_info("input")

        assert info is not None
        assert info["id"] == "input"
        assert info["type"] == "input"
        assert info["is_fixed"] is True

    def test_is_node_fixed(self):
        """Test checking if node is fixed."""
        controller = MainController()

        import os

        test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_image = os.path.join(test_dir, "fixtures", "test_image.tiff")

        if not os.path.exists(test_image):
            pytest.skip("Test image not available")

        controller.load_image(test_image)
        node_id = controller.add_node("grayscale")

        assert controller.is_node_fixed("input") is True
        assert controller.is_node_fixed("output") is True
        assert controller.is_node_fixed(node_id) is False
