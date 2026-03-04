import pytest
from PyQt6.QtWidgets import QApplication, QWidget
from src.ui.main_window import MainWindow


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
        from src.ui.image_navigation import ImageNavigationWidget

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        assert window.image_nav_widget is not None
        assert isinstance(window.image_nav_widget, ImageNavigationWidget)
