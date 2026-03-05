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
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QMimeData
from PyQt6.QtGui import QIcon, QPainter, QColor, QPen, QDrag


class ToggleSwitch(QPushButton):
    """A custom toggle switch styled for the node."""

    def __init__(self, checked=True):
        super().__init__()
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

        switch = ToggleSwitch(self.node_data.get("enabled", True))
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

    def __init__(self, data_path: str = None):
        super().__init__()
        self.pipeline = {}
        self.available_nodes = []
        self.active_node_id = None

        if data_path and os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.pipeline = data.get("pipeline", {})
                self.available_nodes = data.get("availableNodes", [])
                nodes = self.pipeline.get("nodes", [])
                if nodes:
                    self.active_node_id = nodes[0].get("id")

        self.init_ui()

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
        panel.setMinimumWidth(250)
        panel.setObjectName("leftPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header_layout = QHBoxLayout()
        header = QLabel("PIPELINE STACK")
        header.setObjectName("panelHeader")

        add_btn = QPushButton("Add")
        add_btn.setObjectName("addBtn")

        # Menu for Add Button
        self.add_menu = QMenu(self)
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

            help_text = active_node.get("helpText")
            if help_text:
                help_btn = QPushButton("?")
                help_btn.setObjectName("helpBtn")
                help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                help_btn.setFixedSize(14, 14)
                help_btn.clicked.connect(
                    lambda _, t=help_text, b=help_btn: self.show_help_tooltip(t, b)
                )
                title_layout.addWidget(
                    help_btn,
                    alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                )

            title_layout.addStretch()
            self.right_panel_layout.addWidget(title_container)

            self.right_panel_layout.addSpacing(24)

            # Simulated properties based on node selection
            if active_node.get("name") == "CLAHE":
                self.add_spinbox_row(
                    "Clip Limit", "2.0", "Threshold for contrast limiting."
                )
                self.add_spinbox_row("Grid Size", "8", "Divides image into tiles.")
            else:
                desc = QLabel(active_node.get("description", ""))
                desc.setStyleSheet("color: #9AA0A6;")
                desc.setWordWrap(True)
                self.right_panel_layout.addWidget(desc)
        else:
            empty = QLabel("No selection.")
            empty.setStyleSheet("color: #9AA0A6;")
            self.right_panel_layout.addWidget(empty)

        self.right_panel_layout.addStretch()

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
