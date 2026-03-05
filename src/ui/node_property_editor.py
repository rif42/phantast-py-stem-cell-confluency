import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QFrame,
    QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..controllers.main_controller import MainController
from ..core.parameter_schemas import get_node_spec, ParameterType


logger = logging.getLogger(__name__)


class NodePropertyEditor(QWidget):
    """
    Right panel widget for editing node properties.

    Dynamically generates editors based on node type.
    """

    parameter_changed = pyqtSignal(str, str, object)  # node_id, param_name, value

    def __init__(self, controller: MainController, parent=None):
        super().__init__(parent)

        self.controller = controller
        self._current_node_id: Optional[str] = None

        self._setup_ui()
        self._connect_signals()

        logger.info("NodePropertyEditor initialized")

    def _setup_ui(self):
        """Setup the editor UI."""
        self.setObjectName("nodePropertyEditor")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        # Content container
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_layout.setSpacing(12)

        scroll.setWidget(self.content)
        layout.addWidget(scroll)

        # Show empty state initially
        self._show_empty_state()

    def _connect_signals(self):
        """Connect to controller signals."""
        self.controller.node_selected.connect(self._on_node_selected)
        self.controller.node_parameter_changed.connect(self._on_parameter_changed)

    def _clear_content(self):
        """Clear all content widgets."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_empty_state(self):
        """Show empty state (no node selected)."""
        self._clear_content()
        self._current_node_id = None

        # Header
        header = QLabel("NODE PROPERTIES")
        header.setObjectName("panelHeader")
        self.content_layout.addWidget(header)

        # Empty message
        empty = QLabel("Select a node to edit its properties")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty.setStyleSheet("color: #5A6066; font-size: 12px; padding: 32px;")
        self.content_layout.addWidget(empty)

        self.content_layout.addStretch()

    def _on_node_selected(self, node_id: Optional[str]):
        """Handle node selection change."""
        if node_id is None:
            self._show_empty_state()
            return

        node_info = self.controller.get_node_info(node_id)
        if node_info is None:
            self._show_empty_state()
            return

        self._current_node_id = node_id
        self._show_node_editor(node_info)

    def _show_node_editor(self, node_info: dict):
        """Show editor for selected node."""
        self._clear_content()

        # Header
        header = QLabel("NODE PROPERTIES")
        header.setObjectName("panelHeader")
        self.content_layout.addWidget(header)

        self.content_layout.addSpacing(16)

        # Node info box
        info_box = QFrame()
        info_box.setObjectName("infoBox")
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(12, 12, 12, 12)

        name_label = QLabel(node_info["name"])
        name_label.setObjectName("nodeNameLabel")

        type_label = QLabel(f"Type: {node_info['type']}")
        type_label.setObjectName("nodeTypeLabel")

        desc_label = QLabel(node_info.get("description", ""))
        desc_label.setObjectName("nodeDescLabel")
        desc_label.setWordWrap(True)

        info_layout.addWidget(name_label)
        info_layout.addWidget(type_label)
        info_layout.addWidget(desc_label)

        self.content_layout.addWidget(info_box)
        self.content_layout.addSpacing(24)

        # Parameters section
        if node_info["parameters"]:
            params_header = QLabel("Parameters")
            params_header.setObjectName("sectionHeader")
            self.content_layout.addWidget(params_header)

            self.content_layout.addSpacing(12)

            # Get parameter specs
            spec = get_node_spec(node_info["type"])
            if spec:
                for param_name, value in node_info["parameters"].items():
                    param_spec = spec.get_parameter_spec(param_name)
                    if param_spec:
                        editor = self._create_parameter_editor(
                            node_info["id"], param_spec, value
                        )
                        if editor:
                            self.content_layout.addWidget(editor)
        else:
            # No parameters
            no_params = QLabel("No configurable parameters")
            no_params.setStyleSheet(
                "color: #9AA0A6; font-size: 12px; font-style: italic;"
            )
            self.content_layout.addWidget(no_params)

        self.content_layout.addStretch()

    def _create_parameter_editor(
        self, node_id: str, param_spec, current_value
    ) -> Optional[QWidget]:
        """Create an editor widget for a parameter."""
        container = QFrame()
        container.setObjectName("paramEditor")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(4)

        # Label
        label = QLabel(param_spec.name.replace("_", " ").title())
        label.setObjectName("paramLabel")
        layout.addWidget(label)

        # Editor based on type
        editor_widget = None

        if param_spec.param_type == ParameterType.INTEGER:
            editor_widget = self._create_int_editor(node_id, param_spec, current_value)
        elif param_spec.param_type == ParameterType.FLOAT:
            editor_widget = self._create_float_editor(
                node_id, param_spec, current_value
            )
        elif param_spec.param_type == ParameterType.TUPLE:
            # For tuple types, show as read-only for now
            editor_widget = QLabel(str(current_value))
            editor_widget.setObjectName("paramValue")
        else:
            # Default: show as label
            editor_widget = QLabel(str(current_value))
            editor_widget.setObjectName("paramValue")

        if editor_widget:
            layout.addWidget(editor_widget)

        # Description
        if param_spec.description:
            desc = QLabel(param_spec.description)
            desc.setObjectName("paramDesc")
            desc.setWordWrap(True)
            layout.addWidget(desc)

        return container

    def _create_int_editor(self, node_id: str, param_spec, value) -> QSpinBox:
        """Create integer spinbox editor."""
        spinbox = QSpinBox()
        spinbox.setObjectName("paramSpinbox")

        if param_spec.min_value is not None:
            spinbox.setMinimum(int(param_spec.min_value))
        else:
            spinbox.setMinimum(0)

        if param_spec.max_value is not None:
            spinbox.setMaximum(int(param_spec.max_value))
        else:
            spinbox.setMaximum(9999)

        if param_spec.step is not None:
            spinbox.setSingleStep(int(param_spec.step))

        spinbox.setValue(int(value))

        # Connect to controller
        spinbox.valueChanged.connect(
            lambda v: self._on_value_changed(node_id, param_spec.name, v)
        )

        return spinbox

    def _create_float_editor(self, node_id: str, param_spec, value) -> QDoubleSpinBox:
        """Create float spinbox editor."""
        spinbox = QDoubleSpinBox()
        spinbox.setObjectName("paramSpinbox")

        if param_spec.min_value is not None:
            spinbox.setMinimum(param_spec.min_value)
        else:
            spinbox.setMinimum(0.0)

        if param_spec.max_value is not None:
            spinbox.setMaximum(param_spec.max_value)
        else:
            spinbox.setMaximum(9999.0)

        if param_spec.step is not None:
            spinbox.setSingleStep(param_spec.step)
        else:
            spinbox.setSingleStep(0.1)

        spinbox.setDecimals(2)
        spinbox.setValue(float(value))

        # Connect to controller
        spinbox.valueChanged.connect(
            lambda v: self._on_value_changed(node_id, param_spec.name, v)
        )

        return spinbox

    def _on_value_changed(self, node_id: str, param_name: str, value):
        """Handle parameter value change."""
        self.controller.update_node_parameter(node_id, param_name, value)
        self.parameter_changed.emit(node_id, param_name, value)

    def _on_parameter_changed(self, node_id: str, param_name: str, value):
        """Handle parameter change from controller."""
        # Refresh if this is the current node
        if node_id == self._current_node_id:
            # In a full implementation, we would update just the changed editor
            pass

    def refresh(self):
        """Refresh the editor."""
        if self._current_node_id:
            node_info = self.controller.get_node_info(self._current_node_id)
            if node_info:
                self._show_node_editor(node_info)
            else:
                self._show_empty_state()
