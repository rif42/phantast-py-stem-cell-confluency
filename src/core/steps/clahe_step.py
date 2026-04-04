"""CLAHE (Contrast Limited Adaptive Histogram Equalization) processing step.

Adapts the standalone CLAHE.py implementation for the pipeline system.
"""

import cv2
import numpy as np
from typing import Any

from . import register_step, StepParameter


STEP_NAME = "clahe"
STEP_DESCRIPTION = "Enhances local contrast via adaptive histogram equalization"
STEP_ICON = "⚙️"
STEP_CATEGORY = "image_processing"

STEP_PARAMETERS = [
    StepParameter(
        name="clip_limit",
        type="float",
        default=2.0,
        min=0.1,
        max=10.0,
        step=0.1,
        description="CLAHE clip limit - threshold for contrast limiting (higher = more contrast enhancement)",
    ),
    StepParameter(
        name="block_size",
        type="int",
        default=8,
        min=2,
        max=32,
        step=1,
        description="Tile grid size for histogram equalization (block_size x block_size)",
    ),
]


@register_step
def process(
    image: np.ndarray, clip_limit: float = 2.0, block_size: int = 8
) -> np.ndarray:
    """Apply CLAHE to the input image.

    Args:
        image: Input image as numpy array (grayscale)
        clip_limit: CLAHE clip limit - threshold for contrast limiting (default 2.0)
        block_size: Tile grid size for histogram equalization (default 8)

    Returns:
        Processed image with CLAHE applied

    Note:
        - If input is color (3 channels), converts to grayscale first
        - If input is multi-channel, processes first channel only
    """
    # Ensure we have a grayscale image
    if len(image.shape) == 3:
        if image.shape[2] == 3:
            # Convert BGR to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif image.shape[2] == 4:
            # Convert BGRA to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        else:
            # Take first channel
            gray = image[:, :, 0]
    else:
        gray = image

    # Ensure uint8
    if gray.dtype != np.uint8:
        normalized = np.empty_like(gray, dtype=np.uint8)
        cv2.normalize(gray, normalized, 0, 255, cv2.NORM_MINMAX)
        gray = normalized

    # Create CLAHE object
    clahe = cv2.createCLAHE(
        clipLimit=float(clip_limit),
        tileGridSize=(int(block_size), int(block_size)),
    )

    # Apply CLAHE
    result = clahe.apply(gray)

    return result
