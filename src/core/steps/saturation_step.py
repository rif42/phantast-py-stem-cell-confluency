"""Color saturation adjustment processing step."""

import cv2
import numpy as np

from . import register_step, StepParameter


STEP_NAME = "saturation"
STEP_DESCRIPTION = "Adjusts color saturation level"
STEP_ICON = "art"
STEP_CATEGORY = "image_processing"

STEP_PARAMETERS = [
    StepParameter(
        name="saturation",
        type="range",
        default=100,
        min=0,
        max=200,
        step=1,
        description="Color saturation level (%)",
    ),
]


@register_step
def process(image: np.ndarray, saturation: int = 100) -> np.ndarray:
    """Adjust color saturation.

    Args:
        image: Input image as numpy array (BGR or grayscale).
        saturation: Saturation level (0-200). 0 = grayscale, 100 = original, 200 = double.

    Returns:
        Image with adjusted saturation.
    """
    # Grayscale images have no saturation to adjust
    if image.ndim == 2:
        return image

    # Single-channel images
    if image.ndim == 3 and image.shape[2] == 1:
        return image

    # RGBA — process RGB channels, preserve alpha
    if image.ndim == 3 and image.shape[2] == 4:
        alpha = image[:, :, 3]
        bgr = image[:, :, :3]
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (saturation / 100.0), 0, 255)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        return np.dstack([result, alpha])

    # BGR — standard case
    if image.ndim == 3 and image.shape[2] == 3:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (saturation / 100.0), 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    return image
