import logging
import numpy as np
from src.core.pipeline_step import PipelineStep, StepParameter
from typing import List

logger = logging.getLogger(__name__)

# Try to import phantast, but allow graceful degradation
try:
    from phantast_confluency_corrected import process_phantast

    PHANTAST_AVAILABLE = True
except ImportError:
    PHANTAST_AVAILABLE = False
    logger.warning("PHANTAST module not available. PhantastStep will pass-through.")


class PhantastStep(PipelineStep):
    """
    Apply PHANTAST cell detection.
    Creates green overlay on detected cells and stores confluency in metadata.
    """

    def __init__(self):
        super().__init__()
        self.set_param("sigma", 4.0)
        self.set_param("epsilon", 0.05)

    def define_params(self) -> List[StepParameter]:
        return [
            StepParameter(
                name="sigma",
                param_type="float",
                default=4.0,
                min=0.1,
                max=20.0,
                description="Sigma",
            ),
            StepParameter(
                name="epsilon",
                param_type="float",
                default=0.05,
                min=0.001,
                max=1.0,
                description="Epsilon",
            ),
        ]

    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        if not PHANTAST_AVAILABLE:
            logger.warning("PHANTAST not available, skipping step")
            return image

        sigma = self.get_param("sigma")
        epsilon = self.get_param("epsilon")

        try:
            # Process image
            percentage, mask = process_phantast(image, sigma, epsilon)

            # Store results in metadata
            metadata["phantast_confluency"] = percentage
            metadata["phantast_mask"] = mask

            # Create green overlay on detected cells
            result = image.copy()
            if len(result.shape) == 2:
                result = np.stack([result] * 3, axis=-1)

            # Apply green overlay where mask is True
            result[mask] = [0, 255, 0]  # Green in BGR

            return result

        except Exception as e:
            logger.error(f"PHANTAST processing error: {e}")
            return image
