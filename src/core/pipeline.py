import logging
from typing import List
import numpy as np
from .pipeline_step import PipelineStep

logger = logging.getLogger(__name__)


class ImagePipeline:
    """Manages a sequence of processing steps."""

    def __init__(self):
        self.steps: List[PipelineStep] = []
        self._metadata: dict = {}

    def add_step(self, step: PipelineStep):
        """Add a step to the end of the pipeline."""
        self.steps.append(step)

    def remove_step(self, index: int):
        """Remove a step by index."""
        if 0 <= index < len(self.steps):
            self.steps.pop(index)

    def move_step(self, from_index: int, to_index: int):
        """Move a step to a new position."""
        if 0 <= from_index < len(self.steps) and 0 <= to_index < len(self.steps):
            step = self.steps.pop(from_index)
            self.steps.insert(to_index, step)

    def clear(self):
        """Remove all steps."""
        self.steps.clear()

    def execute(self, image: np.ndarray) -> np.ndarray:
        """
        Run the pipeline on an image.

        Args:
            image: Input image as numpy array.

        Returns:
            Processed image.
        """
        current_image = image.copy()
        self._metadata = {}  # Reset metadata

        for step in self.steps:
            if step.enabled:
                try:
                    current_image = step.process(current_image, self._metadata)
                except Exception as e:
                    logger.error(f"Error in step {step.name}: {e}")
                    # Continue with current image on error

        return current_image

    def get_metadata(self) -> dict:
        """Get the metadata dict from last execution."""
        return self._metadata
