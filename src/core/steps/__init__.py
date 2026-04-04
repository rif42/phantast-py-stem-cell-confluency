"""Pipeline step registration system.

This module provides a decorator-based registration system for image processing steps.
Each step can be registered and later discovered by the pipeline system.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union, overload
import numpy as np


@dataclass
class StepParameter:
    """Defines a parameter for a processing step.

    Attributes:
        name: Parameter name (used as key in kwargs)
        type: Parameter type ("float", "int", "bool", "enum")
        default: Default value for the parameter
        min: Minimum allowed value (for numeric types)
        max: Maximum allowed value (for numeric types)
        step: Step size for increment/decrement (for numeric types)
        description: Human-readable description of the parameter
        options: List of options for enum type
    """

    name: str
    type: str  # "float", "int", "bool", "enum"
    default: Any
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    step: Optional[Union[int, float]] = None
    description: str = ""
    options: Optional[List[str]] = None


@dataclass
class StepMetadata:
    """Metadata for a registered processing step.

    Attributes:
        name: Unique step identifier
        description: Human-readable description
        icon: Emoji or icon string for UI
        parameters: List of StepParameter definitions
        process: The processing function
        category: Category for grouping in UI (e.g. "image_processing", "segmentation")
    """

    name: str
    description: str
    icon: str
    parameters: List[StepParameter]
    process: Callable[..., np.ndarray]
    category: str = "image_processing"


# Global registry of processing steps
STEP_REGISTRY: Dict[str, StepMetadata] = {}


@overload
def register_step(func: Callable[..., np.ndarray]) -> Callable[..., np.ndarray]: ...


@overload
def register_step(
    name: Optional[str] = None,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    parameters: Optional[List[StepParameter]] = None,
) -> Callable[[Callable[..., np.ndarray]], Callable[..., np.ndarray]]: ...


def register_step(
    name: Optional[Union[str, Callable[..., np.ndarray]]] = None,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    parameters: Optional[List[StepParameter]] = None,
) -> Union[
    Callable[..., np.ndarray],
    Callable[[Callable[..., np.ndarray]], Callable[..., np.ndarray]],
]:
    """Decorator to register a processing step.

    Can be used in two ways:
    1. With arguments: @register_step(name="custom", ...)
    2. Without arguments (auto-detect from module globals): @register_step

    When used without arguments, the decorator looks for module-level constants:
    - STEP_NAME: str
    - STEP_DESCRIPTION: str
    - STEP_ICON: str
    - STEP_PARAMETERS: List[StepParameter]

    Args:
        name: Unique step name (optional if STEP_NAME is defined)
        description: Step description (optional if STEP_DESCRIPTION is defined)
        icon: Icon string (optional if STEP_ICON is defined)
        parameters: List of parameters (optional if STEP_PARAMETERS is defined)

    Returns:
        Decorated function or decorator factory

    Example:
        @register_step
        def process(image, clip_limit=2.0):
            # ... processing logic ...
            return image
    """

    def decorator(func: Callable[..., np.ndarray]) -> Callable[..., np.ndarray]:
        # Get metadata from module globals or explicit arguments
        import inspect

        module = inspect.getmodule(func)

        step_name = name or getattr(module, "STEP_NAME", func.__name__)
        step_description = description or getattr(
            module, "STEP_DESCRIPTION", func.__doc__ or ""
        )
        step_icon = icon or getattr(module, "STEP_ICON", "⚙️")
        step_params = parameters or getattr(module, "STEP_PARAMETERS", [])
        step_category = getattr(module, "STEP_CATEGORY", "image_processing")

        # Create metadata
        metadata = StepMetadata(
            name=step_name,
            description=step_description,
            icon=step_icon,
            parameters=step_params,
            process=func,
            category=step_category,
        )

        # Register
        STEP_REGISTRY[step_name] = metadata

        # Mark function as registered
        setattr(func, "_step_metadata", metadata)
        setattr(func, "_step_name", step_name)

        return func

    # Handle both @register_step and @register_step(...) syntax
    if callable(name):
        # Used as @register_step without parentheses
        func = name
        name = None  # type: ignore[assignment]
        return decorator(func)

    return decorator


def get_step(name: str) -> Optional[StepMetadata]:
    """Get step metadata by name.

    Args:
        name: Step name

    Returns:
        StepMetadata or None if not found
    """
    return STEP_REGISTRY.get(name)


def list_steps() -> List[str]:
    """List all registered step names.

    Returns:
        List of step names
    """
    return list(STEP_REGISTRY.keys())


def clear_registry():
    """Clear all registered steps. Useful for testing."""
    STEP_REGISTRY.clear()


# Auto-import steps to register them in STEP_REGISTRY
try:
    from . import clahe_step, grayscale_step, crop_step, phantast_step, saturation_step
except ImportError:
    pass  # Steps may not be available in all environments

# Export symbols
__all__ = [
    "StepParameter",
    "StepMetadata",
    "STEP_REGISTRY",
    "register_step",
    "get_step",
    "list_steps",
    "clear_registry",
]
