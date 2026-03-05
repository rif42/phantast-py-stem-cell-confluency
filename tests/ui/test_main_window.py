import pytest
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow
from src.ui.unified_main_widget import UnifiedMainWidget
from src.ui.pipeline_stack_widget import PipelineStackWidget
from src.ui.node_property_editor import NodePropertyEditor
from src.ui.image_canvas import ImageCanvas


class TestMainWindow:
    """Tests for unified MainWindow."""

    def test_window_creation(self, qtbot):
        """Test that MainWindow can be created."""
        window = MainWindow()
        qtbot.addWidget(window)

        assert window.windowTitle() == "Phantast Lab"
        assert window.isVisible() is False  # Not shown yet

    def test_header_exists(self, qtbot):
        """Test that header is properly set up."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Find header by object name
        header = window.findChild(QWidget, "AppHeader")
        assert header is not None
        assert header.height() == 56

    def test_unified_widget_exists(self, qtbot):
        """Test that unified main widget exists."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        assert window.unified_widget is not None
        assert isinstance(window.unified_widget, UnifiedMainWidget)

    def test_controller_exists(self, qtbot):
        """Test that controller is initialized."""
        window = MainWindow()
        qtbot.addWidget(window)

        assert window.controller is not None

    def test_pipeline_widget_exists(self, qtbot):
        """Test that pipeline widget exists."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        assert window.pipeline_widget is not None
        assert isinstance(window.pipeline_widget, PipelineStackWidget)

    def test_property_editor_exists(self, qtbot):
        """Test that node property editor exists."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        assert window.property_editor is not None
        assert isinstance(window.property_editor, NodePropertyEditor)


class TestMainWindowUnifiedInterface:
    """Tests for unified interface components."""

    def test_canvas_exists(self, qtbot):
        """Test that image canvas exists."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        canvas = window.unified_widget.canvas
        assert canvas is not None
        assert isinstance(canvas, ImageCanvas)

    def test_left_panel_adapts_to_phase(self, qtbot):
        """Test that left panel adapts to workflow phase."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Initially hidden (EMPTY phase)
        assert not window.unified_widget.left_panel_container.isVisible()

    def test_right_panel_shows_properties(self, qtbot):
        """Test that right panel shows properties panel."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Should show properties panel initially
        assert window.unified_widget.right_panel_container.isVisible()


class TestMainWindowErrorHandling:
    """Tests for error handling dialogs."""

    def test_error_dialog_method_exists(self, qtbot):
        """Test that error dialog method exists."""
        window = MainWindow()
        qtbot.addWidget(window)

        assert hasattr(window, "show_error_dialog")
        assert callable(window.show_error_dialog)

    def test_warning_dialog_method_exists(self, qtbot):
        """Test that warning dialog method exists."""
        window = MainWindow()
        qtbot.addWidget(window)

        assert hasattr(window, "show_warning_dialog")
        assert callable(window.show_warning_dialog)

    def test_info_dialog_method_exists(self, qtbot):
        """Test that info dialog method exists."""
        window = MainWindow()
        qtbot.addWidget(window)

        assert hasattr(window, "show_info_dialog")
        assert callable(window.show_info_dialog)


class TestMainWindowKeyboardShortcuts:
    """Tests for keyboard shortcuts."""

    def test_shortcut_actions_exist(self, qtbot):
        """Test that keyboard shortcut actions are set up."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Check that actions are added to the window
        actions = window.actions()
        action_texts = [a.text() for a in actions]

        assert "Open Image" in action_texts
        assert "Open Folder" in action_texts
        assert "Save" in action_texts
        assert "Quit" in action_texts
        assert "Help" in action_texts


class TestMainWindowStatusBar:
    """Tests for status bar."""

    def test_status_bar_exists(self, qtbot):
        """Test that status bar is set up."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        assert window.status_bar is not None
        assert window.statusBar() is not None

    def test_status_bar_shows_message(self, qtbot):
        """Test that status bar displays messages."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Status bar should show "Open an image to start" initially
        assert "Open an image" in window.status_bar.currentMessage()

    def test_progress_bar_exists(self, qtbot):
        """Test that progress bar widget exists."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        assert window.progress_bar is not None

    def test_progress_bar_visibility(self, qtbot):
        """Test that progress bar can be shown and hidden."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Initially hidden
        assert not window.progress_bar.isVisible()

        # Show progress
        window.show_progress(50)
        assert window.progress_bar.isVisible()
        assert window.progress_bar.value() == 50

        # Hide progress
        window.hide_progress()
        assert not window.progress_bar.isVisible()

    def test_status_message_signal_updates_bar(self, qtbot):
        """Test that status_message signal updates the status bar."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Emit status message
        window.status_message.emit("Test status", 5000)

        assert window.status_bar.currentMessage() == "Test status"
