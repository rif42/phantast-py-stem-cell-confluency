import logging
from typing import Optional, Callable

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QFrame,
    QScrollArea,
    QMenu,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QMimeData
from PyQt6.QtGui import QPainter, QColor, QDrag

from ..controllers.main_controller import MainController
from ..core.parameter_schemas import get_available_processing_nodes


logger = logging.getLogger(__name__)


class ToggleSwitch(QPushButton):
    """A custom toggle switch styled for the node."""

    def __init__(self, checked=True, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedSize(36, 20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Colors from design system
        bg_color = QColor("#00B884") if self.isChecked() else QColor("#2D3336")
        handle_color = QColor("#FFFFFF")

        # Draw background
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 10, 10)

        # Draw handle
        handle_x = self.width() - 18 if self.isChecked() else 2
        painter.setBrush(handle_color)
        painter.drawEllipse(handle_x, 2, 16, 16)
        painter.end()


class PipelineNodeWidget(QFrame):
    """A single node in the pipeline stack with unified interface integration."""

    clicked = pyqtSignal(str)  # node_id
    toggled = pyqtSignal(str, bool)  # node_id, checked
    deleted = pyqtSignal(str)  # node_id

    def __init__(self, node_data: dict, controller: MainController, parent=None):
        super().__init__(parent)

        self.node_data = node_data
        self.node_id = node_data.get("id", "")
        self.controller = controller

        # Determine draggability based on type
        self.ntype = self.node_data.get("type", "")
        self.is_draggable = self.ntype not in ["input", "output"]
        self.is_removable = self.ntype not in ["input", "output"]
        self.is_toggleable = self.ntype not in ["input", "output"]

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        """Setup the node UI."""
        self.setFixedHeight(72)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Left Icon
        icon_frame = QFrame()
        icon_frame.setFixedSize(32, 32)
        icon_frame.setStyleSheet(
            "background-color: #2D3336; border-radius: 4px; border: none;"
        )
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(self.node_data.get("icon", "⚙️"))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_frame)

        # Middle Details
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(2)

        name_label = QLabel(self.node_data.get("name", "Process Node"))
        name_label.setObjectName("nodeName")

        desc_label = QLabel(self.node_data.get("description", ""))
        desc_label.setObjectName("nodeDesc")

        details_layout.addWidget(name_label)
        details_layout.addWidget(desc_label)
        layout.addLayout(details_layout, stretch=1)

        # Right Actions
        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Badge based on type
        badge_text = "PROCESS"
        badge_color = "#E8A317"

        if self.ntype == "input":
            badge_text = "INPUT"
            badge_color = "#3B82F6"
        elif self.ntype == "output":
            badge_text = "OUTPUT"
            badge_color = "#E8A317"

        badge = QLabel(badge_text)
        badge.setObjectName("nodeBadge")
        badge.setStyleSheet(f"background-color: {badge_color}33; color: {badge_color};")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        actions_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignRight)

        # Toggle switch (only for toggleable nodes)
        if self.is_toggleable:
            switch = ToggleSwitch(self.node_data.get("enabled", True))
            switch.toggled.connect(self._on_toggle)
            actions_layout.addWidget(switch, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(actions_layout)

    def _apply_style(self):
        """Apply dynamic styling."""
        # Check if this node is selected
        is_selected = self.controller.selected_node_id == self.node_id

        # Determine border color
        border_color = "#2D3336"
        if is_selected:
            border_color = "#00B884"
        elif self.ntype == "input":
            border_color = "#3B82F6"
        elif self.ntype == "output":
            border_color = "#E8A317"

        self.setObjectName("nodeCardSelected" if is_selected else "nodeCard")
        self.setStyleSheet(f"""
            #nodeCard, #nodeCardSelected {{
                background-color: transparent;
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            #nodeCard:hover {{
                background-color: #1E2224;
            }}
            #nodeName {{
                color: #E8EAED;
                font-size: 13px;
                font-weight: 600;
            }}
            #nodeDesc {{
                color: #9AA0A6;
                font-size: 11px;
            }}
            #nodeBadge {{
                font-size: 9px;
                font-weight: bold;
                border-radius: 2px;
                padding: 2px 4px;
            }}
        """)

    def _on_toggle(self, checked: bool):
        """Handle toggle switch."""
        self.toggled.emit(self.node_id, checked)

    def mousePressEvent(self, event):
        """Handle mouse press for selection and drag initiation."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
            self.clicked.emit(self.node_id)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle drag initiation."""
        if not self.is_draggable:
            return

        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        # Check drag distance
        if (event.pos() - self.drag_start_position).manhattanLength() < 5:
            return

        # Create drag
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.node_id)
        drag.setMimeData(mime_data)

        # Set drag pixmap
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        drag.exec(Qt.DropAction.MoveAction)

    def contextMenuEvent(self, event):
        """Show context menu for deletable nodes."""
        if not self.is_removable:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E2224;
                color: #E8EAED;
                border: 1px solid #2D3336;
            }
            QMenu::item:selected {
                background-color: #2D3336;
            }
        """)

        delete_action = menu.addAction("Delete Step")
        action = menu.exec(self.mapToGlobal(event.pos()))

        if action == delete_action:
            self.deleted.emit(self.node_id)

    def refresh(self):
        """Refresh styling (call when selection changes)."""
        self._apply_style()


class PipelineStackWidget(QWidget):
    """
    Left panel widget showing the pipeline stack.

    Integrates with MainController for state management.
    Shows Input -> [middle nodes] -> Output with drag-drop reordering.
    """

    node_selected = pyqtSignal(str)

    def __init__(self, controller: MainController, parent=None):
        super().__init__(parent)

        self.controller = controller
        self._node_widgets: dict[str, PipelineNodeWidget] = {}

        self._setup_ui()
        self._connect_signals()
        self._refresh_nodes()

        logger.info("PipelineStackWidget initialized")

    def _setup_ui(self):
        """Setup the widget UI."""
        self.setObjectName("pipelineStackWidget")
        self.setMinimumWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # Header with Add button
        header_layout = QHBoxLayout()

        header = QLabel("PIPELINE")
        header.setObjectName("panelHeader")

        add_btn = QPushButton("+")
        add_btn.setObjectName("addBtn")
        add_btn.setFixedSize(28, 28)
        add_btn.setToolTip("Add processing step")

        # Create add menu
        self.add_menu = QMenu(self)
        self.add_menu.setStyleSheet("""
            QMenu {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                color: #E8EAED;
            }
            QMenu::item:selected {
                background-color: #2D3336;
            }
        """)

        # Populate add menu
        for node_info in get_available_processing_nodes():
            action = self.add_menu.addAction(f"{node_info['icon']} {node_info['name']}")
            action.setData(node_info["type_id"])

        add_btn.setMenu(self.add_menu)
        self.add_menu.triggered.connect(self._on_add_node)

        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)

        layout.addSpacing(16)

        # Scroll area for nodes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")

        # Container for nodes
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")

        self.nodes_layout = QVBoxLayout(self.scroll_content)
        self.nodes_layout.setContentsMargins(0, 0, 0, 0)
        self.nodes_layout.setSpacing(0)

        # Enable dropping
        self.scroll_content.setAcceptDrops(True)
        self.scroll_content.dragEnterEvent = self._drag_enter_event
        self.scroll_content.dropEvent = self._drop_event

        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area)

        layout.addStretch()

        # Apply styles
        self.setStyleSheet("""
            QWidget#pipelineStackWidget {
                background-color: #121415;
            }
            QLabel#panelHeader {
                color: #9AA0A6;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QPushButton#addBtn {
                background-color: transparent;
                color: #00B884;
                border: 1px solid #00B884;
                border-radius: 4px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton#addBtn:hover {
                background-color: rgba(0, 184, 132, 0.1);
            }
        """)

    def _connect_signals(self):
        """Connect to controller signals."""
        self.controller.pipeline_changed.connect(self._refresh_nodes)
        self.controller.node_selected.connect(self._on_selection_changed)
        self.controller.node_removed.connect(self._on_node_removed)

    def _refresh_nodes(self):
        """Refresh the node list from controller state."""
        # Clear existing
        self._clear_nodes_layout()
        self._node_widgets.clear()

        # Get nodes from state
        nodes = self.controller.state.pipeline.nodes

        for i, node in enumerate(nodes):
            # Create node widget
            node_data = {
                "id": node.id,
                "type": node.type,
                "name": node.name,
                "description": node.description,
                "icon": node.icon,
                "enabled": node.enabled,
            }

            widget = PipelineNodeWidget(node_data, self.controller, self.scroll_content)
            widget.clicked.connect(self._on_node_clicked)
            widget.toggled.connect(self._on_node_toggled)
            widget.deleted.connect(self._on_node_deleted)

            self.nodes_layout.addWidget(widget)
            self._node_widgets[node.id] = widget

            # Add connecting line (except for last node)
            if i < len(nodes) - 1:
                line = self._create_connector_line()
                self.nodes_layout.addWidget(line)

        # Add placeholder if no middle nodes
        if len(nodes) <= 2:
            self._add_placeholder()

    def _clear_nodes_layout(self):
        """Clear all widgets from nodes layout."""
        while self.nodes_layout.count():
            item = self.nodes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _create_connector_line(self) -> QWidget:
        """Create a vertical connector line between nodes."""
        container = QWidget()
        container.setFixedHeight(24)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(36, 0, 0, 0)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet(
            "color: #00B884; border-left: 1.5px solid #00B884; max-width: 1px;"
        )

        layout.addWidget(line)
        return container

    def _add_placeholder(self):
        """Add placeholder text when no middle nodes."""
        placeholder = QLabel("Drag nodes here or use + button")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            color: #5A6066;
            font-size: 11px;
            font-style: italic;
            padding: 16px;
        """)
        self.nodes_layout.addWidget(placeholder)

    # =========================================================================
    # Event Handlers
    # =========================================================================

    def _on_node_clicked(self, node_id: str):
        """Handle node click."""
        self.controller.select_node(node_id)
        self.node_selected.emit(node_id)

    def _on_node_toggled(self, node_id: str, checked: bool):
        """Handle node toggle."""
        self.controller.set_node_enabled(node_id, checked)

    def _on_node_deleted(self, node_id: str):
        """Handle node deletion."""
        self.controller.remove_node(node_id)

    def _on_add_node(self, action):
        """Handle add node from menu."""
        node_type = action.data()
        if node_type:
            self.controller.add_node(node_type)

    def _on_selection_changed(self, node_id: Optional[str]):
        """Handle selection change from controller."""
        # Refresh all node styles
        for widget in self._node_widgets.values():
            widget.refresh()

    def _on_node_removed(self, node_id: str):
        """Handle node removal from controller."""
        # Will be refreshed by pipeline_changed signal
        pass

    # =========================================================================
    # Drag and Drop
    # =========================================================================

    def _drag_enter_event(self, event):
        """Handle drag enter."""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def _drop_event(self, event):
        """Handle drop for node reordering."""
        node_id = event.mimeData().text()

        # Get current index
        current_idx = self.controller.state.get_node_index(node_id)
        if current_idx == -1:
            return

        # Calculate drop position
        drop_y = event.position().y()

        # Find target index based on drop position
        new_idx = self._calculate_drop_index(drop_y, node_id)

        # Move node
        if new_idx != current_idx and new_idx != -1:
            success = self.controller.move_node(node_id, new_idx)
            if success:
                event.acceptProposedAction()

    def _calculate_drop_index(self, drop_y: float, dragged_node_id: str) -> int:
        """Calculate new index for dropped node."""
        nodes = self.controller.state.pipeline.nodes

        # Default to after input
        new_idx = 1

        for i in range(self.nodes_layout.count()):
            item = self.nodes_layout.itemAt(i)
            widget = item.widget()

            if (
                isinstance(widget, PipelineNodeWidget)
                and widget.node_id != dragged_node_id
            ):
                widget_mid = widget.y() + (widget.height() / 2)

                if drop_y < widget_mid:
                    # Find index of this widget's node
                    target_idx = self.controller.state.get_node_index(widget.node_id)
                    if target_idx != -1:
                        new_idx = target_idx
                        break
                else:
                    # Go after this widget
                    target_idx = self.controller.state.get_node_index(widget.node_id)
                    if target_idx != -1:
                        new_idx = target_idx + 1

        # Constrain to valid range (between input and output)
        num_nodes = len(nodes)
        if new_idx <= 0:
            new_idx = 1
        if new_idx >= num_nodes - 1:
            new_idx = num_nodes - 2

        return new_idx

    # =========================================================================
    # Public API
    # =========================================================================

    def refresh(self):
        """Refresh the widget."""
        self._refresh_nodes()

    def select_node(self, node_id: str):
        """Select a node programmatically."""
        if node_id in self._node_widgets:
            self._on_node_clicked(node_id)
