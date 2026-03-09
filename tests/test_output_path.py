"""Tests for MainWindow output path generation utility."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.ui.main_window import MainWindow


def _window_without_init() -> MainWindow:
    """Build a MainWindow instance without invoking Qt-heavy __init__."""
    return MainWindow.__new__(MainWindow)


def test_generate_output_path_standard_filename(tmp_path):
    """Standard file gets _processed suffix and keeps extension."""
    input_path = tmp_path / "image.jpg"
    expected = tmp_path / "image_processed.jpg"

    output_path = MainWindow._generate_output_path(
        _window_without_init(), str(input_path)
    )

    assert output_path == str(expected.resolve())


def test_generate_output_path_already_processed_suffix(tmp_path):
    """Existing _processed suffix gets incremented to _processed_1."""
    input_path = tmp_path / "image_processed.jpg"
    expected = tmp_path / "image_processed_1.jpg"

    output_path = MainWindow._generate_output_path(
        _window_without_init(), str(input_path)
    )

    assert output_path == str(expected.resolve())


def test_generate_output_path_no_extension_defaults_to_png(tmp_path):
    """Files without extension default to .png output."""
    input_path = tmp_path / "image"
    expected = tmp_path / "image_processed.png"

    output_path = MainWindow._generate_output_path(
        _window_without_init(), str(input_path)
    )

    assert output_path == str(expected.resolve())


def test_generate_output_path_avoids_existing_processed_file(tmp_path):
    """If default processed path exists, use incremented suffix."""
    input_path = tmp_path / "image.jpg"
    existing_output = tmp_path / "image_processed.jpg"
    existing_output.write_bytes(b"processed")
    expected = tmp_path / "image_processed_1.jpg"

    output_path = MainWindow._generate_output_path(
        _window_without_init(), str(input_path)
    )

    assert output_path == str(expected.resolve())
