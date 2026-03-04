import pytest
import tempfile
import os
from src.models.pipeline_model import Pipeline, PipelineNode


class TestPipelinePersistence:
    def test_node_to_dict(self):
        """Test PipelineNode serialization."""
        node = PipelineNode(
            id="step1",
            type="GrayscaleStep",
            name="Convert to Grayscale",
            description="Converts image to grayscale",
            icon="grayscale.png",
            status="ready",
            enabled=True,
            parameters={"invert": False},
        )

        data = node.to_dict()
        assert data["id"] == "step1"
        assert data["type"] == "GrayscaleStep"
        assert data["parameters"]["invert"] is False

    def test_node_from_dict(self):
        """Test PipelineNode deserialization."""
        data = {
            "id": "step1",
            "type": "GrayscaleStep",
            "name": "Convert to Grayscale",
            "description": "Converts image to grayscale",
            "icon": "grayscale.png",
            "status": "ready",
            "enabled": True,
            "parameters": {"invert": False},
        }

        node = PipelineNode.from_dict(data)
        assert node.id == "step1"
        assert node.type == "GrayscaleStep"
        assert node.parameters["invert"] is False

    def test_pipeline_to_dict(self):
        """Test Pipeline serialization."""
        pipeline = Pipeline(
            id="pipe1",
            name="My Pipeline",
            nodes=[
                PipelineNode(
                    id="step1",
                    type="GrayscaleStep",
                    name="Grayscale",
                    description="",
                    icon="",
                    status="ready",
                    enabled=True,
                    parameters={},
                )
            ],
        )

        data = pipeline.to_dict()
        assert data["id"] == "pipe1"
        assert data["name"] == "My Pipeline"
        assert len(data["nodes"]) == 1

    def test_pipeline_from_dict(self):
        """Test Pipeline deserialization."""
        data = {
            "id": "pipe1",
            "name": "My Pipeline",
            "nodes": [
                {
                    "id": "step1",
                    "type": "GrayscaleStep",
                    "name": "Grayscale",
                    "description": "",
                    "icon": "",
                    "status": "ready",
                    "enabled": True,
                    "parameters": {},
                }
            ],
        }

        pipeline = Pipeline.from_dict(data)
        assert pipeline.id == "pipe1"
        assert pipeline.name == "My Pipeline"
        assert len(pipeline.nodes) == 1
        assert pipeline.nodes[0].type == "GrayscaleStep"

    def test_save_and_load(self):
        """Test saving and loading pipeline."""
        pipeline = Pipeline(
            id="test-pipe",
            name="Test Pipeline",
            nodes=[
                PipelineNode(
                    id="step1",
                    type="GrayscaleStep",
                    name="Grayscale",
                    description="",
                    icon="",
                    status="ready",
                    enabled=True,
                    parameters={},
                )
            ],
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            pipeline.save(filepath)
            loaded = Pipeline.load(filepath)

            assert loaded.id == pipeline.id
            assert loaded.name == pipeline.name
            assert len(loaded.nodes) == len(pipeline.nodes)
            assert loaded.nodes[0].id == pipeline.nodes[0].id
        finally:
            os.unlink(filepath)

    def test_validate_empty_name(self):
        """Test validation catches empty name."""
        pipeline = Pipeline(name="")
        errors = pipeline.validate()
        assert "Pipeline name is required" in errors

    def test_validate_missing_node_id(self):
        """Test validation catches missing node ID."""
        pipeline = Pipeline(
            name="Test",
            nodes=[
                PipelineNode(
                    id="",
                    type="GrayscaleStep",
                    name="",
                    description="",
                    icon="",
                    status="ready",
                    enabled=True,
                )
            ],
        )
        errors = pipeline.validate()
        assert any("ID is required" in e for e in errors)
