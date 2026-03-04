import pytest
import numpy as np
from src.core.pipeline_step import PipelineStep, StepParameter


class DummyStep(PipelineStep):
    """Concrete implementation for testing."""

    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        return image


class TestPipelineStep:
    def test_abstract_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            PipelineStep()

    def test_step_parameter_creation(self):
        param = StepParameter(
            name="clip_limit",
            param_type="float",
            default=2.0,
            min=0.1,
            max=10.0,
            description="Clip Limit",
        )
        assert param.name == "clip_limit"
        assert param.default == 2.0
        assert param.min == 0.1
        assert param.max == 10.0

    def test_get_param_returns_default(self):
        step = DummyStep()
        assert step.get_param("nonexistent") is None

    def test_set_param_overrides(self):
        step = DummyStep()
        step.set_param("test", 42)
        assert step.get_param("test") == 42

    def test_enabled_property(self):
        step = DummyStep()
        assert step.enabled is True
        step.enabled = False
        assert step.enabled is False

    def test_name_property(self):
        step = DummyStep()
        assert step.name == "DummyStep"
