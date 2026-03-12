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
from src.ui import main_window as main_window_module
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


def test_input_image_folder_skipped(qtbot, synthetic_input_path, tmp_path):
    worker = PipelineWorker()
    output_path = tmp_path / "input_folder_node_skip.png"
    nodes = [
        _node("input_image_folder", enabled=True, parameters={"folder_path": "x"}),
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


def test_image_folder_node_created(qtbot, monkeypatch, tmp_path):
    window = MainWindow()

    selected_folder = tmp_path / "images"
    selected_folder.mkdir()
    opened_folders = []

    monkeypatch.setattr(
        main_window_module.QFileDialog,
        "getExistingDirectory",
        lambda *_args, **_kwargs: str(selected_folder),
    )
    monkeypatch.setattr(
        window.image_controller,
        "handle_open_folder",
        lambda folder_path: opened_folders.append(folder_path),
    )

    window.action_open_folder()

    folder_nodes = [
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_image_folder"
    ]
    single_nodes = [
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_single_image"
    ]

    assert opened_folders == [str(selected_folder)]
    assert len(folder_nodes) == 1
    assert folder_nodes[0].name == "Image Folder"
    assert folder_nodes[0].type == "input_image_folder"
    assert folder_nodes[0].parameters["folder_path"] == str(selected_folder.resolve())
    assert len(single_nodes) == 0
    window.close()


def test_open_image_clears_folder_input(qtbot, monkeypatch, tmp_path):
    window = MainWindow()

    selected_folder = tmp_path / "images"
    selected_folder.mkdir()
    selected_image = tmp_path / "single.png"
    selected_image.write_bytes((FIXTURES_DIR / "synthetic_stem_cells.png").read_bytes())
    opened_images = []

    window._create_image_folder_node(str(selected_folder))

    monkeypatch.setattr(
        main_window_module.QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(selected_image), ""),
    )
    monkeypatch.setattr(
        window.image_controller,
        "handle_open_single_image",
        lambda file_path: opened_images.append(file_path),
    )

    window.action_open_image()

    folder_nodes = [
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_image_folder"
    ]
    single_nodes = [
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_single_image"
    ]

    assert opened_images == [str(selected_image)]
    assert len(folder_nodes) == 0
    assert len(single_nodes) == 1
    assert single_nodes[0].parameters["file_path"] == str(selected_image)
    window.close()


def test_open_folder_clears_single_input(qtbot, monkeypatch, tmp_path):
    window = MainWindow()

    selected_image = tmp_path / "stale.png"
    selected_folder = tmp_path / "images"
    selected_folder.mkdir()
    opened_folders = []

    window._create_single_image_node(str(selected_image))

    monkeypatch.setattr(
        main_window_module.QFileDialog,
        "getExistingDirectory",
        lambda *_args, **_kwargs: str(selected_folder),
    )
    monkeypatch.setattr(
        window.image_controller,
        "handle_open_folder",
        lambda folder_path: opened_folders.append(folder_path),
    )

    window.action_open_folder()

    folder_nodes = [
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_image_folder"
    ]
    single_nodes = [
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_single_image"
    ]

    assert opened_folders == [str(selected_folder)]
    assert len(folder_nodes) == 1
    assert len(single_nodes) == 0
    assert folder_nodes[0].parameters["folder_path"] == str(selected_folder.resolve())
    window.close()


def test_image_folder_node_replaced(qtbot, tmp_path):
    window = MainWindow()

    stale_image = tmp_path / "stale.png"
    first_folder = tmp_path / "folder_a"
    second_folder = tmp_path / "folder_b"
    first_folder.mkdir()
    second_folder.mkdir()

    window._create_single_image_node(str(stale_image))
    window._create_image_folder_node(str(first_folder))
    window._create_image_folder_node(str(second_folder))

    folder_nodes = [
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_image_folder"
    ]
    single_nodes = [
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_single_image"
    ]

    assert len(folder_nodes) == 1
    assert folder_nodes[0].name == "Image Folder"
    assert folder_nodes[0].type == "input_image_folder"
    assert folder_nodes[0].parameters["folder_path"] == str(second_folder.resolve())
    assert len(single_nodes) == 0
    window.close()


def test_image_folder_node_metadata_refresh_on_reopen(qtbot, tmp_path):
    window = MainWindow()

    first_folder = tmp_path / "folder_first"
    second_folder = tmp_path / "folder_second"
    first_folder.mkdir()
    second_folder.mkdir()

    window._create_image_folder_node(str(first_folder))
    first_node = next(
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_image_folder"
    )
    first_node_id = first_node.id

    first_node.parameters["stale"] = "value"
    first_node.description = "Input folder: stale"

    window._create_image_folder_node(str(second_folder))

    folder_nodes_after_second_open = [
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_image_folder"
    ]
    assert len(folder_nodes_after_second_open) == 1

    refreshed_node = folder_nodes_after_second_open[0]
    assert refreshed_node.id == first_node_id
    assert refreshed_node.parameters == {"folder_path": str(second_folder.resolve())}
    assert refreshed_node.description == f"Input folder: {str(second_folder.resolve())}"

    window._create_image_folder_node(str(first_folder))

    folder_nodes_after_third_open = [
        node
        for node in window.pipeline_controller.pipeline.nodes
        if node.type == "input_image_folder"
    ]
    assert len(folder_nodes_after_third_open) == 1
    assert folder_nodes_after_third_open[0].id == first_node_id
    assert folder_nodes_after_third_open[0].parameters == {
        "folder_path": str(first_folder.resolve())
    }
    assert (
        folder_nodes_after_third_open[0].description
        == f"Input folder: {str(first_folder.resolve())}"
    )
    window.close()


def test_batch_input_snapshot_filtering(qtbot, tmp_path):
    window = MainWindow()

    input_folder = tmp_path / "input_batch"
    input_folder.mkdir()

    file_names = [
        "zeta.JPG",
        "alpha_processed.png",
        "beta_mask.png",
        "gamma.tif",
        "notes.txt",
        "epsilon.jpeg",
        "delta_processed_1.tiff",
        "theta_mask_2.jpg",
    ]
    for file_name in file_names:
        (input_folder / file_name).write_bytes(b"x")

    window.image_model.current_folder = str(input_folder)
    window.image_model.files = [
        "zeta.JPG",
        "theta_mask_2.jpg",
        "alpha_processed.png",
        "gamma.tif",
        "notes.txt",
        "epsilon.jpeg",
        "delta_processed_1.tiff",
        "beta_mask.png",
        "missing.png",
    ]

    snapshot = window._collect_folder_batch_input_snapshot()
    expected = [
        str((input_folder / "epsilon.jpeg").resolve()),
        str((input_folder / "gamma.tif").resolve()),
        str((input_folder / "zeta.JPG").resolve()),
    ]

    assert snapshot == expected
    assert all(Path(path).is_absolute() for path in snapshot)

    window.image_model.files.append("aaa.png")
    assert snapshot == expected
    window.close()


def test_batch_input_snapshot_filtering_artifact_only_or_empty_folder(qtbot, tmp_path):
    window = MainWindow()

    artifact_folder = tmp_path / "artifact_only"
    artifact_folder.mkdir()
    (artifact_folder / "cell_processed.png").write_bytes(b"x")
    (artifact_folder / "cell_mask.tif").write_bytes(b"x")

    window.image_model.current_folder = str(artifact_folder)
    window.image_model.files = ["cell_mask.tif", "cell_processed.png"]
    assert window._collect_folder_batch_input_snapshot() == []

    window.image_model.files = []
    assert window._collect_folder_batch_input_snapshot() == []
    window.close()


def test_folder_mode_run_gate(qtbot, tmp_path):
    window = MainWindow()

    input_folder = tmp_path / "folder_mode"
    input_folder.mkdir()
    (input_folder / "eligible.png").write_bytes(b"x")
    (input_folder / "eligible_mask.png").write_bytes(b"x")
    (input_folder / "eligible_processed.png").write_bytes(b"x")

    window.image_model.current_folder = str(input_folder)
    window.image_model.files = [
        "eligible_mask.png",
        "eligible_processed.png",
        "eligible.png",
    ]
    window.current_image_path = None

    window._create_image_folder_node(str(input_folder))
    processing_node = _node("clahe", enabled=True)
    window.pipeline_controller.add_node(processing_node)

    window._update_run_button_state()
    assert window.pipeline_stack.run_button.isEnabled()

    processing_node.enabled = False
    window._update_run_button_state()
    assert not window.pipeline_stack.run_button.isEnabled()

    processing_node.enabled = True
    window.image_model.files = ["eligible_mask.png", "eligible_processed.png"]
    window._update_run_button_state()
    assert not window.pipeline_stack.run_button.isEnabled()
    window.close()


def test_folder_mode_run_gate_preserves_single_image_logic(qtbot, tmp_path):
    window = MainWindow()

    window.pipeline_controller.add_node(
        _node(
            "input_single_image",
            enabled=True,
            parameters={"file_path": "placeholder.png"},
        )
    )

    window.current_image_path = None
    window._update_run_button_state()
    assert not window.pipeline_stack.run_button.isEnabled()

    window.current_image_path = str(tmp_path / "selected.png")
    window._update_run_button_state()
    assert window.pipeline_stack.run_button.isEnabled()
    window.close()


def test_single_image_run_remains_non_batch(qtbot, monkeypatch, tmp_path):
    window = MainWindow()

    selected_image = tmp_path / "selected.png"
    selected_image.write_bytes((FIXTURES_DIR / "synthetic_stem_cells.png").read_bytes())

    window.image_model.mode = "SINGLE"
    window.current_image_path = str(selected_image)
    window.pipeline_controller.add_node(
        _node(
            "input_single_image",
            enabled=True,
            parameters={"file_path": str(selected_image)},
        )
    )
    window.pipeline_controller.add_node(_node("clahe", enabled=True))

    monkeypatch.setattr(window, "_set_processing_state", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(window, "_update_run_button_state", lambda: None)
    monkeypatch.setattr(
        window, "_get_current_metadata", lambda: {"filename": "out.png"}
    )
    monkeypatch.setattr(
        window.image_canvas, "load_image", lambda *_args, **_kwargs: True
    )
    monkeypatch.setattr(window.comparison_controls, "show", lambda: None)
    monkeypatch.setattr(
        window.comparison_controls,
        "set_view_mode",
        lambda *_args, **_kwargs: None,
    )

    starts = []

    def _start(input_path, output_path, _nodes, _registry):
        starts.append((input_path, output_path))
        return True

    monkeypatch.setattr(window.pipeline_executor, "start", _start)

    window.handle_run_pipeline()

    assert len(starts) == 1
    assert Path(starts[0][0]).name == "selected.png"
    assert window._batch_queue == []
    assert window._batch_success_count == 0
    assert window._batch_failure_count == 0

    window._handle_pipeline_finished(starts[0][1])

    assert window.status_label.text() == "Processing complete"
    assert window._batch_queue == []
    assert window._batch_success_count == 0
    assert window._batch_failure_count == 0
    window.close()


def test_folder_batch_run_success(qtbot, monkeypatch, tmp_path):
    window = MainWindow()

    input_folder = tmp_path / "batch_success"
    input_folder.mkdir()
    for file_name in [
        "b.png",
        "a.png",
        "c.tif",
        "a_processed.png",
        "b_mask.png",
        "notes.txt",
    ]:
        (input_folder / file_name).write_bytes(b"x")

    window.image_model.mode = "FOLDER"
    window.image_model.current_folder = str(input_folder)
    window.image_model.files = [
        "b.png",
        "a.png",
        "a_processed.png",
        "notes.txt",
        "b_mask.png",
        "c.tif",
    ]
    window._create_image_folder_node(str(input_folder))
    window.pipeline_controller.add_node(_node("clahe", enabled=True))

    monkeypatch.setattr(window, "_set_processing_state", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(window, "_update_run_button_state", lambda: None)
    monkeypatch.setattr(
        window, "_get_current_metadata", lambda: {"filename": "out.png"}
    )
    monkeypatch.setattr(
        window.image_canvas, "load_image", lambda *_args, **_kwargs: True
    )
    monkeypatch.setattr(window.comparison_controls, "show", lambda: None)
    monkeypatch.setattr(
        window.comparison_controls,
        "set_view_mode",
        lambda *_args, **_kwargs: None,
    )

    captured_metadata = []
    monkeypatch.setattr(
        window.right_panel,
        "show_metadata",
        lambda metadata: captured_metadata.append(metadata),
    )

    starts = []

    def _start(input_path, output_path, _nodes, _registry):
        starts.append((input_path, output_path))
        return True

    monkeypatch.setattr(window.pipeline_executor, "start", _start)

    window.handle_run_pipeline()

    assert [Path(call[0]).name for call in starts] == ["a.png"]

    while len(starts) < 3:
        window._handle_pipeline_finished(starts[-1][1])
    window._handle_pipeline_finished(starts[-1][1])

    assert [Path(call[0]).name for call in starts] == ["a.png", "b.png", "c.tif"]
    assert len(starts) == 3
    assert window.status_label.text() == "Batch complete: 3 succeeded, 0 failed"
    assert captured_metadata
    assert (
        captured_metadata[-1]["subtitle"] == "Batch run complete: 3 succeeded, 0 failed"
    )
    assert window._batch_queue == []
    window.close()


def test_batch_output_path_per_input_follows_sorted_queue_order(
    qtbot, monkeypatch, tmp_path
):
    window = MainWindow()

    input_folder = tmp_path / "batch_output_paths"
    input_folder.mkdir()
    for file_name in ["c.png", "a.png", "b.png"]:
        (input_folder / file_name).write_bytes(b"x")

    window.image_model.mode = "FOLDER"
    window.image_model.current_folder = str(input_folder)
    window.image_model.files = ["c.png", "a.png", "b.png"]
    window._create_image_folder_node(str(input_folder))
    window.pipeline_controller.add_node(_node("clahe", enabled=True))

    monkeypatch.setattr(window, "_set_processing_state", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(window, "_update_run_button_state", lambda: None)
    monkeypatch.setattr(
        window, "_get_current_metadata", lambda: {"filename": "out.png"}
    )
    monkeypatch.setattr(
        window.image_canvas, "load_image", lambda *_args, **_kwargs: True
    )
    monkeypatch.setattr(window.comparison_controls, "show", lambda: None)
    monkeypatch.setattr(
        window.comparison_controls,
        "set_view_mode",
        lambda *_args, **_kwargs: None,
    )

    generated_inputs = []
    generated_outputs = []

    def _generate_output_path(input_path):
        generated_inputs.append(input_path)
        output_path = str(
            (tmp_path / f"{Path(input_path).stem}_processed.png").resolve()
        )
        generated_outputs.append(output_path)
        return output_path

    monkeypatch.setattr(window, "_generate_output_path", _generate_output_path)

    starts = []

    def _start(input_path, output_path, _nodes, _registry):
        starts.append((input_path, output_path))
        return True

    monkeypatch.setattr(window.pipeline_executor, "start", _start)

    window.handle_run_pipeline()

    while len(starts) < 3:
        window._handle_pipeline_finished(starts[-1][1])
    window._handle_pipeline_finished(starts[-1][1])

    assert [Path(path).name for path in generated_inputs] == ["a.png", "b.png", "c.png"]
    assert [Path(call[0]).name for call in starts] == ["a.png", "b.png", "c.png"]
    assert generated_inputs == [call[0] for call in starts]
    assert generated_outputs == [call[1] for call in starts]
    assert len(generated_inputs) == 3
    window.close()


def test_folder_batch_continue_on_error(qtbot, monkeypatch, tmp_path):
    window = MainWindow()

    input_folder = tmp_path / "batch_continue"
    input_folder.mkdir()
    for file_name in ["c.png", "a.png", "b.png"]:
        (input_folder / file_name).write_bytes(b"x")

    window.image_model.mode = "FOLDER"
    window.image_model.current_folder = str(input_folder)
    window.image_model.files = ["c.png", "a.png", "b.png"]
    window._create_image_folder_node(str(input_folder))
    window.pipeline_controller.add_node(_node("clahe", enabled=True))

    monkeypatch.setattr(window, "_set_processing_state", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(window, "_update_run_button_state", lambda: None)
    monkeypatch.setattr(
        window, "_get_current_metadata", lambda: {"filename": "out.png"}
    )
    monkeypatch.setattr(
        window.image_canvas, "load_image", lambda *_args, **_kwargs: True
    )
    monkeypatch.setattr(window.comparison_controls, "show", lambda: None)
    monkeypatch.setattr(
        window.comparison_controls,
        "set_view_mode",
        lambda *_args, **_kwargs: None,
    )

    shown_errors = []
    monkeypatch.setattr(
        window, "_show_error_dialog", lambda message: shown_errors.append(message)
    )

    captured_metadata = []
    monkeypatch.setattr(
        window.right_panel,
        "show_metadata",
        lambda metadata: captured_metadata.append(metadata),
    )

    starts = []

    def _start(input_path, output_path, _nodes, _registry):
        starts.append((input_path, output_path))
        return True

    monkeypatch.setattr(window.pipeline_executor, "start", _start)

    window.handle_run_pipeline()
    window._handle_pipeline_finished(starts[0][1])
    window._handle_pipeline_error("second item failed")
    window._handle_pipeline_finished(starts[2][1])

    assert [Path(call[0]).name for call in starts] == ["a.png", "b.png", "c.png"]
    assert len(starts) == 3
    assert shown_errors == []
    assert window.status_label.text() == "Batch complete: 2 succeeded, 1 failed"
    assert captured_metadata
    assert (
        captured_metadata[-1]["subtitle"] == "Batch run complete: 2 succeeded, 1 failed"
    )
    assert window._batch_queue == []
    window.close()


def test_batch_error_no_dialog_spam(qtbot, monkeypatch, tmp_path):
    window = MainWindow()

    input_folder = tmp_path / "batch_no_dialog"
    input_folder.mkdir()
    for file_name in ["a.png", "b.png"]:
        (input_folder / file_name).write_bytes(b"x")

    window.image_model.mode = "FOLDER"
    window.image_model.current_folder = str(input_folder)
    window.image_model.files = ["a.png", "b.png"]
    window._create_image_folder_node(str(input_folder))
    window.pipeline_controller.add_node(_node("clahe", enabled=True))

    monkeypatch.setattr(window, "_set_processing_state", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(window, "_update_run_button_state", lambda: None)

    shown_errors = []
    monkeypatch.setattr(
        window, "_show_error_dialog", lambda message: shown_errors.append(message)
    )

    captured_metadata = []
    monkeypatch.setattr(
        window.right_panel,
        "show_metadata",
        lambda metadata: captured_metadata.append(metadata),
    )

    starts = []

    def _start(input_path, output_path, _nodes, _registry):
        starts.append((input_path, output_path))
        return True

    monkeypatch.setattr(window.pipeline_executor, "start", _start)

    window.handle_run_pipeline()
    window._handle_pipeline_error("first failed")
    window._handle_pipeline_error("second failed")

    assert len(starts) == 2
    assert shown_errors == []
    assert window.status_label.text() == "Batch complete: 0 succeeded, 2 failed"
    assert captured_metadata
    assert (
        captured_metadata[-1]["subtitle"] == "Batch run complete: 0 succeeded, 2 failed"
    )
    window.close()
