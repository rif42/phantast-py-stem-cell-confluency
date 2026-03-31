"""Image path utilities and file management services.

This module provides pure Python utilities for image path generation,
file discovery, and filename handling. No GUI dependencies.
"""

import os
from typing import List, Optional, Tuple


class ImageService:
    """Service for image path operations and file utilities."""

    @staticmethod
    def is_generated_artifact_filename(filename: str) -> bool:
        """Return True when a file name matches generated output artifacts.

        Args:
            filename: The filename to check

        Returns:
            True if filename contains '_processed' or '_mask'
        """
        lowered = filename.lower()
        return "_processed" in lowered or "_mask" in lowered

    @staticmethod
    def generate_output_path(input_path: str) -> str:
        """Generate a non-conflicting processed output path for an input image.

        Creates a path like 'image_processed.png' or 'image_processed_1.png'
        if a conflict exists.

        Args:
            input_path: Absolute path to the input image

        Returns:
            Absolute path for the processed output image
        """
        abs_input_path = os.path.abspath(input_path)
        directory = os.path.dirname(abs_input_path)

        filename = os.path.basename(abs_input_path)
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = ".png"

        base_name = name if name.endswith("_processed") else f"{name}_processed"
        counter = 1 if name.endswith("_processed") else 0

        candidate_name = base_name if counter == 0 else f"{base_name}_{counter}"
        candidate_path = os.path.abspath(
            os.path.join(directory, f"{candidate_name}{ext}")
        )

        while os.path.exists(candidate_path):
            counter = 1 if counter == 0 else counter + 1
            candidate_name = f"{base_name}_{counter}"
            candidate_path = os.path.abspath(
                os.path.join(directory, f"{candidate_name}{ext}")
            )

        return candidate_path

    @staticmethod
    def discover_existing_variants(
        filepath: str,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Search for existing _processed and _mask variants of the image.

        Args:
            filepath: Path to the original image

        Returns:
            Tuple of (processed_path, mask_path) - either may be None if not found
        """
        directory = os.path.dirname(filepath)
        basename = os.path.splitext(os.path.basename(filepath))[0]
        ext = os.path.splitext(filepath)[1].lower()

        processed_path = os.path.join(directory, f"{basename}_processed{ext}")
        mask_path = os.path.join(directory, f"{basename}_mask.png")

        found_processed = os.path.exists(processed_path)
        found_mask = os.path.exists(mask_path)

        return (
            processed_path if found_processed else None,
            mask_path if found_mask else None,
        )

    @staticmethod
    def get_file_size_formatted(filepath: str) -> str:
        """Get formatted file size string.

        Args:
            filepath: Path to the file

        Returns:
            Formatted string like '1.5 MB' or '500 KB'
        """
        if not filepath or not os.path.exists(filepath):
            return "-"

        try:
            size_bytes = os.path.getsize(filepath)
            for unit in ["B", "KB", "MB", "GB"]:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
        except OSError:
            return "-"

    @staticmethod
    def collect_folder_batch_input_snapshot(
        folder_path: str,
        files: List[str],
        valid_extensions: Tuple[str, ...] = (".png", ".jpg", ".jpeg", ".tif", ".tiff"),
    ) -> List[str]:
        """Collect deterministic, filtered folder-mode inputs as absolute paths.

        Args:
            folder_path: Base folder containing the images
            files: List of filenames in the folder
            valid_extensions: Tuple of valid file extensions

        Returns:
            List of absolute paths to valid input images
        """
        if not folder_path or not os.path.isdir(folder_path):
            return []

        absolute_folder = os.path.abspath(folder_path)

        valid_extensions_lower = tuple(ext.lower() for ext in valid_extensions)

        snapshot: List[str] = []
        for filename in sorted(files, key=lambda value: str(value).lower()):
            if not isinstance(filename, str):
                continue

            lowered_name = filename.lower()
            if not lowered_name.endswith(valid_extensions_lower):
                continue
            if ImageService.is_generated_artifact_filename(lowered_name):
                continue

            absolute_path = os.path.abspath(os.path.join(absolute_folder, filename))
            if os.path.isfile(absolute_path):
                snapshot.append(absolute_path)

        return snapshot
