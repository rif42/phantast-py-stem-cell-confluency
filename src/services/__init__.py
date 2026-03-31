"""Services layer for business logic and external dependencies.

This package contains service classes that handle:
- Settings persistence (QSettings-based)
- Batch processing orchestration
- Image path utilities
- Pipeline state management

These services bridge the gap between pure Python models and PyQt6 UI,
keeping models/ free of GUI dependencies while allowing UI to use Qt features.
"""

from src.services.settings_service import (
    SettingsService,
    get_settings_service,
    initialize_settings_interface,
)
from src.services.batch_service import BatchService, BatchState
from src.services.image_service import ImageService
from src.services.pipeline_service import PipelineService

__all__ = [
    "SettingsService",
    "get_settings_service",
    "initialize_settings_interface",
    "BatchService",
    "BatchState",
    "ImageService",
    "PipelineService",
]
