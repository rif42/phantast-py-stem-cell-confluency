import pytest
import numpy as np
from src.core.preview_pipeline import PreviewPipeline, PreviewResult
from src.models.app_state import AppState, WorkflowPhase
from src.models.pipeline_model import PipelineNode


class TestPreviewPipelineInitialization:
    """Test PreviewPipeline initialization."""

    def test_pipeline_creates_successfully(self):
        """Test that PreviewPipeline can be created."""
        pipeline = PreviewPipeline()
        assert pipeline is not None
        assert pipeline._cache_enabled is True

    def test_cache_initially_empty(self):
        """Test that cache starts empty."""
        pipeline = PreviewPipeline()
        stats = pipeline.get_cache_stats()
        assert stats["size"] == 0
        assert stats["enabled"] is True


class TestPreviewPipelineExecution:
    """Test PreviewPipeline execution."""

    def test_execute_with_empty_pipeline_fails(self):
        """Test execution with no enabled nodes fails."""
        pipeline = PreviewPipeline()
        app_state = AppState()
        app_state.initialize_default_pipeline()

        # Disable all nodes
        for node in app_state.pipeline.nodes:
            node.enabled = False

        input_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        result = pipeline.execute(input_image, app_state)

        assert result.success is False
        assert "No enabled nodes" in result.error_message

    def test_execute_with_input_only(self):
        """Test execution with just input node passes through."""
        pipeline = PreviewPipeline()
        app_state = AppState()
        app_state.initialize_default_pipeline()

        # Disable output node
        app_state.pipeline.nodes[-1].enabled = False

        input_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        result = pipeline.execute(input_image, app_state)

        assert result.success is True
        assert result.image is not None
        # Input node just passes through
        assert result.image.shape == input_image.shape

    def test_execute_with_grayscale(self):
        """Test execution with grayscale node."""
        pipeline = PreviewPipeline()
        app_state = AppState()
        app_state.initialize_default_pipeline()

        # Disable output node to see grayscale result directly
        app_state.pipeline.nodes[-1].enabled = False

        # Add grayscale node
        grayscale_node = PipelineNode(
            id="grayscale_1",
            type="grayscale",
            name="Grayscale",
            description="Convert to grayscale",
            icon="",
            status="ready",
            enabled=True,
            parameters={},
        )
        app_state.add_node(grayscale_node)

        input_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        result = pipeline.execute(input_image, app_state)

        assert result.success is True
        assert result.image is not None
        # Grayscale node produces 2D output
        assert len(result.image.shape) == 2

    def test_execute_with_gaussian_blur(self):
        """Test execution with Gaussian blur node."""
        pipeline = PreviewPipeline()
        app_state = AppState()
        app_state.initialize_default_pipeline()

        # Add blur node
        blur_node = PipelineNode(
            id="blur_1",
            type="gaussian_blur",
            name="Gaussian Blur",
            description="Blur",
            icon="",
            status="ready",
            enabled=True,
            parameters={"kernel_size": 5, "sigma": 1.0},
        )
        app_state.add_node(blur_node)

        input_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        result = pipeline.execute(input_image, app_state)

        assert result.success is True
        assert result.image is not None

    def test_execute_tracks_execution_time(self):
        """Test that execution time is tracked."""
        pipeline = PreviewPipeline()
        app_state = AppState()
        app_state.initialize_default_pipeline()

        input_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        result = pipeline.execute(input_image, app_state)

        assert result.success is True
        assert result.execution_time_ms > 0


class TestPreviewPipelineCache:
    """Test PreviewPipeline caching."""

    def test_clear_cache(self):
        """Test clearing cache."""
        pipeline = PreviewPipeline()

        # Add something to cache manually
        pipeline._cache["test_key"] = np.array([1, 2, 3])

        pipeline.clear_cache()

        stats = pipeline.get_cache_stats()
        assert stats["size"] == 0

    def test_disable_cache_clears_cache(self):
        """Test disabling cache clears it."""
        pipeline = PreviewPipeline()

        # Add something to cache
        pipeline._cache["test_key"] = np.array([1, 2, 3])

        pipeline.set_cache_enabled(False)

        assert pipeline._cache_enabled is False
        stats = pipeline.get_cache_stats()
        assert stats["size"] == 0

    def test_re_enable_cache(self):
        """Test re-enabling cache."""
        pipeline = PreviewPipeline()

        pipeline.set_cache_enabled(False)
        assert pipeline._cache_enabled is False

        pipeline.set_cache_enabled(True)
        assert pipeline._cache_enabled is True


class TestPreviewResult:
    """Test PreviewResult dataclass."""

    def test_successful_result(self):
        """Test creating successful result."""
        image = np.array([[1, 2], [3, 4]])
        result = PreviewResult(
            success=True,
            image=image,
            execution_time_ms=100.0,
            node_results={"node1": {"name": "Test", "output": image}},
        )

        assert result.success is True
        assert result.error_message is None
        assert result.execution_time_ms == 100.0

    def test_failed_result(self):
        """Test creating failed result."""
        result = PreviewResult(success=False, error_message="Test error")

        assert result.success is False
        assert result.error_message == "Test error"
        assert result.image is None
