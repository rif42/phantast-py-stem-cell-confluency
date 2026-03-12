"""Asynchronous pipeline processing worker."""

from __future__ import annotations

import os
import logging
from typing import Any, Iterable, Mapping

import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


logger = logging.getLogger(__name__)


def get_base_name(filepath: str) -> str:
    """Extract base name without extension and _processed suffix."""
    name = os.path.splitext(os.path.basename(filepath))[0]
    if name.endswith("_processed"):
        name = name[:-10]
    return name


def create_green_mask_overlay(binary_mask: np.ndarray) -> np.ndarray:
    """Convert binary mask to green RGBA overlay with 40% opacity."""
    height, width = binary_mask.shape
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    rgba[binary_mask > 0] = [0, 255, 0, 102]
    return rgba


class PipelineWorker(QObject):
    """Execute image processing pipeline steps in a worker thread."""

    started = pyqtSignal()
    progress = pyqtSignal(str, int)
    step_completed = pyqtSignal(str, object)
    mask_saved = pyqtSignal(str, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    @pyqtSlot(str, str, object, object)
    def process_pipeline(
        self,
        input_path: str,
        output_path: str,
        nodes: Iterable[Any],
        step_registry: Mapping[str, Any],
    ) -> None:
        """Load image, run enabled nodes, and persist the output image."""
        try:
            self.started.emit()

            image = cv2.imread(os.path.abspath(input_path), cv2.IMREAD_UNCHANGED)
            if image is None:
                raise ValueError(f"Unable to load image: {input_path}")

            executable_nodes = [
                node
                for node in nodes
                if self._node_enabled(node)
                and self._node_type(node)
                not in {"input_single_image", "input_image_folder"}
            ]
            processed_image = image

            if not executable_nodes:
                self.progress.emit("save", 100)
            else:
                total_steps = len(executable_nodes)
                for step_index, node in enumerate(executable_nodes, start=1):
                    step_name = self._node_type(node)
                    self.progress.emit(
                        step_name, int(((step_index - 1) / total_steps) * 100)
                    )

                    step = step_registry.get(step_name)
                    if step is None:
                        raise ValueError(f"Unknown step type: {step_name}")

                    params = self._node_parameters(node)
                    processed_image = step.process(processed_image, **params)
                    if processed_image is None:
                        raise ValueError(f"Step '{step_name}' returned no image")

                    if step_name == "phantast" and processed_image.ndim == 2:
                        try:
                            overlay = create_green_mask_overlay(processed_image)
                            base_name = get_base_name(output_path)
                            output_dir = os.path.dirname(output_path)
                            mask_path = os.path.join(
                                output_dir, f"{base_name}_mask.png"
                            )

                            if cv2.imwrite(mask_path, overlay):
                                self.mask_saved.emit(input_path, mask_path)
                                logger.info("Mask saved to %s", mask_path)
                            else:
                                logger.error("Failed to save mask to %s", mask_path)
                        except (
                            Exception
                        ) as mask_exc:  # pragma: no cover - graceful path
                            logger.error(
                                "Mask save failed for %s: %s", output_path, mask_exc
                            )

                    self.step_completed.emit(step_name, processed_image)
                    self.progress.emit(step_name, int((step_index / total_steps) * 100))

            output_image = self._prepare_for_save(processed_image)
            if not cv2.imwrite(output_path, output_image):
                raise OSError(f"Failed to save processed image to: {output_path}")

            self.finished.emit(output_path)
        except Exception as exc:  # pragma: no cover - signal path covered in tests
            self.error.emit(str(exc))

    @staticmethod
    def _node_type(node: Any) -> str:
        if hasattr(node, "type"):
            return getattr(node, "type")
        if isinstance(node, dict):
            return str(node.get("type", ""))
        return ""

    @staticmethod
    def _node_enabled(node: Any) -> bool:
        if hasattr(node, "enabled"):
            return bool(getattr(node, "enabled"))
        if isinstance(node, dict):
            return bool(node.get("enabled", True))
        return True

    @staticmethod
    def _node_parameters(node: Any) -> dict[str, Any]:
        if hasattr(node, "parameters"):
            params = getattr(node, "parameters")
            return params if isinstance(params, dict) else {}
        if isinstance(node, dict):
            params = node.get("parameters", {})
            return params if isinstance(params, dict) else {}
        return {}

    @staticmethod
    def _prepare_for_save(processed_image: np.ndarray) -> np.ndarray:
        if processed_image.dtype == np.bool_:
            processed_image = processed_image.astype(np.uint8) * 255
        elif processed_image.dtype != np.uint8:
            processed_image = np.nan_to_num(processed_image)
            min_val = float(np.min(processed_image))
            max_val = float(np.max(processed_image))
            if max_val > min_val:
                processed_image = (
                    (processed_image - min_val) * (255.0 / (max_val - min_val))
                ).astype(np.uint8)
            else:
                processed_image = np.zeros_like(processed_image, dtype=np.uint8)

        if processed_image.ndim == 2:
            return cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
        if processed_image.ndim == 3 and processed_image.shape[2] == 1:
            return cv2.cvtColor(processed_image[:, :, 0], cv2.COLOR_GRAY2BGR)
        if processed_image.ndim == 3 and processed_image.shape[2] == 4:
            return cv2.cvtColor(processed_image, cv2.COLOR_BGRA2BGR)
        if processed_image.ndim == 3 and processed_image.shape[2] == 3:
            return processed_image
        raise ValueError(f"Unsupported processed image shape: {processed_image.shape}")
