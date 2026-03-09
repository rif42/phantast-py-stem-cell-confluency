"""Integration tests for pipeline execution behavior."""

import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.core.pipeline_worker import PipelineWorker
from src.core.steps import STEP_REGISTRY
from src.models.pipeline_model import PipelineNode
from src.ui.main_window import MainWindow


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class _NoneStep:
    @staticmethod
    def process(_image, **_kwargs):
        return None


def _node(
    step_type: str, enabled: bool = True, parameters: dict | None = None
) -> PipelineNode:
    return PipelineNode(
        id=f"node-{step_type}-{enabled}",
        type=step_type,
        name=step_type,
        description=step_type,
        icon="x",
        status="idle",
        enabled=enabled,
        parameters=parameters or {},
    )


@pytest.fixture
def synthetic_input_path(tmp_path: Path) -> Path:
    src = FIXTURES_DIR / "synthetic_stem_cells.png"
    dst = tmp_path / "input.png"
    dst.write_bytes(src.read_bytes())
    return dst


def test_full_pipeline_execution_clahe_then_phantast(
    qtbot, synthetic_input_path, tmp_path
):
    worker = PipelineWorker()
    output_path = tmp_path / "full_pipeline_output.png"
    nodes = [
        _node("clahe", parameters={"clip_limit": 2.0, "block_size": 8}),
        _node("phantast", parameters={"sigma": 6.5, "epsilon": 0.045}),
    ]

    completed = []
    worker.step_completed.connect(lambda step_name, _: completed.append(step_name))

    with qtbot.waitSignal(worker.finished, timeout=10000) as finished_signal:
        worker.process_pipeline(
            str(synthetic_input_path),
            str(output_path),
            nodes,
            STEP_REGISTRY,
        )

    assert finished_signal.args[0] == str(output_path)
    assert completed == ["clahe", "phantast"]
    assert output_path.exists()

    out = cv2.imread(str(output_path), cv2.IMREAD_UNCHANGED)
    assert out is not None
    assert out.ndim == 3
    assert out.shape[2] == 3


def test_single_step_pipeline_clahe_writes_output(
    qtbot, synthetic_input_path, tmp_path
):
    worker = PipelineWorker()
    output_path = tmp_path / "clahe_only.png"
    nodes = [_node("clahe", parameters={"clip_limit": 3.0, "block_size": 8})]

    with qtbot.waitSignal(worker.finished, timeout=10000):
        worker.process_pipeline(
            str(synthetic_input_path), str(output_path), nodes, STEP_REGISTRY
        )

    src = cv2.imread(str(synthetic_input_path), cv2.IMREAD_UNCHANGED)
    out = cv2.imread(str(output_path), cv2.IMREAD_UNCHANGED)
    assert out is not None
    assert src is not None
    assert not np.array_equal(out[:, :, 0], src[:, :, 0])


def test_single_step_pipeline_phantast_outputs_binary_like_mask(
    qtbot, synthetic_input_path, tmp_path
):
    worker = PipelineWorker()
    output_path = tmp_path / "phantast_only.png"
    nodes = [_node("phantast")]

    with qtbot.waitSignal(worker.finished, timeout=10000):
        worker.process_pipeline(
            str(synthetic_input_path), str(output_path), nodes, STEP_REGISTRY
        )

    out = cv2.imread(str(output_path), cv2.IMREAD_UNCHANGED)
    assert out is not None
    unique_values = np.unique(out[:, :, 0])
    assert set(unique_values.tolist()).issubset({0, 255})
    assert np.array_equal(out[:, :, 0], out[:, :, 1])
    assert np.array_equal(out[:, :, 1], out[:, :, 2])


def test_disabled_node_is_skipped(qtbot, synthetic_input_path, tmp_path):
    worker = PipelineWorker()
    output_path = tmp_path / "disabled_skip.png"
    nodes = [
        _node("clahe", enabled=False),
        _node("phantast", enabled=True),
    ]
    completed = []
    worker.step_completed.connect(lambda step_name, _: completed.append(step_name))

    with qtbot.waitSignal(worker.finished, timeout=10000):
        worker.process_pipeline(
            str(synthetic_input_path), str(output_path), nodes, STEP_REGISTRY
        )

    assert completed == ["phantast"]


def test_input_single_image_node_is_skipped(qtbot, synthetic_input_path, tmp_path):
    worker = PipelineWorker()
    output_path = tmp_path / "input_node_skip.png"
    nodes = [
        _node("input_single_image", enabled=True, parameters={"file_path": "x"}),
        _node("clahe", enabled=True),
    ]
    completed = []
    worker.step_completed.connect(lambda step_name, _: completed.append(step_name))

    with qtbot.waitSignal(worker.finished, timeout=10000):
        worker.process_pipeline(
            str(synthetic_input_path), str(output_path), nodes, STEP_REGISTRY
        )

    assert completed == ["clahe"]


def test_no_executable_nodes_still_generates_output(
    qtbot, synthetic_input_path, tmp_path
):
    worker = PipelineWorker()
    output_path = tmp_path / "no_steps.png"
    nodes = [_node("input_single_image", enabled=True), _node("clahe", enabled=False)]

    with qtbot.waitSignal(worker.finished, timeout=10000):
        worker.process_pipeline(
            str(synthetic_input_path), str(output_path), nodes, STEP_REGISTRY
        )

    assert output_path.exists()


def test_missing_input_file_emits_error(qtbot, tmp_path):
    worker = PipelineWorker()
    missing_input = tmp_path / "missing.png"
    output_path = tmp_path / "unused.png"

    with qtbot.waitSignal(worker.error, timeout=10000) as error_signal:
        worker.process_pipeline(
            str(missing_input), str(output_path), [_node("clahe")], STEP_REGISTRY
        )

    assert "Unable to load image" in error_signal.args[0]


def test_invalid_output_path_emits_error(qtbot, synthetic_input_path, tmp_path):
    worker = PipelineWorker()
    invalid_output = tmp_path / "missing_dir" / "output.png"

    with qtbot.waitSignal(worker.error, timeout=10000) as error_signal:
        worker.process_pipeline(
            str(synthetic_input_path),
            str(invalid_output),
            [_node("clahe")],
            STEP_REGISTRY,
        )

    assert "Failed to save processed image" in error_signal.args[0]


def test_unknown_step_emits_error(qtbot, synthetic_input_path, tmp_path):
    worker = PipelineWorker()
    output_path = tmp_path / "unknown_step.png"

    with qtbot.waitSignal(worker.error, timeout=10000) as error_signal:
        worker.process_pipeline(
            str(synthetic_input_path),
            str(output_path),
            [_node("does_not_exist")],
            STEP_REGISTRY,
        )

    assert "Unknown step type" in error_signal.args[0]


def test_step_returning_none_emits_error(qtbot, synthetic_input_path, tmp_path):
    worker = PipelineWorker()
    output_path = tmp_path / "none_step.png"
    registry = {"none_step": _NoneStep()}

    with qtbot.waitSignal(worker.error, timeout=10000) as error_signal:
        worker.process_pipeline(
            str(synthetic_input_path),
            str(output_path),
            [_node("none_step")],
            registry,
        )

    assert "returned no image" in error_signal.args[0]


def test_pipeline_finished_updates_canvas_and_current_image(monkeypatch, tmp_path):
    window = MainWindow()
    output_path = tmp_path / "processed.png"
    src = FIXTURES_DIR / "synthetic_stem_cells.png"
    output_path.write_bytes(src.read_bytes())

    loaded_paths = []

    def _load_image(file_path: str) -> bool:
        loaded_paths.append(file_path)
        return True

    monkeypatch.setattr(window.image_canvas, "load_image", _load_image)
    monkeypatch.setattr(window, "_set_processing_state", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(window, "_update_run_button_state", lambda: None)

    monkeypatch.setattr(
        window, "_get_current_metadata", lambda: {"filename": "processed.png"}
    )

    window._handle_pipeline_finished(str(output_path))

    assert window.current_image_path == str(output_path)
    assert loaded_paths == [str(output_path)]
    assert window.image_model.active_image is not None
    assert window.image_model.active_image["filepath"] == str(output_path)
    window.close()


def test_pipeline_error_handler_restores_processing_state(monkeypatch, tmp_path):
    window = MainWindow()

    input_path = tmp_path / "input.png"
    input_path.write_bytes((FIXTURES_DIR / "synthetic_stem_cells.png").read_bytes())
    window.current_image_path = str(input_path)

    monkeypatch.setattr(window, "_set_processing_state", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(window, "_update_run_button_state", lambda: None)
    captured_metadata = []
    monkeypatch.setattr(
        window.right_panel,
        "show_metadata",
        lambda metadata: captured_metadata.append(metadata),
    )

    shown_errors = []
    monkeypatch.setattr(
        window, "_show_error_dialog", lambda message: shown_errors.append(message)
    )
    window._handle_pipeline_error("boom")

    assert shown_errors == ["boom"]
    assert window.status_label.text() == "Processing failed"
    assert captured_metadata
    assert captured_metadata[-1]["subtitle"] == "Pipeline execution failed"
    window.close()
