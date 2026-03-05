import os
from typing import Optional, Dict, Any
import cv2
import numpy as np


class ImageSessionModel:
    """
    Manages the current state of an image viewing session (single file or folder).
    Contains no PyQt GUI or Qt classes, meaning it can be unit tested without Qt.
    """

    def __init__(self):
        self.mode = "EMPTY"  # EMPTY, SINGLE, FOLDER
        self.current_folder: Optional[str] = None
        self.active_image: Optional[Dict[str, Any]] = None
        self.files: list = []
        self.status: str = "raw"  # raw, processing, processed, error

        self.valid_extensions = (
            ".png",
            ".jpg",
            ".jpeg",
            ".tif",
            ".tiff",
            ".bmp",
            ".PNG",
            ".JPG",
            ".JPEG",
            ".TIF",
            ".TIFF",
            ".BMP",
        )

    def set_single_image(self, filepath: str):
        """Sets the model state to a single valid image."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Image not found: {filepath}")

        self.mode = "SINGLE"
        self.current_folder = None
        self.files = []
        self.active_image = {
            "filename": os.path.basename(filepath),
            "filepath": filepath,
        }

    def set_folder(self, folderpath: str):
        """Sets the model state to a folder and loads all valid images."""
        if not os.path.exists(folderpath):
            raise NotADirectoryError(f"Folder not found: {folderpath}")

        self.mode = "FOLDER"
        self.current_folder = folderpath

        # Load files and filter by valid extensions
        all_files = os.listdir(folderpath)
        self.files = [f for f in all_files if f.lower().endswith(self.valid_extensions)]

        if self.files:
            first_file = self.files[0]
            self.active_image = {
                "filename": first_file,
                "filepath": os.path.join(folderpath, first_file),
            }
        else:
            self.active_image = None

    def set_active_image(self, filename: str):
        """Sets the active image from the currently loaded folder."""
        if self.mode != "FOLDER":
            raise ValueError("Cannot select file by name if not in FOLDER mode.")

        if filename not in self.files:
            raise FileNotFoundError(f"File {filename} not found in loaded files.")

        folder = self.current_folder
        if folder is None:
            raise ValueError("Current folder is not set.")

        self.active_image = {
            "filename": filename,
            "filepath": os.path.join(folder, filename),
        }

    def clear(self):
        """Clears the session state."""
        self.mode = "EMPTY"
        self.current_folder = None
        self.active_image = None
        self.files = []

    def get_file_size_formatted(self, filepath: str) -> str:
        """Returns format e.g. '1.50 MB' or '500 KB' for a given file without using Qt."""
        if not filepath or not os.path.exists(filepath):
            return "-"

        file_size_bytes = os.path.getsize(filepath)
        if file_size_bytes > 1024 * 1024:
            return f"{file_size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{file_size_bytes / 1024:.0f} KB"

    def _extract_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract image metadata using OpenCV."""
        try:
            img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
            if img is None:
                return {}

            height, width = img.shape[:2]
            channels = 1 if len(img.shape) == 2 else img.shape[2]
            bit_depth = img.dtype

            channel_map = {1: "1 (Grayscale)", 3: "3 (RGB)", 4: "4 (RGBA)"}
            bit_map = {"uint8": "8-bit", "uint16": "16-bit"}

            return {
                "dimensions": f"{width} x {height}",
                "bit_depth": bit_map.get(str(bit_depth), str(bit_depth)),
                "channels": channel_map.get(channels, f"{channels}"),
                "file_size": self.get_file_size_formatted(filepath),
            }
        except Exception:
            return {}

    def load_metadata(self) -> Dict[str, Any]:
        """Load and store metadata for the active image."""
        if self.active_image is None or self.active_image.get("filepath") is None:
            return {}

        filepath = self.active_image["filepath"]
        metadata = self._extract_metadata(filepath)
        self.active_image.update(metadata)
        return metadata

    def set_processing_result(
        self,
        confluency: Optional[float] = None,
        mask_path: Optional[str] = None,
        total_cells: Optional[int] = None,
    ):
        """Store processing results for the active image."""
        if self.active_image is None:
            return

        self.active_image["confluencyResult"] = {
            "percentage": confluency,
            "totalCells": total_cells,
            "maskPath": mask_path,
            "maskVisible": False,
        }
        self.status = "processed"

    def clear_processing_result(self):
        """Clear processing results for the active image."""
        if self.active_image is None:
            return

        if "confluencyResult" in self.active_image:
            del self.active_image["confluencyResult"]
        self.status = "raw"

    def get_status(self) -> str:
        """Get the current status."""
        return self.status
