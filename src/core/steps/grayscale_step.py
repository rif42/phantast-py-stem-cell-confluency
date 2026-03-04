import cv2
import numpy as np
from src.core.pipeline_step import PipelineStep


class GrayscaleStep(PipelineStep):
    """Convert image to grayscale."""

    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        # If already grayscale, return as-is
        if len(image.shape) == 2:
            return image
        # Convert BGR to grayscale
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
