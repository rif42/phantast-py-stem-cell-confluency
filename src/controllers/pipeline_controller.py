from PyQt6.QtCore import QObject, pyqtSignal
from src.models.pipeline_model import Pipeline, PipelineNode
from typing import Optional, Dict, Any

class PipelineController(QObject):
    pipeline_changed = pyqtSignal()  # Emitted on add, remove, reorder
    node_toggled = pyqtSignal(str, bool)  # node_id, is_enabled
    node_updated = pyqtSignal(str)  # node_id

    def __init__(self):
        super().__init__()
        self.pipeline = Pipeline()

    def add_node(self, node: PipelineNode):
        self.pipeline.nodes.append(node)
        self.pipeline_changed.emit()

    def remove_node(self, node_id: str):
        self.pipeline.nodes = [n for n in self.pipeline.nodes if n.id != node_id]
        self.pipeline_changed.emit()

    def get_node(self, node_id: str) -> Optional[PipelineNode]:
        for node in self.pipeline.nodes:
            if node.id == node_id:
                return node
        return None

    def toggle_node(self, node_id: str, enabled: bool):
        node = self.get_node(node_id)
        if node:
            node.enabled = enabled
            self.node_toggled.emit(node_id, enabled)

    def reorder_nodes(self, node_id: str, new_index: int):
        node = self.get_node(node_id)
        if not node:
            return

        current_index = self.pipeline.nodes.index(node)
        if current_index == new_index:
            return

        # Ensure index is within bounds
        new_index = max(0, min(new_index, len(self.pipeline.nodes) - 1))
        
        self.pipeline.nodes.pop(current_index)
        self.pipeline.nodes.insert(new_index, node)
        self.pipeline_changed.emit()

    def update_node_params(self, node_id: str, params: Dict[str, Any]):
        node = self.get_node(node_id)
        if node:
            node.parameters.update(params)
            self.node_updated.emit(node_id)
