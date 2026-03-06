import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
)

# Import our custom components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.ui.pipeline_view import PipelineConstructionWidget
from src.controllers.pipeline_controller import PipelineController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.resize(1300, 850)

        # Core Container
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        self.setup_header()

        self.load_views()

    def setup_header(self):
        header = QFrame()
        header.setObjectName("AppHeader")
        header.setFixedHeight(56)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        # Left side
        logo = QLabel("🔬")
        logo.setObjectName("appLogo")

        title = QLabel("Phantast Lab")
        title.setObjectName("appTitle")

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()

        # Right side -> Avatar
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setObjectName("appAvatar")
        layout.addWidget(avatar)

        self.main_layout.addWidget(header)

    def load_views(self):
        # Create Pipeline Construction view
        self.view_pipeline = PipelineConstructionWidget()
        self.pipeline_controller = PipelineController()

        # Wire up controller to view signals
        self.view_pipeline.add_step.connect(self._on_add_step)
        self.view_pipeline.toggle_node.connect(self._on_toggle_node)
        self.view_pipeline.delete_node.connect(self._on_delete_node)
        self.view_pipeline.node_reordered.connect(self._on_node_reordered)
        self.view_pipeline.node_selected.connect(self._on_node_selected)
        self.pipeline_controller.pipeline_changed.connect(self._on_pipeline_changed)

        # Add pipeline view to main layout
        self.main_layout.addWidget(self.view_pipeline)

    def _refresh_pipeline_view(self):
        """Refresh the pipeline view from controller data."""
        # Convert Pipeline dataclass to dict for view
        pipeline_dict = {
            "id": self.pipeline_controller.pipeline.id,
            "name": self.pipeline_controller.pipeline.name,
            "nodes": [],
        }
        for node in self.pipeline_controller.pipeline.nodes:
            node_dict = {
                "id": node.id,
                "type": node.type,
                "name": node.name,
                "description": node.description,
                "icon": node.icon,
                "status": node.status,
                "enabled": node.enabled,
                "parameters": node.parameters,
            }
            pipeline_dict["nodes"].append(node_dict)

        self.view_pipeline.pipeline = pipeline_dict
        self.view_pipeline.render_nodes()

    def _on_add_step(self, step_type: str):
        """Handle add step request from view."""
        from src.models.pipeline_model import PipelineNode
        import uuid
        from src.core.steps import STEP_REGISTRY

        if step_type not in STEP_REGISTRY:
            print(f"Unknown step type: {step_type}")
            return

        step_meta = STEP_REGISTRY[step_type]

        # Create default parameters from step definition
        default_params = {}
        for param in step_meta.parameters:
            default_params[param.name] = param.default

        node = PipelineNode(
            id=str(uuid.uuid4()),
            type=step_type,
            name=step_meta.name,
            description=step_meta.description,
            icon=step_meta.icon,
            status="ready",
            enabled=True,
            parameters=default_params,
        )

        self.pipeline_controller.add_node(node)
        self._refresh_pipeline_view()

    def _on_toggle_node(self, node_id: str, enabled: bool):
        """Handle node toggle request."""
        self.pipeline_controller.toggle_node(node_id, enabled)

    def _on_delete_node(self, node_id: str):
        """Handle node deletion request."""
        self.pipeline_controller.remove_node(node_id)
        self._refresh_pipeline_view()

    def _on_node_reordered(self, node_id: str, new_index: int):
        """Handle node reorder request."""
        self.pipeline_controller.reorder_nodes(node_id, new_index)
        self._refresh_pipeline_view()

    def _on_node_selected(self, node_id: str):
        """Handle node selection."""
        self.view_pipeline.active_node_id = node_id
        self.view_pipeline.update_right_panel()

    def _on_pipeline_changed(self):
        """Handle pipeline changes."""
        self._refresh_pipeline_view()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
