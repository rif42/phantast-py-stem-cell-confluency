import pytest
import os
import tempfile
import numpy as np
import cv2
from src.models.image_model import ImageSessionModel


class TestImageSessionModel:
    def test_set_single_image(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            # Create a dummy image
            img = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.imwrite(f.name, img)
            temp_path = f.name

        try:
            model = ImageSessionModel()
            model.set_single_image(temp_path)
            assert model.mode == "SINGLE"
            assert model.active_image is not None
            assert model.active_image["filename"] == os.path.basename(temp_path)
        finally:
            os.unlink(temp_path)

    def test_set_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy images
            for i in range(3):
                img = np.zeros((100, 100, 3), dtype=np.uint8)
                cv2.imwrite(os.path.join(tmpdir, f"test{i}.png"), img)

            model = ImageSessionModel()
            model.set_folder(tmpdir)
            assert model.mode == "FOLDER"
            assert len(model.files) == 3

    def test_metadata_extraction(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = np.zeros((512, 256, 3), dtype=np.uint8)
            cv2.imwrite(f.name, img)
            temp_path = f.name

        try:
            model = ImageSessionModel()
            model.set_single_image(temp_path)
            metadata = model.load_metadata()
            assert metadata["dimensions"] == "256 x 512"
            assert metadata["bit_depth"] == "8-bit"
            assert metadata["channels"] == "3 (RGB)"
        finally:
            os.unlink(temp_path)

    def test_processing_result(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.imwrite(f.name, img)
            temp_path = f.name

        try:
            model = ImageSessionModel()
            model.set_single_image(temp_path)
            model.set_processing_result(
                confluency=85.5, mask_path="mask.png", total_cells=150
            )

            assert model.status == "processed"
            assert model.active_image["confluencyResult"]["percentage"] == 85.5
            assert model.active_image["confluencyResult"]["totalCells"] == 150
        finally:
            os.unlink(temp_path)

    def test_clear_processing_result(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.imwrite(f.name, img)
            temp_path = f.name

        try:
            model = ImageSessionModel()
            model.set_single_image(temp_path)
            model.set_processing_result(confluency=85.5)
            model.clear_processing_result()

            assert model.status == "raw"
            assert "confluencyResult" not in model.active_image
        finally:
            os.unlink(temp_path)
