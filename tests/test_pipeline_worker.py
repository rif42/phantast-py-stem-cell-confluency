"""Tests for asynchronous pipeline execution worker and executor."""

import time
import sys
from pathlib import Path

import cv2
import numpy as np
from PyQt6.QtCore import QTimer

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.models.pipeline_model import PipelineNode
from src.core.pipeline_worker import PipelineWorker
from src.ui.main_window import PipelineExecutor


class _AddConstantStep:
    @staticmethod
    def process(image, amount=1):
        return np.clip(image + amount, 0, 255).astype(np.uint8)


class _SlowPassThroughStep:
    @staticmethod
    def process(image, delay=0.1):
        time.sleep(delay)
        return image


def test_pipeline_worker_emits_progress_step_and_finished_signals(qtbot, tmp_path):
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    source = np.full((8, 8, 3), 10, dtype=np.uint8)
    cv2.imwrite(str(input_path), source)

    worker = PipelineWorker()
    nodes = [
        PipelineNode(
            id="1",
            type="add_constant",
            name="add",
            description="add",
            icon="x",
            status="idle",
            enabled=True,
            parameters={"amount": 5},
        )
    ]
    step_registry = {"add_constant": _AddConstantStep()}

    progress_events = []
    completed_events = []
    worker.progress.connect(lambda name, pct: progress_events.append((name, pct)))
    worker.step_completed.connect(lambda name, _: completed_events.append(name))

    with qtbot.waitSignal(worker.finished, timeout=2000) as finished_signal:
        worker.process_pipeline(str(input_path), str(output_path), nodes, step_registry)

    assert finished_signal.args[0] == str(output_path)
    assert completed_events == ["add_constant"]
    assert progress_events
    assert progress_events[-1][1] == 100
    assert output_path.exists()


def test_pipeline_worker_emits_error_for_unknown_step(qtbot, tmp_path):
    input_path = tmp_path / "input.png"
    source = np.zeros((4, 4, 3), dtype=np.uint8)
    cv2.imwrite(str(input_path), source)

    worker = PipelineWorker()
    nodes = [
        PipelineNode(
            id="1",
            type="missing_step",
            name="missing",
            description="missing",
            icon="x",
            status="idle",
            enabled=True,
            parameters={},
        )
    ]

    with qtbot.waitSignal(worker.error, timeout=2000) as error_signal:
        worker.process_pipeline(
            str(input_path), str(tmp_path / "output.png"), nodes, {}
        )

    assert "Unknown step type" in error_signal.args[0]


def test_pipeline_executor_runs_in_thread_and_cleans_up(qtbot, tmp_path):
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    source = np.full((16, 16, 3), 20, dtype=np.uint8)
    cv2.imwrite(str(input_path), source)

    nodes = [
        PipelineNode(
            id="1",
            type="slow_step",
            name="slow",
            description="slow",
            icon="x",
            status="idle",
            enabled=True,
            parameters={"delay": 0.15},
        )
    ]
    step_registry = {"slow_step": _SlowPassThroughStep()}
    executor = PipelineExecutor()

    heartbeat = {"tick": False}
    QTimer.singleShot(20, lambda: heartbeat.__setitem__("tick", True))

    with qtbot.waitSignal(executor.finished, timeout=3000):
        assert executor.start(str(input_path), str(output_path), nodes, step_registry)
        qtbot.waitUntil(lambda: heartbeat["tick"], timeout=1000)

    assert output_path.exists()
    assert not executor.is_running()
    assert executor._thread is None
    assert executor._worker is None
