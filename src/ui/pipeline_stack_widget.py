"""Pipeline Stack Widget - Reusable pipeline node stack component."""

import os
import json
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
    QDoubleSpinBox,
    QSpinBox,
    QWidgetAction,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QMimeData
from PyQt6.QtGui import QIcon, QPainter, QColor, QPen, QDrag


class ToggleSwitch(QPushButton):
    """A custom toggle switch styled for the node."""

    def __init__(self, checked=True, parent=None):
        super().__init__(parent=parent)
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


class HelpTooltip(QWidget):
    """A custom tooltip modal for property definitions."""

    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        frame = QFrame(parent=self)
        frame.setStyleSheet("""
            QFrame {
                background-color: #E8EAED;
                border-radius: 8px;
            }
            QLabel {
                color: #121415;
                font-size: 13px;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(16, 12, 16, 12)

        label = QLabel(text, parent=frame)
        label.setWordWrap(True)
        label.setFixedWidth(280)
        frame_layout.addWidget(label)

        layout.addWidget(frame)


class PipelineNodeWidget(QFrame):
    """A single node inside the pipeline stack."""

    clicked = pyqtSignal(str)  # node_id
    toggled = pyqtSignal(str, bool)
    deleted = pyqtSignal(str)

    def __init__(self, node_data, is_selected=False, parent=None):
        super().__init__(parent=parent)
        self.node_data = node_data
        self.node_id = node_data.get("id", "")
        self.is_selected = is_selected

        # Enforce type-based draggability
        self.ntype = self.node_data.get("type", "")
        self.is_draggable = self.ntype not in [
            "input",
            "algorithm",
        ]  # 'algorithm' is output here

        self.init_ui()

    def init_ui(self):
        self.setObjectName("nodeCardSelected" if self.is_selected else "nodeCard")
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Left Icon
        icon_frame = QFrame(parent=self)
        icon_frame.setFixedSize(32, 32)
        icon_frame.setObjectName("iconFrame")
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel(self.node_data.get("icon", "⚙️"), parent=icon_frame)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_frame)

        # Middle Details
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(2)

        name_label = QLabel(self.node_data.get("name", "Process Node"), parent=self)
        name_label.setObjectName("nodeName")
        name_label.setStyleSheet("""
            #nodeName {
                color: #E8EAED;
                font-size: 15px;
                font-weight: 600;
            }
        """)
        # Show description as tooltip on hover
        description = self.node_data.get("description", "")
        if description:
            name_label.setToolTip(description)

        details_layout.addWidget(name_label)
        layout.addLayout(details_layout, stretch=1)

        # Right Actions — fixed width so they never collapse
        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(6)
        actions_layout.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        # Determine badge text and color based on type/category
        ntype = self.node_data.get("type", "")
        ncategory = self.node_data.get("category", "")

        # Category color mapping for badges
        cat_badge_config = {
            "image_processing": ("PREPROCESS", "#3B82F6"),
            "segmentation": ("SEGMENT", "#E8A317"),
        }

        badge_text = "PROCESS"
        badge_color = "#9AA0A6"  # default gray
        if ntype == "input":
            badge_text = "INPUT"
            badge_color = "#3B82F6"
        elif ntype == "algorithm":
            badge_text = "OUTPUT"
            badge_color = "#E8A317"
        elif ncategory in cat_badge_config:
            badge_text, badge_color = cat_badge_config[ncategory]

        badge = QLabel(badge_text, parent=self)
        badge.setObjectName("nodeBadge")
        badge.setProperty("nodeType", ntype)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        )

        switch = ToggleSwitch(self.node_data.get("enabled", True), parent=self)
        switch.toggled.connect(lambda checked: self.toggled.emit(self.node_id, checked))
        switch.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        )

        actions_layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignRight)
        actions_layout.addWidget(switch, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(actions_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
            self.clicked.emit(self.node_id)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.is_draggable:
            return

        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if (
            event.pos() - self.drag_start_position
        ).manhattanLength() < 5:  # QApplication.startDragDistance()
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.node_id)
        drag.setMimeData(mime_data)

        # Optional: set a pixmap for the drag operation
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        drag.exec(Qt.DropAction.MoveAction)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        delete_action = menu.addAction("Delete Step")
        # Style the delete action as destructive (opaque red bg, bold black text)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1d21;
                border: 1px solid #2a2e33;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #E8EAED;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #00B884;
                color: #121415;
            }
            QMenu::item#deleteAction {
                background-color: #DC2626;
                color: #000000;
                font-weight: bold;
            }
            QMenu::item#deleteAction:selected {
                background-color: #EF4444;
                color: #000000;
                font-weight: bold;
            }
        """)
        delete_action.setObjectName("deleteAction")
        action = menu.exec(self.mapToGlobal(event.pos()))
        if action == delete_action:
            self.deleted.emit(self.node_id)


class PipelineStackWidget(QFrame):
    """Reusable pipeline stack widget with add button, nodes list, and drag-drop reordering."""

    # Signals
    add_step_requested = pyqtSignal(str)  # step_type
    toggle_node = pyqtSignal(str, bool)  # node_id, enabled
    delete_node = pyqtSignal(str)  # node_id
    node_selected = pyqtSignal(dict)  # node_data
    node_reordered = pyqtSignal(list)  # new_order list of node_ids
    run_pipeline = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.pipeline = {"nodes": []}
        self.available_nodes = []
        self.active_node_id = None
        self.add_button = None  # Will be created in init_ui

        # Load available nodes from step registry
        self._load_available_nodes()
        self.init_ui()

    def _load_available_nodes(self):
        """Load available processing nodes from step registry."""
        try:
            from src.core.steps import STEP_REGISTRY

            self.available_nodes = []
            self._type_to_category: dict[str, str] = {}
            for step_name, step_meta in STEP_REGISTRY.items():
                node_info = {
                    "type": step_name,
                    "name": step_meta.name.replace("_", " ").title(),
                    "description": step_meta.description,
                    "icon": step_meta.icon,
                    "category": step_meta.category,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.type,
                            "default": p.default,
                            "min": p.min,
                            "max": p.max,
                            "step": p.step,
                            "description": p.description,
                        }
                        for p in step_meta.parameters
                    ],
                }
                self.available_nodes.append(node_info)
                self._type_to_category[step_name] = step_meta.category
        except Exception:
            # Fallback if registry not available
            self.available_nodes = []
            self._type_to_category = {}

    def init_ui(self):
        self.setMinimumWidth(300)
        self.setObjectName("leftPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # TODO: Project header — will be reworked later
        # project_header = QFrame(parent=self)
        # project_header_layout = QVBoxLayout(project_header)
        # project_header_layout.setContentsMargins(0, 0, 0, 0)
        # project_header_layout.setSpacing(2)
        #
        # project_title_row = QHBoxLayout()
        # project_title_row.setSpacing(8)
        #
        # project_name = QLabel("Untitled Project", parent=project_header)
        # project_name.setStyleSheet("color: #E8EAED; font-size: 14px; font-weight: 600;")
        #
        # # Yellow dot indicator
        # status_dot = QLabel("●", parent=project_header)
        # status_dot.setStyleSheet("color: #E8A317; font-size: 10px;")
        #
        # project_title_row.addWidget(project_name)
        # project_title_row.addWidget(status_dot)
        # project_title_row.addStretch()
        # project_header_layout.addLayout(project_title_row)
        #
        # project_status = QLabel("Draft - Unsaved", parent=project_header)
        # project_status.setStyleSheet("color: #9AA0A6; font-size: 11px;")
        # project_header_layout.addWidget(project_status)
        #
        # layout.addWidget(project_header)
        # layout.addSpacing(20)

        # Pipeline Stack Header
        header_layout = QHBoxLayout()
        header = QLabel("PIPELINE STACK", parent=self)
        header.setStyleSheet("""
            color: #E8EAED; 
            font-size: 13px; 
            font-weight: 700; 
            letter-spacing: 1px;
        """)

        self.add_button = QPushButton("Add", parent=self)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #00B884;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #00D69A;
            }
            QPushButton:disabled {
                background-color: #2D3336;
                color: #9AA0A6;
            }
        """)

        # Menu for Add Button — categorized with color-coded sections
        self.add_menu = QMenu(self)

        # Category configuration: display name → color
        category_config = {
            "image_processing": ("IMAGE PROCESSING", "#3B82F6"),
            "segmentation": ("SEGMENTATION", "#E8A317"),
        }

        # Group available nodes by category (preserving registration order)
        from collections import OrderedDict

        grouped: "OrderedDict[str, list]" = OrderedDict()
        for node in self.available_nodes:
            cat = node.get("category", "image_processing")
            grouped.setdefault(cat, []).append(node)

        first_section = True
        for cat_key, nodes in grouped.items():
            display_name, color = category_config.get(
                cat_key, (cat_key.replace("_", " ").upper(), "#9AA0A6")
            )

            # Add separator between sections
            if not first_section:
                self.add_menu.addSeparator()
            first_section = False

            # Add category header using QWidgetAction for full color control
            header_widget = QLabel(f"  {display_name}", parent=self)
            header_widget.setStyleSheet(f"""
                color: {color};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
                padding: 10px 12px 4px 12px;
                background: transparent;
            """)
            header_action = QWidgetAction(self)
            header_action.setDefaultWidget(header_widget)
            self.add_menu.addAction(header_action)

            # Add step items under this category
            for node in nodes:
                action = self.add_menu.addAction(
                    f"    {node.get('icon', '')}  {node.get('name')}"
                )
                action.setData(node.get("type"))

        self.add_menu.setStyleSheet("""
            QMenu {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                border-radius: 6px;
                padding: 6px 4px;
            }
            QMenu::item {
                padding: 7px 20px;
                color: #E8EAED;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #2D3336;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 1px;
                background: #2D3336;
                margin: 4px 12px;
            }
        """)

        self.add_button.setMenu(self.add_menu)
        self.add_menu.triggered.connect(
            lambda action: self.add_step_requested.emit(action.data())
        )

        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)

        # Nodes List area
        scroll_area = QScrollArea(parent=self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")

        scroll_content = QWidget(parent=scroll_area)
        scroll_content.setStyleSheet("background-color: transparent;")

        self.nodes_main_layout = QVBoxLayout(scroll_content)
        self.nodes_main_layout.setContentsMargins(0, 16, 0, 16)

        self.nodes_inner_layout = QVBoxLayout()
        self.nodes_inner_layout.setContentsMargins(0, 0, 0, 0)
        self.nodes_inner_layout.setSpacing(0)

        self.nodes_main_layout.addLayout(self.nodes_inner_layout)
        self.nodes_main_layout.addStretch()

        # Enable dropping on the scroll area container
        scroll_content.setAcceptDrops(True)
        scroll_content.dragEnterEvent = self.scroll_dragEnterEvent
        scroll_content.dropEvent = self.scroll_dropEvent

        self.render_nodes()

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Bottom Action
        self.run_button = QPushButton("Run Pipeline", parent=self)
        self.run_button.setObjectName("runBtn")
        self.run_button.clicked.connect(self.run_pipeline.emit)
        layout.addWidget(self.run_button)

    def render_nodes(self):
        """Render all nodes in the pipeline stack."""
        # Clear existing nodes
        for i in reversed(range(self.nodes_inner_layout.count())):
            item = self.nodes_inner_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.spacerItem():
                self.nodes_inner_layout.removeItem(item)

        nodes = self.pipeline.get("nodes", [])
        for i, node in enumerate(nodes):
            is_selected = node.get("id") == self.active_node_id
            # IMPORTANT: Create node widget with parent to prevent window spawning
            node_widget = PipelineNodeWidget(
                node, is_selected, parent=self.nodes_inner_layout.parentWidget()
            )
            node_widget.clicked.connect(self.handle_node_selected)
            node_widget.toggled.connect(self.toggle_node.emit)
            node_widget.deleted.connect(self.delete_node.emit)

            # Dynamic border styling based on type and category
            ntype = node.get("type", "")
            ncategory = node.get("category", "") or self._type_to_category.get(
                ntype, ""
            )

            # Category color mapping
            cat_colors = {
                "image_processing": ("#3B82F6", "#60A5FA"),  # blue / lighter blue
                "segmentation": ("#E8A317", "#FCD34D"),  # yellow / lighter yellow
            }

            border_color = "#2D3336"  # default
            if is_selected:
                border_color = "#00B884"  # selected accent
            elif ntype == "input":
                border_color = "#3B82F6"  # blue for input
            elif ntype == "algorithm":
                border_color = "#E8A317"  # orange for output
            elif ncategory in cat_colors:
                border_color = cat_colors[ncategory][0]  # category color

            node_widget.setStyleSheet(f"""
                #nodeCard, #nodeCardSelected {{
                    background-color: transparent;
                    border: 1px solid {border_color};
                    border-radius: 8px;
                }}
                #nodeCard:hover {{
                    background-color: #1E2224;
                }}
            """)

            self.nodes_inner_layout.addWidget(node_widget)

            # Add connecting line if not last node
            if i < len(nodes) - 1:
                line_container = QWidget(parent=self.nodes_inner_layout.parentWidget())
                line_container.setFixedHeight(24)
                line_layout = QVBoxLayout(line_container)
                line_layout.setContentsMargins(
                    36, 0, 0, 0
                )  # align with left side of node
                line = QFrame(parent=line_container)
                line.setFrameShape(QFrame.Shape.VLine)
                line.setStyleSheet(
                    "color: #00B884; border-left: 1.5px solid #00B884; max-width: 1px;"
                )
                line_layout.addWidget(line)
                self.nodes_inner_layout.addWidget(line_container)

    def handle_node_selected(self, node_id):
        """Handle node selection."""
        self.active_node_id = node_id
        self.render_nodes()

        # Find node data and emit
        for node in self.pipeline.get("nodes", []):
            if node.get("id") == node_id:
                self.node_selected.emit(node)
                break

    def scroll_dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def scroll_dropEvent(self, event):
        node_id = event.mimeData().text()

        # Calculate drop index based on y position
        drop_y = event.position().y()

        nodes = self.pipeline.get("nodes", [])
        current_idx = next(
            (i for i, n in enumerate(nodes) if n.get("id") == node_id), -1
        )
        if current_idx == -1:
            return

        # Find which widget we dropped on/near
        new_idx = 1  # default minimum valid index (after input)
        for i in range(self.nodes_inner_layout.count()):
            item = self.nodes_inner_layout.itemAt(i)
            w = item.widget()
            if isinstance(w, PipelineNodeWidget):
                # If we drop above the vertical center of this widget, insert here
                if drop_y < w.y() + (w.height() / 2):
                    target_node_id = w.node_id
                    new_idx = next(
                        (
                            j
                            for j, n in enumerate(nodes)
                            if n.get("id") == target_node_id
                        ),
                        new_idx,
                    )
                    break
                else:
                    # Otherwise, assume it goes after this widget
                    new_idx = (
                        next(
                            (
                                j
                                for j, n in enumerate(nodes)
                                if n.get("id") == w.node_id
                            ),
                            new_idx,
                        )
                        + 1
                    )

        # Restrict dropping above input (index 0) or below output (len-1)
        if new_idx <= 0:
            new_idx = 1
        if new_idx >= len(nodes) - 1:
            new_idx = len(nodes) - 2  # Place before the final output node

        if current_idx < new_idx:
            new_idx -= 1  # Adjust for shifting elements

        if current_idx != new_idx:
            # Reorder the internal data
            node = nodes.pop(current_idx)
            nodes.insert(new_idx, node)
            self.render_nodes()
            # Emit signal with new order
            new_order = [n.get("id") for n in nodes]
            self.node_reordered.emit(new_order)
            event.acceptProposedAction()

    def set_pipeline(self, pipeline_data):
        """Set the pipeline data and re-render."""
        self.pipeline = pipeline_data
        self.render_nodes()

    def get_pipeline(self):
        """Get the current pipeline data."""
        return self.pipeline

    def set_active_node(self, node_id):
        """Set the active/selected node."""
        self.active_node_id = node_id
        self.render_nodes()

    def add_node(self, node_data):
        """Add a node to the pipeline."""
        if "nodes" not in self.pipeline:
            self.pipeline["nodes"] = []
        self.pipeline["nodes"].append(node_data)
        self.render_nodes()

    def remove_node(self, node_id):
        """Remove a node from the pipeline."""
        if "nodes" in self.pipeline:
            self.pipeline["nodes"] = [
                n for n in self.pipeline["nodes"] if n.get("id") != node_id
            ]
            if self.active_node_id == node_id:
                self.active_node_id = None
            self.render_nodes()

    def update_node(self, node_id, node_data):
        """Update a node's data."""
        if "nodes" in self.pipeline:
            for i, node in enumerate(self.pipeline["nodes"]):
                if node.get("id") == node_id:
                    self.pipeline["nodes"][i] = node_data
                    break
            self.render_nodes()

    def clear(self):
        """Clear all nodes."""
        self.pipeline = {"nodes": []}
        self.active_node_id = None
        self.render_nodes()

    def get_nodes(self):
        """Get list of all nodes."""
        return self.pipeline.get("nodes", [])

    def set_add_button_enabled(self, enabled):
        """Enable or disable the Add button."""
        if self.add_button:
            self.add_button.setEnabled(enabled)
