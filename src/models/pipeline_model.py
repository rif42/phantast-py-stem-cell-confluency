import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class PipelineNode:
    id: str
    type: str
    name: str
    description: str
    icon: str
    status: str
    enabled: bool
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize node to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "status": self.status,
            "enabled": self.enabled,
            "parameters": self.parameters,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineNode":
        """Deserialize node from dictionary."""
        return cls(
            id=data["id"],
            type=data["type"],
            name=data["name"],
            description=data.get("description", ""),
            icon=data.get("icon", ""),
            status=data.get("status", "ready"),
            enabled=data.get("enabled", True),
            parameters=data.get("parameters", {}),
        )


@dataclass
class Pipeline:
    id: str = ""
    name: str = "New Pipeline"
    nodes: List[PipelineNode] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize pipeline to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "nodes": [node.to_dict() for node in self.nodes],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pipeline":
        """Deserialize pipeline from dictionary."""
        nodes = [PipelineNode.from_dict(n) for n in data.get("nodes", [])]
        return cls(
            id=data.get("id", ""),
            name=data.get("name", "New Pipeline"),
            nodes=nodes,
        )

    def save(self, filepath: str):
        """Save pipeline to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "Pipeline":
        """Load pipeline from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def validate(self) -> List[str]:
        """Validate pipeline configuration. Returns list of errors."""
        errors = []

        if not self.name:
            errors.append("Pipeline name is required")

        for i, node in enumerate(self.nodes):
            if not node.id:
                errors.append(f"Node {i}: ID is required")
            if not node.type:
                errors.append(f"Node {i}: Type is required")

        return errors
