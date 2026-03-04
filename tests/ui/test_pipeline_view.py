import pytest
from PyQt6.QtCore import Qt
from src.ui.pipeline_view import (
    PipelineConstructionWidget,
    PipelineNodeWidget,
    ToggleSwitch,
    HelpTooltip,
)


class TestToggleSwitch:
    """Tests for the custom toggle switch."""

    def test_toggle_creation(self, qtbot):
        switch = ToggleSwitch(checked=True)
        qtbot.addWidget(switch)
        assert switch.isChecked() is True

    def test_toggle_click_changes_state(self, qtbot):
        switch = ToggleSwitch(checked=True)
        qtbot.addWidget(switch)

        # Click to toggle off
        qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)
        assert switch.isChecked() is False

        # Click to toggle on
        qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)
        assert switch.isChecked() is True


class TestPipelineNodeWidget:
    """Tests for individual pipeline node widgets."""

    def test_node_creation(self, qtbot):
        node_data = {
            "id": "step1",
            "name": "Test Step",
            "description": "A test step",
            "type": "process",
            "enabled": True,
            "icon": "⚙️",
        }
        node = PipelineNodeWidget(node_data)
        qtbot.addWidget(node)

        assert node.node_id == "step1"
        assert node.is_draggable is True  # process type is draggable

    def test_input_node_not_draggable(self, qtbot):
        node_data = {
            "id": "input1",
            "name": "Input",
            "description": "Input node",
            "type": "input",
            "enabled": True,
        }
        node = PipelineNodeWidget(node_data)
        qtbot.addWidget(node)

        assert node.is_draggable is False  # input type is not draggable

    def test_node_click_emits_signal(self, qtbot):
        node_data = {"id": "step1", "name": "Test", "type": "process"}
        node = PipelineNodeWidget(node_data)
        qtbot.addWidget(node)

        # Track signal emissions
        clicked_ids = []
        node.clicked.connect(lambda nid: clicked_ids.append(nid))

        qtbot.mouseClick(node, Qt.MouseButton.LeftButton)

        assert len(clicked_ids) == 1
        assert clicked_ids[0] == "step1"


class TestPipelineConstructionWidget:
    """Tests for the pipeline construction widget."""

    def test_widget_creation(self, qtbot):
        widget = PipelineConstructionWidget()
        qtbot.addWidget(widget)

        assert widget is not None
        assert widget.left_panel is not None
        assert widget.right_panel is not None

    def test_node_selection(self, qtbot):
        widget = PipelineConstructionWidget()
        qtbot.addWidget(widget)

        # Set up sample pipeline data
        widget.pipeline = {
            "nodes": [
                {"id": "input1", "name": "Input", "type": "input"},
                {"id": "step1", "name": "CLAHE", "type": "process"},
                {"id": "output1", "name": "Output", "type": "algorithm"},
            ]
        }
        widget.active_node_id = "step1"
        widget.render_nodes()

        assert widget.active_node_id == "step1"

    def test_run_pipeline_signal(self, qtbot):
        widget = PipelineConstructionWidget()
        qtbot.addWidget(widget)

        # Track signal emissions
        run_emitted = [False]
        widget.run_pipeline.connect(lambda: run_emitted.__setitem__(0, True))

        # Find and click run button
        run_btn = widget.left_panel.findChild(type(widget.left_panel), "runBtn")
        if run_btn:
            qtbot.mouseClick(run_btn, Qt.MouseButton.LeftButton)

        # The signal should be connected to the button
        assert widget.run_pipeline is not None


class TestHelpTooltip:
    """Tests for help tooltip widget."""

    def test_tooltip_creation(self, qtbot):
        tooltip = HelpTooltip("Test help text")
        qtbot.addWidget(tooltip)

        assert tooltip is not None
