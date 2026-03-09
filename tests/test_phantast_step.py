"""Unit tests for PHANTAST step internals and outputs."""

import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.core.steps.phantast_step import (
    calculate_confluency,
    contrast_stretching,
    gaussian_filter_separable,
    halo_removal,
    kirsch_edge_detection,
    local_contrast_cv,
    process,
    process_phantast,
    remove_holes,
    remove_small_objects_mask,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def synthetic_image() -> np.ndarray:
    image = cv2.imread(str(FIXTURES_DIR / "synthetic_stem_cells.png"), cv2.IMREAD_COLOR)
    assert image is not None
    return image


@pytest.fixture
def expected_mask() -> np.ndarray:
    mask = cv2.imread(
        str(FIXTURES_DIR / "expected_phantast_mask.png"), cv2.IMREAD_GRAYSCALE
    )
    assert mask is not None
    return mask


def test_gaussian_filter_separable_preserves_shape():
    image = np.arange(100, dtype=np.float64).reshape(10, 10)
    out = gaussian_filter_separable(image, sigma=2.0)

    assert out.shape == image.shape
    assert out.dtype == np.float64


def test_contrast_stretching_zero_saturation_is_identity():
    image = np.linspace(0, 1, 25, dtype=np.float64).reshape(5, 5)
    out = contrast_stretching(image, saturation_percentage=0)

    assert np.array_equal(out, image)


def test_contrast_stretching_maps_values_into_unit_range():
    image = np.array([[0, 20, 50], [120, 200, 255]], dtype=np.uint8)
    out = contrast_stretching(image, saturation_percentage=1.0)

    assert out.dtype == np.float64
    assert out.min() >= 0
    assert out.max() <= 1


def test_local_contrast_cv_returns_boolean_mask():
    image = np.tile(np.linspace(0, 1, 64), (64, 1))
    mask = local_contrast_cv(image, sigma=2.0, epsilon=0.05)

    assert mask.shape == image.shape
    assert mask.dtype == np.bool_


def test_local_contrast_cv_epsilon_controls_sensitivity(synthetic_image):
    gray = cv2.cvtColor(synthetic_image, cv2.COLOR_BGR2GRAY)
    sensitive = local_contrast_cv(gray, sigma=4.0, epsilon=0.03)
    strict = local_contrast_cv(gray, sigma=4.0, epsilon=0.09)

    assert np.sum(sensitive) >= np.sum(strict)


def test_remove_small_objects_mask_removes_objects_at_or_below_threshold():
    mask = np.zeros((20, 20), dtype=bool)
    mask[1:3, 1:3] = True
    mask[10:18, 10:18] = True

    cleaned = remove_small_objects_mask(mask, threshold_area=4)

    assert not np.any(cleaned[1:3, 1:3])
    assert np.any(cleaned[10:18, 10:18])


def test_remove_holes_fills_only_holes_within_area_limit():
    mask = np.ones((15, 15), dtype=bool)
    mask[3:5, 3:5] = False
    mask[7:12, 7:12] = False

    filled = remove_holes(mask, max_area=5)

    assert np.all(filled[3:5, 3:5])
    assert not np.any(filled[7:12, 7:12])


def test_kirsch_edge_detection_returns_valid_direction_indices(synthetic_image):
    gray = cv2.cvtColor(synthetic_image, cv2.COLOR_BGR2GRAY).astype(np.float64) / 255.0
    intensity, direction = kirsch_edge_detection(gray)

    assert intensity.shape == gray.shape
    assert direction.shape == gray.shape
    assert direction.min() >= 1
    assert direction.max() <= 8


def test_halo_removal_rejects_unknown_kernel_type(synthetic_image):
    gray = cv2.cvtColor(synthetic_image, cv2.COLOR_BGR2GRAY)
    mask = gray > 120

    with pytest.raises(ValueError, match="Only 'kirsch' kernel type is implemented"):
        halo_removal(gray, mask, max_fill_area=100, kernel_type="sobel")


def test_process_phantast_returns_confluency_and_boolean_mask(synthetic_image):
    confluency, mask = process_phantast(
        synthetic_image,
        sigma=6.5,
        epsilon=0.045,
        do_contrast_stretching=True,
        contrast_stretching_saturation=0.5,
        do_halo_removal=True,
        minimum_fill_area=120,
        do_remove_small_objects=True,
        minimum_object_area=90,
        hr_remove_small_objects=90,
        max_removal_ratio=0.3,
    )

    assert 0.0 <= confluency <= 100.0
    assert mask.dtype == np.bool_
    assert mask.shape[:2] == synthetic_image.shape[:2]


def test_process_output_is_valid_binary_mask_and_matches_regression(
    synthetic_image, expected_mask
):
    out = process(
        synthetic_image,
        sigma=6.5,
        epsilon=0.045,
        contrast_stretch=True,
        contrast_saturation=0.5,
        halo_removal=True,
        min_fill_area=120,
        remove_small_objects=True,
        min_object_area=90,
        max_removal_ratio=0.3,
    )

    assert out.dtype == np.uint8
    assert set(np.unique(out).tolist()).issubset({0, 255})
    assert np.array_equal(out, expected_mask)


def test_calculate_confluency_matches_known_ratio():
    mask = np.zeros((10, 10), dtype=bool)
    mask[:3, :] = True

    confluency = calculate_confluency(mask)
    assert confluency == 30.0
