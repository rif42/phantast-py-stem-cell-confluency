"""
Parameter schemas and defaults for pipeline nodes.

This module defines the parameters each node type accepts,
along with their default values and validation rules.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable
from enum import Enum


class ParameterType(Enum):
    """Types of parameters supported."""

    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    STRING = "string"
    CHOICE = "choice"
    TUPLE = "tuple"


@dataclass
class ParameterSpec:
    """Specification for a single parameter."""

    name: str
    param_type: ParameterType
    default: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    choices: Optional[List[str]] = None
    description: str = ""

    def validate(self, value: Any) -> bool:
        """Validate a value against this spec."""
        if self.param_type == ParameterType.INTEGER:
            if not isinstance(value, int):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False

        elif self.param_type == ParameterType.FLOAT:
            if not isinstance(value, (int, float)):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False

        elif self.param_type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                return False

        elif self.param_type == ParameterType.STRING:
            if not isinstance(value, str):
                return False

        elif self.param_type == ParameterType.CHOICE:
            if self.choices is not None and value not in self.choices:
                return False

        elif self.param_type == ParameterType.TUPLE:
            if not isinstance(value, (list, tuple)):
                return False

        return True

    def clamp(self, value: Any) -> Any:
        """Clamp value to valid range."""
        if self.param_type in (ParameterType.INTEGER, ParameterType.FLOAT):
            if self.min_value is not None:
                value = max(value, self.min_value)
            if self.max_value is not None:
                value = min(value, self.max_value)
        return value


@dataclass
class NodeTypeSpec:
    """Specification for a node type."""

    type_id: str
    name: str
    description: str
    icon: str
    category: str
    parameters: List[ParameterSpec]

    def get_default_parameters(self) -> Dict[str, Any]:
        """Get dictionary of default parameter values."""
        return {p.name: p.default for p in self.parameters}

    def get_parameter_spec(self, name: str) -> Optional[ParameterSpec]:
        """Get spec for a specific parameter."""
        for p in self.parameters:
            if p.name == name:
                return p
        return None

    def validate_parameters(self, params: Dict[str, Any]) -> List[str]:
        """Validate a parameter dict. Returns list of error messages."""
        errors = []

        for spec in self.parameters:
            if spec.name in params:
                if not spec.validate(params[spec.name]):
                    errors.append(f"Invalid value for {spec.name}: {params[spec.name]}")
            else:
                # Use default if missing
                pass

        return errors


# =============================================================================
# NODE TYPE DEFINITIONS
# =============================================================================

# Input node - no parameters (informational only)
INPUT_NODE_SPEC = NodeTypeSpec(
    type_id="input",
    name="Input",
    description="Input image source",
    icon="📷",
    category="io",
    parameters=[],  # No parameters - uses loaded image
)

# Grayscale conversion node - no parameters
GRAYSCALE_NODE_SPEC = NodeTypeSpec(
    type_id="grayscale",
    name="Grayscale",
    description="Convert image to grayscale",
    icon="◑",
    category="processing",
    parameters=[],  # No configurable parameters
)

# Gaussian Blur node
GAUSSIAN_BLUR_NODE_SPEC = NodeTypeSpec(
    type_id="gaussian_blur",
    name="Gaussian Blur",
    description="Apply Gaussian blur to reduce noise",
    icon="◯",
    category="processing",
    parameters=[
        ParameterSpec(
            name="kernel_size",
            param_type=ParameterType.INTEGER,
            default=5,
            min_value=1,
            max_value=51,
            step=2,
            description="Kernel size (must be odd number)",
        ),
        ParameterSpec(
            name="sigma",
            param_type=ParameterType.FLOAT,
            default=1.0,
            min_value=0.1,
            max_value=10.0,
            step=0.1,
            description="Standard deviation (sigma)",
        ),
    ],
)

# CLAHE (Contrast Limited Adaptive Histogram Equalization) node
CLAHE_NODE_SPEC = NodeTypeSpec(
    type_id="clahe",
    name="CLAHE",
    description="Adaptive histogram equalization for contrast enhancement",
    icon="☀",
    category="processing",
    parameters=[
        ParameterSpec(
            name="clip_limit",
            param_type=ParameterType.FLOAT,
            default=2.0,
            min_value=1.0,
            max_value=40.0,
            step=0.5,
            description="Threshold for contrast limiting",
        ),
        ParameterSpec(
            name="grid_size",
            param_type=ParameterType.TUPLE,
            default=(8, 8),
            description="Size of grid for histogram equalization (width, height)",
        ),
    ],
)

# PHANTAST (Output) node
PHANTAST_NODE_SPEC = NodeTypeSpec(
    type_id="output",
    name="PHANTAST",
    description="Cell detection and analysis using PHANTAST algorithm",
    icon="🔬",
    category="io",
    parameters=[
        ParameterSpec(
            name="sigma",
            param_type=ParameterType.FLOAT,
            default=5.0,
            min_value=0.1,
            max_value=20.0,
            step=0.5,
            description="Gaussian smoothing sigma",
        ),
        ParameterSpec(
            name="epsilon",
            param_type=ParameterType.FLOAT,
            default=0.5,
            min_value=0.01,
            max_value=5.0,
            step=0.01,
            description="Morphological closing epsilon",
        ),
    ],
)

# =============================================================================
# REGISTRY
# =============================================================================

NODE_TYPE_SPECS: Dict[str, NodeTypeSpec] = {
    "input": INPUT_NODE_SPEC,
    "grayscale": GRAYSCALE_NODE_SPEC,
    "gaussian_blur": GAUSSIAN_BLUR_NODE_SPEC,
    "clahe": CLAHE_NODE_SPEC,
    "output": PHANTAST_NODE_SPEC,
}

PROCESSING_NODE_TYPES = ["grayscale", "gaussian_blur", "clahe"]


def get_node_spec(node_type: str) -> Optional[NodeTypeSpec]:
    """Get specification for a node type."""
    return NODE_TYPE_SPECS.get(node_type)


def get_processing_node_specs() -> List[NodeTypeSpec]:
    """Get specifications for all processing nodes."""
    return [NODE_TYPE_SPECS[t] for t in PROCESSING_NODE_TYPES]


def create_default_node_parameters(node_type: str) -> Dict[str, Any]:
    """Create default parameters for a node type."""
    spec = get_node_spec(node_type)
    if spec:
        return spec.get_default_parameters()
    return {}


def validate_node_parameters(node_type: str, parameters: Dict[str, Any]) -> List[str]:
    """Validate parameters for a node type."""
    spec = get_node_spec(node_type)
    if spec:
        return spec.validate_parameters(parameters)
    return [f"Unknown node type: {node_type}"]


def get_available_node_types() -> List[str]:
    """Get list of available node type IDs."""
    return list(NODE_TYPE_SPECS.keys())


def get_available_processing_nodes() -> List[Dict[str, str]]:
    """Get list of available processing nodes for UI."""
    return [
        {
            "type_id": spec.type_id,
            "name": spec.name,
            "description": spec.description,
            "icon": spec.icon,
        }
        for spec in get_processing_node_specs()
    ]
