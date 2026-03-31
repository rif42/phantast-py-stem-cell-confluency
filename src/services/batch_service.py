"""Batch processing service for folder-mode execution.

This module manages batch queue state and orchestrates folder-mode
processing without GUI dependencies.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class BatchState:
    """Immutable state container for batch processing."""

    input_snapshot: List[str] = field(default_factory=list)
    queue: List[str] = field(default_factory=list)
    current_index: int = -1
    success_count: int = 0
    failure_count: int = 0

    def is_active(self) -> bool:
        """Return True when batch orchestration is active."""
        return len(self.queue) > 0 and 0 <= self.current_index < len(self.queue)

    def total_items(self) -> int:
        """Return total number of items in the queue."""
        return len(self.queue)

    def current_item(self) -> Optional[str]:
        """Return the current item being processed, or None."""
        if not self.is_active():
            return None
        return self.queue[self.current_index]

    def progress_text(self) -> str:
        """Return progress text for display."""
        if not self.is_active():
            return ""
        return f"{self.current_index + 1}/{self.total_items()}"

    def summary(self) -> str:
        """Return batch completion summary."""
        total = self.total_items()
        return f"Batch complete: {self.success_count} succeeded, {self.failure_count} failed"


class BatchService:
    """Service for managing batch processing state and orchestration."""

    def __init__(self):
        """Initialize batch service with empty state."""
        self._state = BatchState()

    @property
    def state(self) -> BatchState:
        """Get current batch state (read-only)."""
        return self._state

    def start_batch(self, input_snapshot: List[str]) -> None:
        """Initialize batch processing with input files.

        Args:
            input_snapshot: List of absolute paths to input images
        """
        self._state = BatchState(
            input_snapshot=list(input_snapshot),
            queue=list(input_snapshot),
            current_index=0,
            success_count=0,
            failure_count=0,
        )

    def reset(self) -> None:
        """Reset batch state to empty."""
        self._state = BatchState()

    def mark_success(self) -> None:
        """Mark current item as successfully completed."""
        self._state.success_count += 1
        self._advance()

    def mark_failure(self) -> None:
        """Mark current item as failed."""
        self._state.failure_count += 1
        self._advance()

    def _advance(self) -> None:
        """Advance to next item in queue."""
        if self._state.current_index < len(self._state.queue) - 1:
            self._state.current_index += 1
        else:
            # Batch complete
            self._state.current_index = -1

    def get_current_item(self) -> Optional[str]:
        """Get the current item being processed."""
        return self._state.current_item()

    def is_active(self) -> bool:
        """Check if batch processing is currently active."""
        return self._state.is_active()

    @staticmethod
    def has_enabled_executable_nodes(nodes: List[Any]) -> bool:
        """Return True if at least one enabled non-input node exists.

        Args:
            nodes: List of pipeline nodes

        Returns:
            True if there's at least one enabled node that's not an input node
        """
        return any(
            node.enabled
            and node.type not in {"input_single_image", "input_image_folder"}
            for node in nodes
        )
