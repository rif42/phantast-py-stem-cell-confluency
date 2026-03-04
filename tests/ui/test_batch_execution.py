import pytest
from PyQt6.QtCore import Qt
from src.ui.batch_execution_view import BatchExecutionIntegrationWidget


class TestBatchExecutionWidget:
    """Tests for batch execution widget."""

    def test_widget_creation(self, qtbot):
        widget = BatchExecutionIntegrationWidget()
        qtbot.addWidget(widget)

        assert widget is not None
        assert widget.left_panel is not None
        assert widget.canvas_area is not None
        assert widget.right_panel is not None

    def test_signals_exist(self, qtbot):
        widget = BatchExecutionIntegrationWidget()
        qtbot.addWidget(widget)

        # Check signals exist
        assert hasattr(widget, "run_pipeline")
        assert hasattr(widget, "open_folder")

    def test_initial_state(self, qtbot):
        widget = BatchExecutionIntegrationWidget()
        qtbot.addWidget(widget)

        # Initial batch job should be empty
        assert widget.batch_job == {}
        assert widget.results == []

    def test_run_pipeline_signal(self, qtbot):
        widget = BatchExecutionIntegrationWidget()
        qtbot.addWidget(widget)

        signals_received = []
        widget.run_pipeline.connect(lambda: signals_received.append("run"))

        # Signal should be connectable
        assert len(signals_received) == 0  # Not emitted yet

    def test_three_panel_layout(self, qtbot):
        widget = BatchExecutionIntegrationWidget()
        qtbot.addWidget(widget)

        # Verify three-panel structure
        assert widget.left_panel.objectName() == "leftPanel"
        assert widget.canvas_area.objectName() == "canvasArea"
        assert widget.right_panel.objectName() == "rightPanel"
