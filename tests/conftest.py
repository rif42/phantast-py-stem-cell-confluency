import pytest
import tempfile
import numpy as np
import cv2
from pathlib import Path


@pytest.fixture
def sample_image_gray():
    """Create a sample grayscale image."""
    return np.random.randint(0, 255, (100, 100), dtype=np.uint8)


@pytest.fixture
def sample_image_color():
    """Create a sample color image."""
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def temp_image_file(tmp_path):
    """Create a temporary image file."""

    def _create_image(shape=(100, 100, 3), dtype=np.uint8):
        img = np.random.randint(0, 255, shape, dtype=dtype)
        filepath = tmp_path / "test_image.png"
        cv2.imwrite(str(filepath), img)
        return str(filepath)

    return _create_image


@pytest.fixture
def temp_folder_with_images(tmp_path):
    """Create a temporary folder with sample images."""
    folder = tmp_path / "test_images"
    folder.mkdir()

    # Create several test images
    for i in range(5):
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        cv2.imwrite(str(folder / f"test_{i}.png"), img)

    return str(folder)
