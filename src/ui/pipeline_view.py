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
    QSplitter,
    QDoubleSpinBox,
    QSpinBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QMimeData
from PyQt6.QtGui import QIcon, QPainter, QColor, QPen, QDrag


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


class HelpTooltip(QWidget):
    """A custom tooltip modal for property definitions."""

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #E8EAED;
                border-radius: 8px;
            }
            QLabel {
                color: #121415;
                font-size: 13px;
                font-family: 'Inter';
            }
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(16, 12, 16, 12)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setFixedWidth(280)
        frame_layout.addWidget(label)

        layout.addWidget(frame)


class PipelineNodeWidget(QFrame):
    """A single node inside the pipeline stack."""

    clicked = pyqtSignal(str)  # node_id
    toggled = pyqtSignal(str, bool)
    deleted = pyqtSignal(str)

    def __init__(self, node_data, is_selected=False):
        super().__init__()
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
        self.setFixedHeight(72)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Left Icon
        icon_frame = QFrame()
        icon_frame.setFixedSize(32, 32)
        icon_frame.setObjectName("iconFrame")
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

        # Determine badge text and color based on type
        ntype = self.node_data.get("type", "")
        badge_text = "PROCESS"
        badge_color = "#E8A317"  # default orangeish
        if ntype == "input":
            badge_text = "INPUT"
            badge_color = "#3B82F6"
        elif ntype == "algorithm":
            badge_text = "OUTPUT"
            badge_color = "#E8A317"

        badge = QLabel(badge_text)
        badge.setObjectName("nodeBadge")
        # Badge color is handled via type-based logic in stylesheet
        # Colors: INPUT=blue, OUTPUT=orange, PROCESS=default
        badge.setProperty("nodeType", ntype)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        switch = ToggleSwitch(self.node_data.get("enabled", True), parent=self)
        switch.toggled.connect(lambda checked: self.toggled.emit(self.node_id, checked))

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
        action = menu.exec(self.mapToGlobal(event.pos()))
        if action == delete_action:
            self.deleted.emit(self.node_id)


class PipelineConstructionWidget(QWidget):
    # Signals
    add_step = pyqtSignal(str)
    toggle_node = pyqtSignal(str, bool)
    delete_node = pyqtSignal(str)
    run_pipeline = pyqtSignal()
    node_selected = pyqtSignal(str)
    node_reordered = pyqtSignal(str, int)  # node_id, new_index
    node_params_changed = pyqtSignal(str, str, object)  # node_id, param_name, value

    def __init__(self, data_path: str = None):
        super().__init__()
        self.pipeline = {}
        self.available_nodes = []
        self.active_node_id = None

        # Load available nodes from step registry
        self._load_available_nodes()

        if data_path and os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.pipeline = data.get("pipeline", {})
                # Don't override available_nodes from registry
                nodes = self.pipeline.get("nodes", [])
                if nodes:
                    self.active_node_id = nodes[0].get("id")

        self.init_ui()

    def _load_available_nodes(self):
        """Load available processing nodes from step registry."""
        try:
            from src.core.steps import STEP_REGISTRY

            self.available_nodes = []
            for step_name, step_meta in STEP_REGISTRY.items():
                node_info = {
                    "type": step_name,
                    "name": step_meta.description,  # Use description as display name
                    "description": step_meta.description,
                    "icon": step_meta.icon,
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
        except ImportError:
            # Fallback if registry not available
            self.available_nodes = []
            for step_name, step_meta in STEP_REGISTRY.items():
                node_info = {
                    "type": step_name,
                    "name": step_meta.name,
                    "description": step_meta.description,
                    "icon": step_meta.icon,
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
        except Exception:
            # Fallback if registry not available
            self.available_nodes = []

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #2D3336; }")

        self.left_panel = self.create_left_panel()
        splitter.addWidget(self.left_panel)

        self.canvas_area = self.create_canvas_area()
        splitter.addWidget(self.canvas_area)

        self.right_panel = self.create_right_panel()
        splitter.addWidget(self.right_panel)

        # Give the canvas the vast majority of the stretch factor
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        main_layout.addWidget(splitter)

    def create_left_panel(self):
        panel = QFrame()
        panel.setMinimumWidth(280)
        panel.setObjectName("leftPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # Project Header (matches design)
        project_header = QFrame()
        project_header_layout = QVBoxLayout(project_header)
        project_header_layout.setContentsMargins(0, 0, 0, 0)
        project_header_layout.setSpacing(2)

        project_title_row = QHBoxLayout()
        project_title_row.setSpacing(8)

        project_name = QLabel("Untitled Project")
        project_name.setStyleSheet("color: #E8EAED; font-size: 14px; font-weight: 600;")

        # Yellow dot indicator
        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #E8A317; font-size: 10px;")

        project_title_row.addWidget(project_name)
        project_title_row.addWidget(status_dot)
        project_title_row.addStretch()
        project_header_layout.addLayout(project_title_row)

        project_status = QLabel("Draft - Unsaved")
        project_status.setStyleSheet("color: #9AA0A6; font-size: 11px;")
        project_header_layout.addWidget(project_status)

        layout.addWidget(project_header)
        layout.addSpacing(20)

        # Pipeline Stack Header
        header_layout = QHBoxLayout()
        header = QLabel("PIPELINE STACK")
        header.setStyleSheet("""
            color: #9AA0A6; 
            font-size: 10px; 
            font-weight: 600; 
            letter-spacing: 1px;
        """)

        add_btn = QPushButton("Add")
        add_btn.setStyleSheet("""
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
        """)

        # Menu for Add Button
        self.add_menu = QMenu(self)
        self.add_menu.setStyleSheet("""
            QMenu {
                background-color: #1E2224;
                border: 1px solid #2D3336;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                color: #E8EAED;
            }
            QMenu::item:selected {
                background-color: #2D3336;
                border-radius: 4px;
            }
        """)
        for node in self.available_nodes:
            action = self.add_menu.addAction(node.get("name"))
            action.setData(node.get("type"))

        add_btn.setMenu(self.add_menu)
        self.add_menu.triggered.connect(
            lambda action: self.add_step.emit(action.data())
        )

        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)

        # Nodes List area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")

        scroll_content = QWidget()
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
        run_btn = QPushButton("Run Pipeline")
        run_btn.setObjectName("runBtn")
        run_btn.clicked.connect(self.run_pipeline.emit)
        layout.addWidget(run_btn)

        return panel

    def render_nodes(self):
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
            node_widget = PipelineNodeWidget(node, is_selected)
            node_widget.clicked.connect(self.handle_node_selected)
            node_widget.toggled.connect(self.toggle_node.emit)
            node_widget.deleted.connect(self.delete_node.emit)

            # Dynamic border styling based on type
            ntype = node.get("type", "")
            border_color = "#2D3336"  # default
            if is_selected:
                border_color = "#00B884"  # selected process
            elif ntype == "input":
                border_color = "#3B82F6"  # blue for input
                if is_selected:
                    border_color = "#60A5FA"
            elif ntype == "algorithm":
                border_color = "#E8A317"  # orange for output
                if is_selected:
                    border_color = "#FCD34D"

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
                line_container = QWidget()
                line_container.setFixedHeight(24)
                line_layout = QVBoxLayout(line_container)
                line_layout.setContentsMargins(
                    36, 0, 0, 0
                )  # align with left side of node
                line = QFrame()
                line.setFrameShape(QFrame.Shape.VLine)
                line.setStyleSheet(
                    "color: #00B884; border-left: 1.5px solid #00B884; max-width: 1px;"
                )
                line_layout.addWidget(line)
                self.nodes_inner_layout.addWidget(line_container)

    def handle_node_selected(self, node_id):
        self.active_node_id = node_id
        self.render_nodes()
        self.node_selected.emit(node_id)

        self.update_right_panel()

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
            # Reorder the internal data for preview visualization
            node = nodes.pop(current_idx)
            nodes.insert(new_idx, node)
            self.render_nodes()
            # Emit signal for actual application logic
            self.node_reordered.emit(node_id, new_idx)
            event.acceptProposedAction()

    def update_right_panel(self):
        # Clear panel
        for i in reversed(range(self.right_panel_layout.count())):
            item = self.right_panel_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
            elif item.spacerItem():
                self.right_panel_layout.removeItem(item)

        header = QLabel("PROPERTIES")
        header.setObjectName("panelHeader")
        self.right_panel_layout.addWidget(header)

        active_node = next(
            (
                n
                for n in self.pipeline.get("nodes", [])
                if n.get("id") == self.active_node_id
            ),
            None,
        )

        if active_node:
            self.right_panel_layout.addSpacing(16)

            title_container = QWidget()
            title_layout = QHBoxLayout(title_container)
            title_layout.setContentsMargins(0, 0, 0, 0)
            title_layout.setSpacing(1)

            title = QLabel(active_node.get("name", "Node Properties"))
            title.setObjectName("sectionHeader")
            title_layout.addWidget(title)
            title_layout.addStretch()
            self.right_panel_layout.addWidget(title_container)

            self.right_panel_layout.addSpacing(24)

            # Dynamic parameter generation from step metadata
            node_type = active_node.get("type", "")
            node_params = active_node.get("parameters", {})

            # Find step definition in available_nodes
            step_def = next(
                (n for n in self.available_nodes if n.get("type") == node_type), None
            )

            if step_def and step_def.get("parameters"):
                # Generate dynamic parameter UI
                for param in step_def["parameters"]:
                    self._add_parameter_widget(
                        param, node_params, active_node.get("id")
                    )
            else:
                # No parameters - show description only
                desc = QLabel(active_node.get("description", ""))
                desc.setStyleSheet("color: #9AA0A6;")
                desc.setWordWrap(True)
                self.right_panel_layout.addWidget(desc)
        else:
            empty = QLabel("No selection.")
            empty.setStyleSheet("color: #9AA0A6;")
            self.right_panel_layout.addWidget(empty)

        self.right_panel_layout.addStretch()

    def _add_parameter_widget(self, param_def, node_params, node_id):
        """Add a parameter widget for a single parameter.

        Args:
            param_def: Parameter definition dict with name, type, default, min, max, step
            node_params: Current parameter values dict for the node
            node_id: ID of the node being edited
        """
        param_name = param_def.get("name", "")
        param_type = param_def.get("type", "float")
        param_default = param_def.get("default", 0)
        param_min = param_def.get("min")
        param_max = param_def.get("max")
        param_step = param_def.get("step", 1)
        param_desc = param_def.get("description", "")

        # Get current value or use default
        current_value = node_params.get(param_name, param_default)

        # Create container
        container = QFrame()
        container.setStyleSheet("margin-bottom: 16px;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Parameter name label
        name_label = QLabel(param_name.replace("_", " ").title())
        name_label.setStyleSheet("color: #E8EAED; font-size: 13px; font-weight: 500;")
        layout.addWidget(name_label)

        # Create appropriate widget based on type
        if param_type == "float":
            spinbox = QDoubleSpinBox()
            spinbox.setDecimals(1)
            if param_step:
                spinbox.setSingleStep(float(param_step))
            if param_min is not None:
                spinbox.setMinimum(float(param_min))
            if param_max is not None:
                spinbox.setMaximum(float(param_max))
            spinbox.setValue(float(current_value))
            spinbox.valueChanged.connect(
                lambda val, n=node_id, p=param_name: self._on_parameter_changed(
                    n, p, val
                )
            )
            layout.addWidget(spinbox)
        elif param_type == "int":
            spinbox = QSpinBox()
            if param_step:
                spinbox.setSingleStep(int(param_step))
            if param_min is not None:
                spinbox.setMinimum(int(param_min))
            if param_max is not None:
                spinbox.setMaximum(int(param_max))
            spinbox.setValue(int(current_value))
            spinbox.valueChanged.connect(
                lambda val, n=node_id, p=param_name: self._on_parameter_changed(
                    n, p, val
                )
            )
            layout.addWidget(spinbox)
        else:
            # Fallback for other types
            label = QLabel(str(current_value))
            label.setStyleSheet("color: #FFFFFF;")
            layout.addWidget(label)

        # Description text
        if param_desc:
            desc_label = QLabel(param_desc)
            desc_label.setStyleSheet("color: #9AA0A6; font-size: 11px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        self.right_panel_layout.addWidget(container)

    def _on_parameter_changed(self, node_id, param_name, value):
        """Handle parameter value change.

        Args:
            node_id: ID of the node
            param_name: Name of the parameter
            value: New value
        """
        # Find the node and update its parameter
        for node in self.pipeline.get("nodes", []):
            if node.get("id") == node_id:
                if "parameters" not in node:
                    node["parameters"] = {}
                node["parameters"][param_name] = value
                break
        # Emit signal to notify controller
        self.node_params_changed.emit(node_id, param_name, value)

    def add_spinbox_row(self, label_txt, val_txt, subtext_txt=""):
        container = QFrame()
        container.setStyleSheet("margin-bottom: 16px;")
        l = QVBoxLayout(container)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(4)

        title = QLabel(label_txt)
        title.setStyleSheet("color: #E8EAED; font-size: 13px; font-weight: 500;")

        # mock combobox/spinbox
        box = QFrame()
        box.setObjectName("inputBox")
        bl = QHBoxLayout(box)
        bl.setContentsMargins(12, 8, 12, 8)
        val = QLabel(val_txt)
        val.setStyleSheet("color: #FFFFFF;")
        arr = QLabel("↕")
        arr.setStyleSheet("color: #9AA0A6;")
        bl.addWidget(val)
        bl.addStretch()
        bl.addWidget(arr)

        l.addWidget(title)
        l.addWidget(box)

        if subtext_txt:
            sub = QLabel(subtext_txt)
            sub.setStyleSheet("color: #9AA0A6; font-size: 11px;")
            sub.setWordWrap(True)
            l.addWidget(sub)

        self.right_panel_layout.addWidget(container)

    def show_help_tooltip(self, text, button):
        if hasattr(self, "_current_tooltip") and getattr(
            self, "_current_tooltip", None
        ):
            self._current_tooltip.close()

        tooltip = HelpTooltip(text, self)
        # Position it relative to the button
        pos = button.mapToGlobal(QPoint(button.width(), 0))
        # Move slightly to appear like a popup bubble
        tooltip.move(pos + QPoint(10, -10))
        tooltip.show()
        self._current_tooltip = tooltip

    def create_canvas_area(self):
        area = QFrame()
        area.setObjectName("canvasArea")
        layout = QVBoxLayout(area)

        # Simple placeholder for canvas
        self.image_label = QLabel(
            "Central Canvas area.\nThis would show the image with processing applied."
        )
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setObjectName("canvasImage")
        layout.addWidget(self.image_label)

        return area

    def create_right_panel(self):
        panel = QFrame()
        panel.setMinimumWidth(250)
        panel.setObjectName("rightPanel")

        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        self.right_panel_layout = QVBoxLayout(scroll_content)
        self.right_panel_layout.setContentsMargins(16, 16, 16, 16)

        self.update_right_panel()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        return panel

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121415;
                color: #E8EAED;
                font-family: 'Inter';
            }
            #leftPanel, #rightPanel {
                background-color: #121415;
                border-left: 1px solid #2D3336;
                border-right: 1px solid #2D3336;
            }
            #canvasArea {
                background-color: #0d0f10;
            }
            #panelHeader {
                color: #9AA0A6;
                font-size: 11px;
                font-weight: bold;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            #sectionHeader {
                color: #E8EAED;
                font-size: 14px;
                font-weight: bold;
            }
            #addBtn {
                background-color: transparent;
                color: #00B884;
                border: 1px solid #00B884;
                border-radius: 4px;
                padding: 4px 12px;
                font-weight: 500;
                font-size: 12px;
            }
            #addBtn:hover {
                background-color: rgba(0, 184, 132, 0.1);
            }
            #runBtn {
                background-color: #00B884;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 14px;
                margin-top: 16px;
            }
            #runBtn:hover {
                background-color: #00C890;
            }
            #nodeCard {
                background-color: transparent;
                border: 1px solid #2D3336;
                border-radius: 8px;
            }
            #nodeCard:hover {
                background-color: #1E2224;
            }
            #nodeCardSelected {
                background-color: transparent;
                border: 1px solid #00B884;
                border-radius: 8px;
            }
            #nodeName {
                color: #E8EAED;
                font-size: 13px;
                font-weight: 600;
            }
            #nodeDesc {
                color: #9AA0A6;
                font-size: 11px;
            }
            #nodeBadge {
                font-size: 9px;
                font-weight: bold;
                border-radius: 2px;
                padding: 2px 4px;
            }
            #inputBox {
                background-color: #121415;
                border: 1px solid #2D3336;
                border-radius: 4px;
            }
            #helpBtn {
                background: transparent;
                border: none;
                color: #9AA0A6;
                font-weight: 600;
                font-size: 11px;
                padding: 0px;
                margin-top: -2px;
            }
            #helpBtn:hover {
                color: #00B884;
            }
        """)
