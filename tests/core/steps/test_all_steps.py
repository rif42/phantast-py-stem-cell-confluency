import pytest
from src.core.pipeline_step import PipelineStep, StepParameter
from src.core.steps import (
    GrayscaleStep,
    GaussianBlurStep,
    ClaheStep,
    PhantastStep,
)
import numpy as np


class TestGrayscaleStep:
    def test_convert_color_to_grayscale(self):
        step = GrayscaleStep()
        color_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = step.process(color_image, {})
        assert result.shape == (100, 100)
        assert result.dtype == np.uint8

    def test_pass_through_grayscale(self):
        step = GrayscaleStep()
        gray_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        result = step.process(gray_image, {})
        np.testing.assert_array_equal(result, gray_image)


class TestGaussianBlurStep:
    def test_blur_reduces_variance(self):
        step = GaussianBlurStep()
        image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        result = step.process(image, {})
        # Blurred image should have lower variance
        assert result.std() < image.std()

    def test_kernel_size_odd_adjustment(self):
        step = GaussianBlurStep()
        step.set_param("kernel_size", 4)  # Even
        image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        result = step.process(image, {})  # Should work, adjusts to 5
        assert result.shape == image.shape


class TestClaheStep:
    def test_enhances_contrast(self):
        step = ClaheStep()
        step.set_param("clip_limit", 3.0)
        # Low contrast image
        low_contrast = np.full((100, 100), 100, dtype=np.uint8)
        low_contrast[40:60, 40:60] = 110
        result = step.process(low_contrast, {})
        assert result.std() > low_contrast.std()

    def test_handles_color_input(self):
        step = ClaheStep()
        color_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = step.process(color_image, {})
        assert result.shape == (100, 100)  # Returns grayscale


class TestPhantastStep:
    def test_processes_image(self):
        """Test that PHANTAST processes the image and creates green overlay."""
        step = PhantastStep()
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = step.process(image, {})
        # Result should be same shape
        assert result.shape == image.shape
        # Result should have green pixels (overlay applied)
        # Green channel should have 255 values where mask was applied
        green_pixels = np.sum(result[:, :, 1] == 255)
        assert green_pixels > 0, "Expected green overlay pixels"

    def test_metadata_storage(self):
        """Test that PHANTAST stores confluency and mask in metadata."""
        step = PhantastStep()
        metadata = {}
        image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        result = step.process(image, metadata)
        # Should add metadata when phantast available
        assert "phantast_confluency" in metadata
        assert isinstance(metadata["phantast_confluency"], (int, float))
        assert "phantast_mask" in metadata
        assert metadata["phantast_mask"].shape == (100, 100)

    def test_parameters(self):
        """Test that PHANTAST parameters work correctly."""
        step = PhantastStep()
        # Check default parameters
        assert step.get_param("sigma") == 4.0
        assert step.get_param("epsilon") == 0.05
        # Test parameter update
        step.set_param("sigma", 2.0)
        assert step.get_param("sigma") == 2.0
