"""Tests for folder explorer functionality in UnifiedRightPanel."""

import pytest
from PyQt6.QtWidgets import QApplication, QListWidget
from PyQt6.QtCore import Qt

from src.ui.unified_right_panel import UnifiedRightPanel


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def panel(qtbot, qapp):
    """Create a UnifiedRightPanel instance for testing."""
    widget = UnifiedRightPanel()
    qtbot.addWidget(widget)
    widget.show()
    return widget


class TestFolderExplorerWidget:
    """Test folder explorer widget creation and basic functionality."""

    def test_file_list_widget_exists(self, panel):
        """Verify QListWidget is created and accessible."""
        assert hasattr(panel, "file_list")
        assert isinstance(panel.file_list, QListWidget)
        assert panel.file_list.objectName() == "fileList"

    def test_file_list_has_parent(self, panel):
        """Verify file_list has proper parent to prevent window spawning."""
        assert panel.file_list.parent() is not None
        assert panel.file_list.parent() == panel.metadata_page

    def test_refresh_button_exists(self, panel):
        """Verify refresh button is created."""
        assert hasattr(panel, "refresh_btn")
        assert panel.refresh_btn.objectName() == "refreshBtn"

    def test_empty_label_exists(self, panel):
        """Verify empty state label is created."""
        assert hasattr(panel, "empty_label")
        assert panel.empty_label.objectName() == "emptyLabel"
        assert not panel.empty_label.isVisible()  # Hidden by default

    def test_signals_exist(self, panel):
        """Verify required signals are defined."""
        assert hasattr(panel, "file_selected")
        assert hasattr(panel, "refresh_requested")


class TestUpdateFileList:
    """Test file list population and updates."""

    def test_update_file_list_populates(self, panel):
        """Verify list populates with file paths."""
        test_files = [
            "/path/to/image1.png",
            "/path/to/image2.jpg",
            "/path/to/image3.tiff",
        ]

        panel.update_file_list(test_files)

        assert panel.file_list.count() == 3
        assert panel.file_list.item(0).text() == "image1.png"
        assert panel.file_list.item(1).text() == "image2.jpg"
        assert panel.file_list.item(2).text() == "image3.tiff"

    def test_update_file_list_selects_first_item(self, panel):
        """Verify first item is selected after update."""
        test_files = ["/path/to/image1.png", "/path/to/image2.png"]

        panel.update_file_list(test_files)

        assert panel.file_list.currentRow() == 0

    def test_empty_folder_shows_message(self, panel):
        """Verify empty state shows when no files."""
        panel.update_file_list([])

        assert not panel.file_list.isVisible()
        assert panel.empty_label.isVisible()
        assert panel.empty_label.text() == "No images found"

    def test_non_empty_folder_hides_empty_message(self, panel):
        """Verify empty state hidden when files exist."""
        panel.update_file_list(["/path/to/image.png"])

        assert panel.file_list.isVisible()
        assert not panel.empty_label.isVisible()

    def test_refresh_button_disabled_when_empty(self, panel):
        """Verify refresh button disabled when no files."""
        panel.update_file_list([])
        assert not panel.refresh_btn.isEnabled()

    def test_refresh_button_enabled_with_files(self, panel):
        """Verify refresh button enabled when files exist."""
        panel.update_file_list(["/path/to/image.png"])
        assert panel.refresh_btn.isEnabled()


class TestFileSelection:
    """Test file selection and double-click behavior."""

    def test_double_click_emits_signal(self, panel, qtbot):
        """Verify double-click emits file_selected signal with filename."""
        test_files = ["/path/to/image1.png", "/path/to/image2.jpg"]
        panel.update_file_list(test_files)

        # Listen for signal
        with qtbot.waitSignal(panel.file_selected, timeout=1000) as blocker:
            # Double-click second item
            item = panel.file_list.item(1)
            panel.file_list.itemDoubleClicked.emit(item)

        assert blocker.args[0] == "image2.jpg"

    def test_double_click_first_item(self, panel, qtbot):
        """Verify double-click on first item works."""
        test_files = ["/path/to/image1.png"]
        panel.update_file_list(test_files)

        with qtbot.waitSignal(panel.file_selected, timeout=1000) as blocker:
            item = panel.file_list.item(0)
            panel.file_list.itemDoubleClicked.emit(item)

        assert blocker.args[0] == "image1.png"


class TestRefresh:
    """Test refresh button functionality."""

    def test_refresh_button_emits_signal(self, panel, qtbot):
        """Verify refresh button click emits refresh_requested signal."""
        panel.update_file_list(["/path/to/image.png"])

        with qtbot.waitSignal(panel.refresh_requested, timeout=1000):
            panel.refresh_btn.click()


class TestPerformanceSettings:
    """Test QListWidget performance optimizations."""

    def test_uniform_item_sizes_enabled(self, panel):
        """Verify setUniformItemSizes is True for performance."""
        assert panel.file_list.uniformItemSizes()

    def test_batch_mode_enabled(self, panel):
        """Verify batch mode is enabled for performance."""
        from PyQt6.QtWidgets import QListWidget

        assert panel.file_list.layoutMode() == QListWidget.LayoutMode.Batched

    def test_batch_size_set(self, panel):
        """Verify batch size is set to 100."""
        assert panel.file_list.batchSize() == 100
