"""PHANTAST stem cell confluency detection step.

Implements the PHANTAST algorithm for automated stem cell confluency measurement.
This is a special/flagship node with gold border styling.
"""

import cv2
import numpy as np
from typing import Any

from . import register_step, StepParameter


STEP_NAME = "phantast"
STEP_DESCRIPTION = (
    "PHANTAST - Stem cell confluency detection using adaptive thresholding"
)
STEP_ICON = "🔬"

STEP_PARAMETERS = [
    StepParameter(
        name="sigma",
        type="float",
        default=1.5,
        min=0.1,
        max=5.0,
        step=0.1,
        description="Sigma parameter for Gaussian smoothing (higher = more smoothing)",
    ),
    StepParameter(
        name="epsilon",
        type="float",
        default=0.05,
        min=0.01,
        max=0.5,
        step=0.01,
        description="Epsilon threshold for confluency detection (lower = more sensitive)",
    ),
]


def process(image: np.ndarray, sigma: float = 1.5, epsilon: float = 0.05) -> np.ndarray:
    """Apply PHANTAST confluency detection to the input image.

    Args:
        image: Input image as numpy array
        sigma: Sigma for Gaussian smoothing (default 1.5)
        epsilon: Threshold for confluency detection (default 0.05)

    Returns:
        Binary mask showing detected confluent regions

    Note:
        - Converts color images to grayscale automatically
        - Returns uint8 binary image (0 or 255)
    """
    # Ensure we have a grayscale image
    if len(image.shape) == 3:
        if image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif image.shape[2] == 4:
            gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        else:
            gray = image[:, :, 0]
    else:
        gray = image

    # Normalize to float
    gray_float = gray.astype(np.float32) / 255.0

    # Apply Gaussian smoothing
    ksize = int(sigma * 6) | 1  # Ensure odd kernel size
    smoothed = cv2.GaussianBlur(gray_float, (ksize, ksize), sigma)

    # Compute local statistics for adaptive thresholding
    mean = cv2.blur(smoothed, (15, 15))
    mean_sq = cv2.blur(smoothed * smoothed, (15, 15))
    variance = mean_sq - mean * mean
    std = np.sqrt(np.maximum(variance, 0))

    # Adaptive threshold: pixels significantly darker than local mean
    threshold = mean - epsilon * std
    binary = (smoothed < threshold).astype(np.uint8) * 255

    # Morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    return binary


# Register the step
process = register_step(process)
