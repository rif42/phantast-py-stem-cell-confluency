"""Asynchronous pipeline processing worker."""

from __future__ import annotations

import os
import sys
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


def apply_overlay_to_image(image: np.ndarray, overlay_rgba: np.ndarray) -> np.ndarray:
    """Alpha-blend an RGBA overlay onto an image, returning BGR result."""
    # Ensure base is 3-channel BGR
    if image.ndim == 2:
        base = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.ndim == 3 and image.shape[2] == 4:
        base = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    elif image.ndim == 3 and image.shape[2] == 3:
        base = image.copy()
    else:
        base = cv2.cvtColor(image[:, :, 0], cv2.COLOR_GRAY2BGR)

    alpha = overlay_rgba[:, :, 3:4].astype(np.float32) / 255.0
    blended = (
        base.astype(np.float32) * (1.0 - alpha)
        + overlay_rgba[:, :, :3].astype(np.float32) * alpha
    )
    return np.clip(blended, 0, 255).astype(np.uint8)


# Logo reserved width in the header (logo scales to ~90px, reserve 100px)
LOGO_RESERVED_WIDTH = 100


def create_report_header(image: np.ndarray, metadata: dict) -> np.ndarray:
    """Create an 80px tall header band and stack it on top of the image."""
    height, width = image.shape[:2]

    # Skip header for small images
    if width < 400:
        return image

    # Create 60px tall black header
    header = np.zeros((60, width, 3), dtype=np.uint8)

    # Font settings (uniform across both sides)
    font = cv2.FONT_HERSHEY_SIMPLEX
    title_scale = 0.8
    subtitle_scale = 0.5
    title_thickness = 1
    subtitle_thickness = 1

    # Left side — title (offset to avoid logo)
    left_x = LOGO_RESERVED_WIDTH + 16
    cv2.putText(
        header,
        "Stem Cell Confluency Detector",
        (left_x, 28),
        font,
        title_scale,
        (255, 255, 255),
        title_thickness,
        cv2.LINE_AA,
    )

    # Left side — UUID (offset to avoid logo)
    cv2.putText(
        header,
        f"ID: {metadata.get('uuid', 'N/A')}",
        (left_x, 52),
        font,
        subtitle_scale,
        (180, 180, 180),
        subtitle_thickness,
        cv2.LINE_AA,
    )

    # Right side — confluency (right-aligned)
    confluency_text = f"Confluency: {metadata.get('confluency', 0.0):.1f}%"
    (cw, _), _ = cv2.getTextSize(confluency_text, font, title_scale, title_thickness)
    cv2.putText(
        header,
        confluency_text,
        (width - cw - 20, 28),
        font,
        title_scale,
        (255, 255, 255),
        title_thickness,
        cv2.LINE_AA,
    )

    # Right side — parameters (ASCII names; OpenCV cannot render Greek)
    params_text = (
        f"sigma={metadata.get('sigma', 0.0):.2f}  "
        f"epsilon={metadata.get('epsilon', 0.0):.2f}"
    )
    (pw, _), _ = cv2.getTextSize(params_text, font, subtitle_scale, subtitle_thickness)
    cv2.putText(
        header,
        params_text,
        (width - pw - 20, 52),
        font,
        subtitle_scale,
        (180, 180, 180),
        subtitle_thickness,
        cv2.LINE_AA,
    )

    # Vertically stack header on top of image
    return np.vstack([header, image])


def _get_logo_path() -> str:
    """Resolve path to sccrlogo.png (dev and PyInstaller compatible)."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return os.path.join(str(meipass), "sccrlogo.png")
    # In dev: project root (2 levels up from src/core/)
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "sccrlogo.png")
    )


def overlay_logo(image: np.ndarray) -> np.ndarray:
    """Overlay sccrlogo.png on the top-left corner of the report header.

    The logo is scaled to fit within the 60px header height with padding,
    placed on the left side. Text elements are offset to the right to avoid
    overlapping with the logo.
    If the logo file is missing or the image is too small, the original
    image is returned unchanged.
    """
    logo_path = _get_logo_path()
    if not os.path.isfile(logo_path):
        logger.warning("Logo not found at %s, skipping overlay", logo_path)
        return image

    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    if logo is None:
        return image

    height, width = image.shape[:2]

    # Skip overlay on images without sufficient width for header
    if width < 400:
        return image

    # Scale logo to fit within the 60px header height with padding
    header_height = 60
    logo_target_height = header_height - 16  # 8px top + 8px bottom padding
    scale = logo_target_height / logo.shape[0]
    logo_target_width = int(logo.shape[1] * scale)

    # Ensure logo doesn't exceed reasonable width
    if logo_target_width > width // 3:
        scale = (width // 3) / logo.shape[1]
        logo_target_height = int(logo.shape[0] * scale)
        logo_target_width = int(logo.shape[1] * scale)

    logo_resized = cv2.resize(
        logo, (logo_target_width, logo_target_height), interpolation=cv2.INTER_AREA
    )

    # Place logo on the left side of the header, vertically centered
    pad = 8
    y1 = pad
    y2 = pad + logo_target_height
    x1 = pad
    x2 = pad + logo_target_width

    if y2 > height or x2 > width:
        return image

    # Alpha blending for RGBA logo
    if logo_resized.ndim == 3 and logo_resized.shape[2] == 4:
        alpha = logo_resized[:, :, 3:4].astype(np.float32) / 255.0
        roi = image[y1:y2, x1:x2].astype(np.float32)
        blended = (
            roi * (1.0 - alpha) + logo_resized[:, :, :3].astype(np.float32) * alpha
        )
        image[y1:y2, x1:x2] = np.clip(blended, 0, 255).astype(np.uint8)
    else:
        image[y1:y2, x1:x2] = logo_resized[:, :, :3]

    return image


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
            report_metadata = {}

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
                    # Save image state before phantast for overlay compositing
                    pre_step_image = (
                        processed_image if step_name == "phantast" else None
                    )
                    try:
                        processed_image = step.process(
                            processed_image, _metadata=report_metadata, **params
                        )
                    except TypeError:
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

                            # Composite green overlay onto pre-step image
                            # so the processed output shows the green mask
                            processed_image = apply_overlay_to_image(
                                pre_step_image, overlay
                            )
                        except (
                            Exception
                        ) as mask_exc:  # pragma: no cover - graceful path
                            logger.error(
                                "Mask save failed for %s: %s", output_path, mask_exc
                            )

                    self.step_completed.emit(step_name, processed_image)
                    self.progress.emit(step_name, int((step_index / total_steps) * 100))

            output_image = self._prepare_for_save(processed_image)
            if report_metadata and output_image.shape[1] >= 400:
                output_image = create_report_header(output_image, report_metadata)
            output_image = overlay_logo(output_image)
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
