"""Task 9 verification runner for pipeline feature.

Runs headless end-to-end checks against real project images and writes
machine-readable evidence logs under .sisyphus/evidence/task-9/.
"""

from __future__ import annotations

import gc
import json
import os
import shutil
import sys
import time
import tracemalloc
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np
from PyQt6.QtCore import QEventLoop, QTimer
from PyQt6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if TYPE_CHECKING:
    from src.ui.main_window import MainWindow


EVIDENCE_DIR = ROOT / ".sisyphus" / "evidence" / "task-9"
RUNTIME_DIR = EVIDENCE_DIR / "runtime_data"
MANUAL_LOG = EVIDENCE_DIR / "manual-test-results.json"
PERF_LOG = EVIDENCE_DIR / "performance-data.json"


def wait_for_executor(window: "MainWindow", timeout_ms: int = 300000) -> None:
    """Wait until pipeline executor finishes or timeout expires."""
    if not window.pipeline_executor.is_running():
        return

    loop = QEventLoop()
    timer = QTimer()
    timer.setSingleShot(True)
    timed_out = {"value": False}

    def _on_timeout() -> None:
        timed_out["value"] = True
        loop.quit()

    timer.timeout.connect(_on_timeout)
    window.pipeline_executor.finished.connect(loop.quit)
    window.pipeline_executor.error.connect(loop.quit)

    timer.start(timeout_ms)
    loop.exec()

    timer.stop()
    if timed_out["value"]:
        raise TimeoutError(f"Pipeline execution timed out after {timeout_ms}ms")


def prepare_runtime_images() -> dict[str, Path]:
    """Copy real project images and build one >10MB derived case."""
    if RUNTIME_DIR.exists():
        shutil.rmtree(RUNTIME_DIR)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    src_jpg = ROOT / "test_images" / "sample_images" / "test_06.jpg"
    src_png = ROOT / "test_images" / "sample_images" / "test_05.png"
    src_tiff = ROOT / "test_images" / "sample_images" / "test_07.tiff"

    jpg = RUNTIME_DIR / "real_sample.jpg"
    png = RUNTIME_DIR / "real_sample.png"
    tiff = RUNTIME_DIR / "real_sample.tiff"
    shutil.copy2(src_jpg, jpg)
    shutil.copy2(src_png, png)
    shutil.copy2(src_tiff, tiff)

    # Build a larger PNG (>10MB) derived from real data.
    tiff_image = cv2.imread(str(src_tiff), cv2.IMREAD_UNCHANGED)
    if tiff_image is None:
        raise RuntimeError(f"Unable to read source TIFF: {src_tiff}")
    factor = 2
    large_png = RUNTIME_DIR / "real_large_derived.png"
    while True:
        tiled = (
            np.tile(tiff_image, (factor, factor, 1))
            if tiff_image.ndim == 3
            else np.tile(tiff_image, (factor, factor))
        )
        if not cv2.imwrite(str(large_png), tiled, [cv2.IMWRITE_PNG_COMPRESSION, 0]):
            raise RuntimeError(f"Unable to write large PNG: {large_png}")
        if large_png.stat().st_size > 10 * 1024 * 1024:
            break
        factor += 1

    return {
        "jpg": jpg,
        "png": png,
        "tiff": tiff,
        "large_png": large_png,
    }


def configure_two_step_pipeline(window: "MainWindow") -> None:
    """Set CLAHE + PHANTAST nodes with defaults."""
    window.pipeline_controller.pipeline.nodes = []
    window._refresh_pipeline_view()
    window._update_run_button_state()
    window.handle_add_step("clahe")
    window.handle_add_step("phantast")


def run_single_mode_case(window: "MainWindow", image_path: Path) -> dict:
    """Run pipeline in single-image mode and return result metadata."""
    window.image_controller.handle_open_single_image(str(image_path))
    configure_two_step_pipeline(window)

    before = set(p.name for p in image_path.parent.iterdir() if p.is_file())
    started = time.perf_counter()
    window.handle_run_pipeline()
    wait_for_executor(window)
    elapsed = time.perf_counter() - started
    after = set(p.name for p in image_path.parent.iterdir() if p.is_file())
    new_files = sorted(after - before)

    current_path = window.current_image_path
    out_path = Path(str(current_path)) if current_path else None
    return {
        "mode": "single",
        "input": str(image_path),
        "elapsed_sec": round(elapsed, 3),
        "new_files": new_files,
        "output": str(out_path) if out_path else None,
        "output_exists": bool(out_path and out_path.exists()),
        "status_text": window.status_label.text(),
    }


def run_folder_mode_case(window: "MainWindow", folder_path: Path) -> dict:
    """Run pipeline in folder mode and verify explorer list updates."""
    window.image_controller.handle_open_folder(str(folder_path))
    if not window.image_model.files:
        raise RuntimeError("Folder mode has no files to test")

    preferred = [
        name for name in window.image_model.files if name.lower().endswith(".jpg")
    ]
    chosen = preferred[0] if preferred else window.image_model.files[0]
    window.image_controller.handle_file_selected(chosen)
    configure_two_step_pipeline(window)

    before_files = set(window.image_model.files)
    started = time.perf_counter()
    window.handle_run_pipeline()
    wait_for_executor(window)
    elapsed = time.perf_counter() - started
    after_files = set(window.image_model.files)

    output_path = window.current_image_path
    if not output_path:
        raise RuntimeError("Pipeline did not set current_image_path in folder mode")
    produced_filename = Path(str(output_path)).name
    return {
        "mode": "folder",
        "folder": str(folder_path),
        "selected_input": chosen,
        "elapsed_sec": round(elapsed, 3),
        "output_filename": produced_filename,
        "output_in_model_files": produced_filename in after_files,
        "file_list_grew": len(after_files) > len(before_files),
    }


def run_rapid_start_case(window: "MainWindow", image_path: Path) -> dict:
    """Fire rapid run clicks and verify only one execution starts."""
    window.image_controller.handle_open_single_image(str(image_path))
    configure_two_step_pipeline(window)

    before_count = len(list(image_path.parent.glob("*_processed*.jpg")))
    start = time.perf_counter()
    window.handle_run_pipeline()
    for _ in range(5):
        window.handle_run_pipeline()
    wait_for_executor(window)
    elapsed = time.perf_counter() - start
    after_count = len(list(image_path.parent.glob("*_processed*.jpg")))

    return {
        "mode": "single",
        "scenario": "rapid_start",
        "input": str(image_path),
        "elapsed_sec": round(elapsed, 3),
        "new_output_count": after_count - before_count,
        "executor_running_after": window.pipeline_executor.is_running(),
    }


def run_performance_case(window: "MainWindow", typical_image: Path) -> dict:
    """Measure timing and memory trend on a typical image."""
    window.image_controller.handle_open_single_image(str(typical_image))
    configure_two_step_pipeline(window)

    tracemalloc.start()
    gc.collect()
    before_current, before_peak = tracemalloc.get_traced_memory()

    timings = []
    for _ in range(2):
        started = time.perf_counter()
        window.handle_run_pipeline()
        wait_for_executor(window)
        timings.append(time.perf_counter() - started)
        gc.collect()

    after_current, after_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "input": str(typical_image),
        "input_size_mb": round(typical_image.stat().st_size / (1024 * 1024), 3),
        "run1_sec": round(timings[0], 3),
        "run2_sec": round(timings[1], 3),
        "threshold_sec": 30.0,
        "under_threshold": timings[0] < 30.0 and timings[1] < 30.0,
        "tracemalloc_before_bytes": before_current,
        "tracemalloc_after_bytes": after_current,
        "tracemalloc_peak_bytes": max(before_peak, after_peak),
        "memory_growth_bytes": after_current - before_current,
        "memory_growth_under_8mb": (after_current - before_current) < 8 * 1024 * 1024,
    }


def main() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    images = prepare_runtime_images()

    from src.ui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()

    try:
        manual_cases = [
            run_single_mode_case(window, images["jpg"]),
            run_single_mode_case(window, images["png"]),
            run_single_mode_case(window, images["tiff"]),
            run_single_mode_case(window, images["large_png"]),
            run_folder_mode_case(window, RUNTIME_DIR),
            run_rapid_start_case(window, images["jpg"]),
        ]
        perf_case = run_performance_case(window, images["tiff"])
    finally:
        window.close()
        app.quit()

    MANUAL_LOG.write_text(
        json.dumps({"cases": manual_cases}, indent=2), encoding="utf-8"
    )
    PERF_LOG.write_text(json.dumps(perf_case, indent=2), encoding="utf-8")

    print(f"Manual results written: {MANUAL_LOG}")
    print(f"Performance results written: {PERF_LOG}")


if __name__ == "__main__":
    main()
