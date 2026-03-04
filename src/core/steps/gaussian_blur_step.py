import cv2
import numpy as np
from src.core.pipeline_step import PipelineStep, StepParameter
from typing import List


class GaussianBlurStep(PipelineStep):
    """Apply Gaussian blur to reduce noise."""

    def __init__(self):
        super().__init__()
        self.set_param("kernel_size", 5)
        self.set_param("sigma", 0)

    def define_params(self) -> List[StepParameter]:
        return [
            StepParameter(
                name="kernel_size",
                param_type="int",
                default=5,
                min=1,
                max=31,
                description="Kernel Size (odd)",
            ),
            StepParameter(
                name="sigma",
                param_type="float",
                default=0,
                min=0,
                max=10,
                description="Sigma (0 = auto)",
            ),
        ]

    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        k = self.get_param("kernel_size")
        sigma = self.get_param("sigma")
        # Ensure kernel size is odd
        if k % 2 == 0:
            k += 1
        return cv2.GaussianBlur(image, (k, k), sigma)
