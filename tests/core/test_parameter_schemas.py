import pytest
from src.core.parameter_schemas import (
    ParameterSpec,
    ParameterType,
    NodeTypeSpec,
    get_node_spec,
    create_default_node_parameters,
    validate_node_parameters,
    get_available_node_types,
    get_available_processing_nodes,
    GRAYSCALE_NODE_SPEC,
    GAUSSIAN_BLUR_NODE_SPEC,
    CLAHE_NODE_SPEC,
    PHANTAST_NODE_SPEC,
)


class TestParameterSpec:
    """Test ParameterSpec class."""

    def test_integer_validation_valid(self):
        """Test valid integer values."""
        spec = ParameterSpec(
            name="test",
            param_type=ParameterType.INTEGER,
            default=5,
            min_value=1,
            max_value=10,
        )

        assert spec.validate(5) is True
        assert spec.validate(1) is True
        assert spec.validate(10) is True

    def test_integer_validation_invalid(self):
        """Test invalid integer values."""
        spec = ParameterSpec(
            name="test",
            param_type=ParameterType.INTEGER,
            default=5,
            min_value=1,
            max_value=10,
        )

        assert spec.validate(0) is False
        assert spec.validate(11) is False
        assert spec.validate(5.5) is False
        assert spec.validate("5") is False

    def test_float_validation(self):
        """Test float parameter validation."""
        spec = ParameterSpec(
            name="test",
            param_type=ParameterType.FLOAT,
            default=1.5,
            min_value=0.0,
            max_value=10.0,
        )

        assert spec.validate(1.5) is True
        assert spec.validate(5) is True  # Int is valid for float
        assert spec.validate(-1.0) is False
        assert spec.validate(11.0) is False

    def test_boolean_validation(self):
        """Test boolean parameter validation."""
        spec = ParameterSpec(
            name="test",
            param_type=ParameterType.BOOLEAN,
            default=True,
        )

        assert spec.validate(True) is True
        assert spec.validate(False) is True
        assert spec.validate(1) is False
        assert spec.validate("true") is False

    def test_choice_validation(self):
        """Test choice parameter validation."""
        spec = ParameterSpec(
            name="test",
            param_type=ParameterType.CHOICE,
            default="option1",
            choices=["option1", "option2", "option3"],
        )

        assert spec.validate("option1") is True
        assert spec.validate("option2") is True
        assert spec.validate("invalid") is False

    def test_clamp_value(self):
        """Test value clamping."""
        spec = ParameterSpec(
            name="test",
            param_type=ParameterType.INTEGER,
            default=5,
            min_value=0,
            max_value=10,
        )

        assert spec.clamp(-5) == 0
        assert spec.clamp(15) == 10
        assert spec.clamp(5) == 5


class TestNodeTypeSpec:
    """Test NodeTypeSpec class."""

    def test_get_default_parameters(self):
        """Test getting default parameters."""
        spec = NodeTypeSpec(
            type_id="test",
            name="Test",
            description="Test node",
            icon="",
            category="test",
            parameters=[
                ParameterSpec(
                    name="param1",
                    param_type=ParameterType.INTEGER,
                    default=10,
                ),
                ParameterSpec(
                    name="param2",
                    param_type=ParameterType.FLOAT,
                    default=2.5,
                ),
            ],
        )

        defaults = spec.get_default_parameters()

        assert defaults["param1"] == 10
        assert defaults["param2"] == 2.5

    def test_get_parameter_spec(self):
        """Test getting parameter specification."""
        param_spec = ParameterSpec(
            name="test_param",
            param_type=ParameterType.INTEGER,
            default=5,
        )

        spec = NodeTypeSpec(
            type_id="test",
            name="Test",
            description="Test node",
            icon="",
            category="test",
            parameters=[param_spec],
        )

        found = spec.get_parameter_spec("test_param")
        assert found is not None
        assert found.name == "test_param"

        not_found = spec.get_parameter_spec("nonexistent")
        assert not_found is None


class TestGrayscaleNodeSpec:
    """Test Grayscale node specification."""

    def test_spec_exists(self):
        """Test that grayscale spec exists."""
        assert GRAYSCALE_NODE_SPEC is not None
        assert GRAYSCALE_NODE_SPEC.type_id == "grayscale"
        assert GRAYSCALE_NODE_SPEC.name == "Grayscale"

    def test_no_parameters(self):
        """Test grayscale has no parameters."""
        assert len(GRAYSCALE_NODE_SPEC.parameters) == 0
        assert GRAYSCALE_NODE_SPEC.get_default_parameters() == {}


class TestGaussianBlurNodeSpec:
    """Test Gaussian Blur node specification."""

    def test_spec_exists(self):
        """Test that Gaussian blur spec exists."""
        assert GAUSSIAN_BLUR_NODE_SPEC is not None
        assert GAUSSIAN_BLUR_NODE_SPEC.type_id == "gaussian_blur"

    def test_has_kernel_size_param(self):
        """Test kernel_size parameter."""
        spec = GAUSSIAN_BLUR_NODE_SPEC.get_parameter_spec("kernel_size")
        assert spec is not None
        assert spec.param_type == ParameterType.INTEGER
        assert spec.default == 5
        assert spec.min_value == 1
        assert spec.max_value == 51

    def test_has_sigma_param(self):
        """Test sigma parameter."""
        spec = GAUSSIAN_BLUR_NODE_SPEC.get_parameter_spec("sigma")
        assert spec is not None
        assert spec.param_type == ParameterType.FLOAT
        assert spec.default == 1.0
        assert spec.min_value == 0.1
        assert spec.max_value == 10.0

    def test_default_parameters(self):
        """Test default parameters."""
        defaults = GAUSSIAN_BLUR_NODE_SPEC.get_default_parameters()
        assert defaults["kernel_size"] == 5
        assert defaults["sigma"] == 1.0


class TestClaheNodeSpec:
    """Test CLAHE node specification."""

    def test_spec_exists(self):
        """Test that CLAHE spec exists."""
        assert CLAHE_NODE_SPEC is not None
        assert CLAHE_NODE_SPEC.type_id == "clahe"

    def test_has_clip_limit_param(self):
        """Test clip_limit parameter."""
        spec = CLAHE_NODE_SPEC.get_parameter_spec("clip_limit")
        assert spec is not None
        assert spec.param_type == ParameterType.FLOAT
        assert spec.default == 2.0

    def test_has_grid_size_param(self):
        """Test grid_size parameter."""
        spec = CLAHE_NODE_SPEC.get_parameter_spec("grid_size")
        assert spec is not None
        assert spec.param_type == ParameterType.TUPLE
        assert spec.default == (8, 8)


class TestPhantastNodeSpec:
    """Test PHANTAST node specification."""

    def test_spec_exists(self):
        """Test that PHANTAST spec exists."""
        assert PHANTAST_NODE_SPEC is not None
        assert PHANTAST_NODE_SPEC.type_id == "output"
        assert "PHANTAST" in PHANTAST_NODE_SPEC.name

    def test_has_sigma_param(self):
        """Test sigma parameter."""
        spec = PHANTAST_NODE_SPEC.get_parameter_spec("sigma")
        assert spec is not None
        assert spec.default == 5.0

    def test_has_epsilon_param(self):
        """Test epsilon parameter."""
        spec = PHANTAST_NODE_SPEC.get_parameter_spec("epsilon")
        assert spec is not None
        assert spec.default == 0.5


class TestRegistryFunctions:
    """Test registry helper functions."""

    def test_get_node_spec_existing(self):
        """Test getting spec for existing node type."""
        spec = get_node_spec("grayscale")
        assert spec is not None
        assert spec.type_id == "grayscale"

    def test_get_node_spec_nonexistent(self):
        """Test getting spec for non-existent node type."""
        spec = get_node_spec("nonexistent")
        assert spec is None

    def test_create_default_parameters(self):
        """Test creating default parameters."""
        params = create_default_node_parameters("gaussian_blur")
        assert "kernel_size" in params
        assert "sigma" in params
        assert params["kernel_size"] == 5

    def test_create_default_parameters_unknown_type(self):
        """Test creating defaults for unknown type returns empty."""
        params = create_default_node_parameters("unknown")
        assert params == {}

    def test_validate_node_parameters(self):
        """Test validating node parameters."""
        errors = validate_node_parameters(
            "gaussian_blur",
            {
                "kernel_size": 100,  # Invalid - too high
            },
        )
        assert len(errors) > 0

    def test_get_available_node_types(self):
        """Test getting list of available node types."""
        types = get_available_node_types()
        assert "input" in types
        assert "output" in types
        assert "grayscale" in types
        assert "gaussian_blur" in types
        assert "clahe" in types

    def test_get_available_processing_nodes(self):
        """Test getting processing nodes for UI."""
        nodes = get_available_processing_nodes()
        assert len(nodes) == 3  # grayscale, gaussian_blur, clahe

        type_ids = [n["type_id"] for n in nodes]
        assert "grayscale" in type_ids
        assert "gaussian_blur" in type_ids
        assert "clahe" in type_ids

        # Check structure
        for node in nodes:
            assert "type_id" in node
            assert "name" in node
            assert "description" in node
            assert "icon" in node
