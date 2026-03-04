from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Dict, Optional
import numpy as np


@dataclass
class StepParameter:
    """Metadata for a step parameter to generate UI controls."""

    name: str
    param_type: str  # 'float', 'int', 'bool', 'choice'
    default: Any
    min: Optional[Any] = None
    max: Optional[Any] = None
    description: str = ""


class PipelineStep(ABC):
    """Abstract base class for a processing step."""

    def __init__(self):
        self.enabled = True
        self._params: Dict[str, Any] = {}

    @abstractmethod
    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        """
        Process the image.

        Args:
            image: Input image (numpy array, usually BGR or Gray).
            metadata: Dict to store/retrieve inter-step data (e.g. masks, metrics).

        Returns:
            Processed image.
        """
        pass

    def define_params(self) -> List[StepParameter]:
        """Override to return a list of StepParameter objects."""
        return []

    def get_param(self, name: str) -> Any:
        """Get current value of a parameter."""
        if name in self._params:
            return self._params[name]
        for p in self.define_params():
            if p.name == name:
                return p.default
        return None

    def set_param(self, name: str, value: Any):
        """Set a parameter value."""
        self._params[name] = value

    @property
    def name(self) -> str:
        """Return the step name (class name by default)."""
        return self.__class__.__name__
