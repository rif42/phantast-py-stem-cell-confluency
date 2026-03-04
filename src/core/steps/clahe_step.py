import cv2
import numpy as np
from src.core.pipeline_step import PipelineStep, StepParameter
from typing import List


class ClaheStep(PipelineStep):
    """Apply Contrast Limited Adaptive Histogram Equalization."""

    def __init__(self):
        super().__init__()
        self.set_param("clip_limit", 2.0)
        self.set_param("tile_grid_size", 8)

    def define_params(self) -> List[StepParameter]:
        return [
            StepParameter(
                name="clip_limit",
                param_type="float",
                default=2.0,
                min=0.1,
                max=10.0,
                description="Clip Limit",
            ),
            StepParameter(
                name="tile_grid_size",
                param_type="int",
                default=8,
                min=2,
                max=32,
                description="Tile Grid Size",
            ),
        ]

    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        clip_limit = self.get_param("clip_limit")
        tile_size = self.get_param("tile_grid_size")

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        clahe = cv2.createCLAHE(
            clipLimit=clip_limit, tileGridSize=(tile_size, tile_size)
        )
        return clahe.apply(gray)
