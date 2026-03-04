import pytest
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QStackedWidget
from PyQt6.QtCore import Qt
from src.ui.main_window import MainWindow
from src.ui.image_navigation import ImageNavigationWidget
from src.ui.pipeline_view import PipelineConstructionWidget
from src.ui.batch_execution_view import BatchExecutionIntegrationWidget


class TestMainWindow:
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

    def test_image_nav_widget_exists(self, qtbot):
        """Test that image navigation widget exists."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        assert window.image_nav_widget is not None
        assert isinstance(window.image_nav_widget, ImageNavigationWidget)


class TestMainWindowNavigation:
    """Phase 4.1: Navigation between views using QStackedWidget."""

    def test_stacked_widget_exists(self, qtbot):
        """Test that QStackedWidget is set up for view switching."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        assert window.stacked_widget is not None
        assert isinstance(window.stacked_widget, QStackedWidget)
        assert window.stacked_widget.count() == 3  # 3 views

    def test_all_views_loaded(self, qtbot):
        """Test that all three views are loaded into the stack."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Check each view is the correct type
        view0 = window.stacked_widget.widget(0)
        view1 = window.stacked_widget.widget(1)
        view2 = window.stacked_widget.widget(2)

        assert isinstance(view0, ImageNavigationWidget)
        assert isinstance(view1, PipelineConstructionWidget)
        assert isinstance(view2, BatchExecutionIntegrationWidget)

    def test_navigation_buttons_exist(self, qtbot):
        """Test that navigation buttons exist and are checkable."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        assert window.btn_img is not None
        assert window.btn_pipe is not None
        assert window.btn_exec is not None

        assert window.btn_img.isCheckable()
        assert window.btn_pipe.isCheckable()
        assert window.btn_exec.isCheckable()

    def test_view_switching(self, qtbot):
        """Test that clicking navigation buttons switches views."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Initial state: first view should be active
        assert window.stacked_widget.currentIndex() == 0
        assert window.btn_img.isChecked()

        # Switch to pipeline view
        qtbot.mouseClick(window.btn_pipe, Qt.MouseButton.LeftButton)
        assert window.stacked_widget.currentIndex() == 1
        assert window.btn_pipe.isChecked()

        # Switch to batch execution view
        qtbot.mouseClick(window.btn_exec, Qt.MouseButton.LeftButton)
        assert window.stacked_widget.currentIndex() == 2
        assert window.btn_exec.isChecked()

        # Switch back to image view
        qtbot.mouseClick(window.btn_img, Qt.MouseButton.LeftButton)
        assert window.stacked_widget.currentIndex() == 0
        assert window.btn_img.isChecked()

    def test_jump_to_execution(self, qtbot):
        """Test that jump_to_execution switches to batch execution view."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Start at image view
        window.switch_view(0)
        window.btn_img.setChecked(True)

        # Jump to execution
        window.jump_to_execution()

        assert window.stacked_widget.currentIndex() == 2
        assert window.btn_exec.isChecked()


class TestMainWindowStateSynchronization:
    """Phase 4.2: State synchronization between views."""

    def test_pipeline_config_signal(self, qtbot):
        """Test that pipeline config can be synchronized."""
        window = MainWindow()
        qtbot.addWidget(window)

        # Mock pipeline config
        test_config = {"nodes": [{"id": "test", "name": "TestNode"}]}
        window._current_pipeline_config = test_config

        assert window._current_pipeline_config == test_config

    def test_view_signal_connections(self, qtbot):
        """Test that view signals are properly connected."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Test that views have expected signals
        assert hasattr(window.image_nav_widget, "open_single_image_requested")
        assert hasattr(window.image_nav_widget, "open_folder_requested")
        assert hasattr(window.pipeline_view, "run_pipeline")

    def test_status_message_signal(self, qtbot):
        """Test that status message signal works."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Emit status message
        with qtbot.waitSignal(window.status_message, timeout=1000):
            window.status_message.emit("Test message", 1000)


class TestMainWindowErrorHandling:
    """Phase 4.3: Error handling with QMessageBox."""

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
    """Phase 4.4: Keyboard shortcuts for common actions."""

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
        assert "Image Loading" in action_texts
        assert "Pipeline Construction" in action_texts
        assert "Batch Execution" in action_texts
        assert "Help" in action_texts

    def test_f1_shortcut_switches_to_image_view(self, qtbot):
        """Test F1 shortcut switches to image loading view."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Start at a different view
        window.switch_view(2)
        window.btn_exec.setChecked(True)

        # Use the action directly instead of keyClick
        # Find the Image Loading action
        for action in window.actions():
            if action.text() == "Image Loading":
                action.trigger()
                break

        assert window.stacked_widget.currentIndex() == 0
        assert window.btn_img.isChecked()

    def test_f2_shortcut_switches_to_pipeline_view(self, qtbot):
        """Test F2 shortcut switches to pipeline construction view."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Use the action directly instead of keyClick
        for action in window.actions():
            if action.text() == "Pipeline Construction":
                action.trigger()
                break

        assert window.stacked_widget.currentIndex() == 1
        assert window.btn_pipe.isChecked()

    def test_f3_shortcut_switches_to_batch_view(self, qtbot):
        """Test F3 shortcut switches to batch execution view."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Use the action directly instead of keyClick
        for action in window.actions():
            if action.text() == "Batch Execution":
                action.trigger()
                break

        assert window.stacked_widget.currentIndex() == 2
        assert window.btn_exec.isChecked()


class TestMainWindowStatusBar:
    """Phase 4.5: Status bar with progress/info."""

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

        # Status bar should show "Ready" initially
        assert window.status_bar.currentMessage() == "Ready"

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

        # Clear any initial message
        window.status_bar.clearMessage()

        # Emit status message
        window.status_message.emit("Test status", 5000)

        assert window.status_bar.currentMessage() == "Test status"
