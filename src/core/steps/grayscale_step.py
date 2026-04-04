"""Grayscale conversion processing step (placeholder).

This is a placeholder implementation that returns the input unchanged.
Full implementation will convert color images to grayscale.
"""

import numpy as np
from typing import Any

from . import register_step, StepParameter


STEP_NAME = "grayscale"
STEP_DESCRIPTION = "Converts color image to grayscale"
STEP_ICON = "🔲"
STEP_CATEGORY = "image_processing"

STEP_PARAMETERS: list[StepParameter] = []


def process(image: np.ndarray) -> np.ndarray:
    """Placeholder grayscale conversion.

    Args:
        image: Input image as numpy array

    Returns:
        Input image unchanged (placeholder behavior)
    """
    # Placeholder: return input unchanged
    return image


# Register the step
process = register_step(process)
