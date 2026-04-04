"""Crop processing step (placeholder).

This is a placeholder implementation that returns the input unchanged.
Full implementation will crop a region of interest from the image.
"""

import numpy as np
from typing import Any

from . import register_step, StepParameter


STEP_NAME = "crop"
STEP_DESCRIPTION = "Crops a region of interest from the image"
STEP_ICON = "✂️"

STEP_PARAMETERS: list[StepParameter] = []


def process(image: np.ndarray) -> np.ndarray:
    """Placeholder crop operation.

    Args:
        image: Input image as numpy array

    Returns:
        Input image unchanged (placeholder behavior)
    """
    # Placeholder: return input unchanged
    return image


# Register the step
process = register_step(process)
