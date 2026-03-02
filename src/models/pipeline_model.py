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

@dataclass
class Pipeline:
    id: str = ""
    name: str = "New Pipeline"
    nodes: List[PipelineNode] = field(default_factory=list)
