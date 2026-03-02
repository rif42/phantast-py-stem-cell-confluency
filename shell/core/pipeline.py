
import copy
import numpy as np
from .steps import PipelineStep

class ImagePipeline:
    """
    Manages a sequence of processing steps.
    """
    def __init__(self):
        self.steps = []
        self.metadata = {} # Shared data between steps (e.g. masks, metrics)

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
        self.steps = []

    def execute(self, image: np.ndarray) -> np.ndarray:
        """
        Run the pipeline on an image.
        Returns the processed image.
        """
        current_image = image.copy()
        self.metadata = {} # Reset metadata
        
        for step in self.steps:
            if step.enabled:
                try:
                    current_image = step.process(current_image, self.metadata)
                except Exception as e:
                    print(f"Error in step {step.name}: {e}")
                    # Decide whether to continue or abort. 
                    # For now, continue with previous image or stop?
                    # Let's clean up semantics later. 
                    # Returning partial result might be better than crash.
                    pass
        
        return current_image

    def get_metadata(self):
        return self.metadata
