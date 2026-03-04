import pytest
import numpy as np
from src.core.pipeline import ImagePipeline
from src.core.pipeline_step import PipelineStep


class IdentityStep(PipelineStep):
    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        return image


class MultiplyStep(PipelineStep):
    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        return image * 2


class FailingStep(PipelineStep):
    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        raise ValueError("Test error")


class MetadataStep(PipelineStep):
    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        if "steps" not in metadata:
            metadata["steps"] = []
        metadata["steps"].append(self.name)
        return image


class TestImagePipeline:
    def test_add_step(self):
        pipeline = ImagePipeline()
        step = IdentityStep()
        pipeline.add_step(step)
        assert len(pipeline.steps) == 1

    def test_remove_step(self):
        pipeline = ImagePipeline()
        step = IdentityStep()
        pipeline.add_step(step)
        pipeline.remove_step(0)
        assert len(pipeline.steps) == 0

    def test_remove_step_invalid_index(self):
        pipeline = ImagePipeline()
        pipeline.remove_step(0)  # Should not raise
        assert len(pipeline.steps) == 0

    def test_move_step(self):
        pipeline = ImagePipeline()
        step1 = IdentityStep()
        step2 = MultiplyStep()
        pipeline.add_step(step1)
        pipeline.add_step(step2)
        pipeline.move_step(0, 1)
        assert pipeline.steps[0].name == "MultiplyStep"
        assert pipeline.steps[1].name == "IdentityStep"

    def test_clear(self):
        pipeline = ImagePipeline()
        pipeline.add_step(IdentityStep())
        pipeline.clear()
        assert len(pipeline.steps) == 0

    def test_execute_runs_steps(self):
        pipeline = ImagePipeline()
        pipeline.add_step(IdentityStep())
        input_img = np.array([1, 2, 3])
        result = pipeline.execute(input_img)
        np.testing.assert_array_equal(result, input_img)

    def test_execute_metadata_passed(self):
        pipeline = ImagePipeline()
        pipeline.add_step(MetadataStep())
        pipeline.add_step(MetadataStep())
        input_img = np.array([1, 2, 3])
        pipeline.execute(input_img)
        assert pipeline.get_metadata()["steps"] == ["MetadataStep", "MetadataStep"]

    def test_execute_disabled_step_skipped(self):
        pipeline = ImagePipeline()
        step = MetadataStep()
        step.enabled = False
        pipeline.add_step(step)
        input_img = np.array([1, 2, 3])
        pipeline.execute(input_img)
        assert "steps" not in pipeline.get_metadata()

    def test_execute_error_caught(self):
        pipeline = ImagePipeline()
        pipeline.add_step(FailingStep())
        input_img = np.array([1, 2, 3])
        result = pipeline.execute(input_img)
        np.testing.assert_array_equal(result, input_img)  # Pass-through on error
