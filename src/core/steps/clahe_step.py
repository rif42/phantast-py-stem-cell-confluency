"""CLAHE (Contrast Limited Adaptive Histogram Equalization) processing step.

Adapts the standalone CLAHE.py implementation for the pipeline system.
"""

import cv2
import numpy as np
from typing import Any

from . import register_step, StepParameter


STEP_NAME = "clahe"
STEP_DESCRIPTION = "Contrast Limited Adaptive Histogram Equalization - enhances local contrast in images"
STEP_ICON = "⚙️"

STEP_PARAMETERS = [
    StepParameter(
        name="epsilon",
        type="float",
        default=2.0,
        min=0.1,
        max=10.0,
        step=0.1,
        description="CLAHE clip limit - threshold for contrast limiting (higher = more contrast enhancement)",
    ),
    StepParameter(
        name="sigma",
        type="float",
        default=8.0,
        min=2.0,
        max=32.0,
        step=1.0,
        description="Tile grid size for histogram equalization (sigma x sigma)",
    ),
]


def process(image: np.ndarray, epsilon: float = 2.0, sigma: float = 8.0) -> np.ndarray:
    """Apply CLAHE to the input image.

    Args:
        image: Input image as numpy array (grayscale)
        epsilon: CLAHE clip limit - threshold for contrast limiting (default 2.0)
        sigma: Tile grid size for histogram equalization (default 8.0)

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
        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # Create CLAHE object
    clahe = cv2.createCLAHE(
        clipLimit=float(epsilon), tileGridSize=(int(sigma), int(sigma))
    )

    # Apply CLAHE
    result = clahe.apply(gray)

    return result


# Register the step
process = register_step(process)
