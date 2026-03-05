"""
Preview Pipeline Executor

Executes the image processing pipeline on the current image for real-time preview.
Includes caching and async execution support.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from ..models.app_state import AppState
from ..models.pipeline_model import PipelineNode
from ..core.steps.grayscale_step import GrayscaleStep
from ..core.steps.gaussian_blur_step import GaussianBlurStep
from ..core.steps.clahe_step import ClaheStep
from ..core.steps.phantast_step import PhantastStep


logger = logging.getLogger(__name__)


@dataclass
class PreviewResult:
    """Result of a preview pipeline execution."""

    success: bool
    image: Optional[np.ndarray] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    node_results: Optional[Dict[str, Any]] = None


class PreviewPipeline:
    """
    Executes the image processing pipeline for real-time preview.

    Features:
    - Caching of intermediate results
    - Async execution support
    - Progress reporting
    - Error handling
    """

    def __init__(self, cache_enabled: bool = True):
        super().__init__()

        self._cache_enabled = cache_enabled
        self._cache: Dict[str, np.ndarray] = {}
        self._executor = ThreadPoolExecutor(max_workers=1)

        # Signals (will be connected to UI)
        self._callbacks = {
            "execution_started": [],
            "progress_updated": [],
            "node_completed": [],
            "execution_completed": [],
            "execution_failed": [],
        }

        logger.info("PreviewPipeline initialized")

    # Signal-like callback system
    @property
    def execution_started(self):
        return self._create_signal_proxy("execution_started")

    @property
    def progress_updated(self):
        return self._create_signal_proxy("progress_updated")

    @property
    def node_completed(self):
        return self._create_signal_proxy("node_completed")

    @property
    def execution_completed(self):
        return self._create_signal_proxy("execution_completed")

    @property
    def execution_failed(self):
        return self._create_signal_proxy("execution_failed")

    def _create_signal_proxy(self, signal_name: str):
        """Create a proxy object that mimics pyqtSignal connect/disconnect."""

        class SignalProxy:
            def __init__(proxy_self, pipeline, name):
                proxy_self.pipeline = pipeline
                proxy_self.name = name

            def connect(proxy_self, callback):
                if callback not in proxy_self.pipeline._callbacks[proxy_self.name]:
                    proxy_self.pipeline._callbacks[proxy_self.name].append(callback)

            def disconnect(proxy_self, callback):
                if callback in proxy_self.pipeline._callbacks[proxy_self.name]:
                    proxy_self.pipeline._callbacks[proxy_self.name].remove(callback)

            def emit(proxy_self, *args):
                for callback in proxy_self.pipeline._callbacks[proxy_self.name]:
                    try:
                        callback(*args)
                    except Exception as e:
                        logger.error(f"Error in {proxy_self.name} callback: {e}")

        return SignalProxy(self, signal_name)

    def execute(
        self,
        input_image: np.ndarray,
        pipeline: AppState,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> PreviewResult:
        """
        Execute the preview pipeline.

        Args:
            input_image: Input image as numpy array
            pipeline: AppState containing pipeline configuration
            progress_callback: Optional callback(current, total) for progress

        Returns:
            PreviewResult with success status and output image
        """
        start_time = time.time()

        self.execution_started.emit()

        try:
            # Get enabled nodes only
            nodes = [node for node in pipeline.pipeline.nodes if node.enabled]

            if not nodes:
                return PreviewResult(
                    success=False, error_message="No enabled nodes in pipeline"
                )

            # Execute node by node
            current_image = input_image.copy()
            node_results = {}
            metadata = {}  # Shared metadata across nodes

            for i, node in enumerate(nodes):
                # Update progress
                self.progress_updated.emit(i + 1, len(nodes))
                if progress_callback:
                    progress_callback(i + 1, len(nodes))

                # Execute node
                result = self._execute_node(node, current_image, metadata)

                if not result["success"]:
                    return PreviewResult(
                        success=False,
                        error_message=f"Node '{node.name}' failed: {result.get('error')}",
                    )

                current_image = result["image"]
                node_results[node.id] = {
                    "name": node.name,
                    "output": current_image.copy(),
                }

                # Emit node completion signal
                self.node_completed.emit(node.id, current_image.copy())

            execution_time = (time.time() - start_time) * 1000

            result = PreviewResult(
                success=True,
                image=current_image,
                execution_time_ms=execution_time,
                node_results=node_results,
            )

            self.execution_completed.emit(result)
            return result

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            self.execution_failed.emit(str(e))
            return PreviewResult(success=False, error_message=str(e))

    def _execute_node(
        self, node: PipelineNode, input_image: np.ndarray, metadata: dict
    ) -> Dict[str, Any]:
        """
        Execute a single node.

        Args:
            node: PipelineNode to execute
            input_image: Input image
            metadata: Metadata dictionary passed through pipeline

        Returns:
            Dict with 'success', 'image', and optional 'error'
        """
        try:
            # Check cache for input/output nodes (they don't change)
            if self._cache_enabled and node.type in ["input", "output"]:
                cache_key = f"{node.id}_{hash(input_image.tobytes())}"
                if cache_key in self._cache:
                    return {"success": True, "image": self._cache[cache_key]}

            # Execute based on node type
            if node.type == "input":
                # Input node just passes through
                result = input_image

            elif node.type == "grayscale":
                step = GrayscaleStep()
                result = step.process(input_image, metadata)

            elif node.type == "gaussian_blur":
                params = node.parameters
                step = GaussianBlurStep()
                step.set_param("kernel_size", params.get("kernel_size", 5))
                step.set_param("sigma", params.get("sigma", 1.0))
                result = step.process(input_image, metadata)

            elif node.type == "clahe":
                params = node.parameters
                step = ClaheStep()
                step.set_param("clip_limit", params.get("clip_limit", 2.0))
                step.set_param("tile_grid_size", params.get("grid_size", (8, 8)))
                result = step.process(input_image, metadata)

            elif node.type == "output":
                # PHANTAST output
                params = node.parameters
                step = PhantastStep()
                step.set_param("sigma", params.get("sigma", 5.0))
                step.set_param("epsilon", params.get("epsilon", 0.5))
                result = step.process(input_image, metadata)

            else:
                return {"success": False, "error": f"Unknown node type: {node.type}"}

            # Cache result
            if self._cache_enabled and node.type in ["input", "output"]:
                cache_key = f"{node.id}_{hash(input_image.tobytes())}"
                self._cache[cache_key] = result.copy()

            return {"success": True, "image": result}

        except Exception as e:
            logger.error(f"Node execution failed: {e}")
            return {"success": False, "error": str(e)}

    def execute_async(
        self,
        input_image: np.ndarray,
        pipeline: AppState,
        callback: Optional[Callable[[PreviewResult], None]] = None,
    ):
        """
        Execute pipeline asynchronously.

        Args:
            input_image: Input image as numpy array
            pipeline: AppState containing pipeline configuration
            callback: Optional callback to receive result
        """

        def _run():
            result = self.execute(input_image, pipeline)
            if callback:
                callback(result)
            return result

        return self._executor.submit(_run)

    def clear_cache(self):
        """Clear the execution cache."""
        self._cache.clear()
        logger.debug("Preview cache cleared")

    def set_cache_enabled(self, enabled: bool):
        """Enable or disable caching."""
        self._cache_enabled = enabled
        if not enabled:
            self.clear_cache()
        logger.debug(f"Cache enabled: {enabled}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "enabled": self._cache_enabled,
        }


# Type alias for backward compatibility
PipelineExecutor = PreviewPipeline
