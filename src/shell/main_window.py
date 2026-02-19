
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QDockWidget,
    QLabel,
    QToolBar,
    QStatusBar,
    QPushButton,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon

# Import Navigation Manager
# Assuming structure:
# src/
#   shell/
#     main_window.py
#     navigation.py

from .navigation import NavigationManager
from ..core.pipeline import ImagePipeline
from ..gui.image_viewer import ImageViewer
from ..gui.pipeline_editor import PipelineEditorWidget, StepConfigWidget
import cv2
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.resize(1280, 800)

        # Core Pipeline
        self.pipeline = ImagePipeline()
        self.current_image = None # The original loaded image
        self.processed_image = None # The result of processing

        # Apply Theme (Dark Mode based on Design Tokens)
        self.apply_stylesheet()

        # Central Widget (Stack for different modes)
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        # Setup Dock Widgets
        self.setup_docks()

        # Setup Navigation Manager
        self.nav_manager = NavigationManager(
            self.central_stack,
            {"Pipeline": self.pipeline_dock, "Settings": self.settings_dock},
        )

        # initialize Modes
        self.setup_modes()

        # Setup Toolbar
        self.setup_toolbar()

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def apply_stylesheet(self):
        """Applies the application-wide QSS stylesheet."""
        # Design Tokens
        # Primary: #009B77 (Teal)
        # Secondary: #D4AF37 (Gold)
        # Background: #333333 (Charcoal)
        # Text: #EEEEEE
        
        style = """
        QMainWindow {
            background-color: #333333;
            color: #EEEEEE;
        }
        QWidget {
            background-color: #333333;
            color: #EEEEEE;
            font-family: "Segoe UI";
            font-size: 14px;
        }
        QDockWidget {
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }
        QDockWidget::title {
            background: #222222;
            padding-left: 10px;
            padding-top: 4px;
            padding-bottom: 4px;
        }
        QToolBar {
            background: #222222;
            padding: 5px;
            border-bottom: 1px solid #444444;
        }
        QStatusBar {
            background: #222222;
            color: #AAAAAA;
        }
        QPushButton {
            background-color: #444444;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px 12px;
            color: #EEEEEE;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QPushButton:pressed {
            background-color: #009B77; /* Primary Color */
        }
        /* Specialized styling for primary buttons if we have a class for them */
        .primary-button {
             background-color: #009B77;
             border: 1px solid #007A5E;
        }
        QListWidget {
            background-color: #2A2A2A;
            border: 1px solid #444444;
        }
        QListWidget::item:selected {
            background-color: #009B77;
            color: white;
        }
        QComboBox, QSpinBox, QDoubleSpinBox {
            background-color: #444444;
            border: 1px solid #555555;
            padding: 4px;
            color: #EEEEEE;
        }
        """
        self.setStyleSheet(style)

    def setup_docks(self):
        """Initializes the dock widgets for the layout."""
        # Top-Left: Pipeline Editor Dock
        self.pipeline_dock = QDockWidget("Pipeline Steps", self)
        self.pipeline_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.pipeline_editor = PipelineEditorWidget(self.pipeline)
        self.pipeline_editor.step_selected.connect(self.on_step_selected)
        self.pipeline_editor.pipeline_changed.connect(self.run_pipeline)
        
        self.pipeline_dock.setWidget(self.pipeline_editor)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pipeline_dock)

        # Top-Right: Settings/Properties Dock
        self.settings_dock = QDockWidget("Properties", self)
        self.settings_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        self.step_config = StepConfigWidget()
        self.step_config.param_changed.connect(self.run_pipeline)

        self.settings_dock.setWidget(self.step_config)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.settings_dock)

    def setup_modes(self):
        """ initializes the application modes (Image Analysis vs Batch)."""
        
        # Mode 1: Image Analysis Workspace
        self.image_viewer = ImageViewer()
        
        self.nav_manager.register_mode("analysis", self.image_viewer, ["Pipeline", "Settings"])
        
        # Mode 2: Batch Workflow
        batch_widget = QLabel("Batch Processing Workflow (Coming Soon)")
        batch_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        batch_widget.setStyleSheet("font-size: 18px; color: #888888;")
        
        self.nav_manager.register_mode("batch", batch_widget, ["Pipeline"]) # Maybe hide settings in batch mode?

        # Set default mode
        self.nav_manager.switch_to("analysis")

    def setup_toolbar(self):
        """Initializes the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # File Actions
        open_action = QAction("Open Image", self)
        open_action.setStatusTip("Open a new image for analysis")
        open_action.triggered.connect(self.open_image)
        toolbar.addAction(open_action)

        save_action = QAction("Save Pipeline", self)
        save_action.setStatusTip("Save current processing pipeline")
        save_action.triggered.connect(lambda: print("Save Pipeline triggered"))
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()

        # Mode Switching (For demonstration)
        analysis_mode_action = QAction("Analysis Mode", self)
        analysis_mode_action.triggered.connect(lambda: self.nav_manager.switch_to("analysis"))
        toolbar.addAction(analysis_mode_action)
        
        batch_mode_action = QAction("Batch Mode", self)
        batch_mode_action.triggered.connect(lambda: self.nav_manager.switch_to("batch"))
        toolbar.addAction(batch_mode_action)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        if file_path:
            image = cv2.imread(file_path)
            if image is not None:
                self.current_image = image
                self.run_pipeline()
                self.status_bar.showMessage(f"Loaded: {file_path}")
            else:
                QMessageBox.critical(self, "Error", "Could not load image.")

    def on_step_selected(self, step):
        self.step_config.set_step(step)

    def run_pipeline(self):
        if self.current_image is None:
            return
        
        try:
            processed = self.pipeline.execute(self.current_image)
            self.processed_image = processed
            self.image_viewer.set_image(processed)
            
            # Update status with metadata if any
            meta = self.pipeline.get_metadata()
            if "phantast_confluency" in meta:
                conf = meta["phantast_confluency"]
                self.status_bar.showMessage(f"Confluency: {conf:.2f}%")
                
        except Exception as e:
            print(f"Pipeline Execution Error: {e}")
            self.status_bar.showMessage(f"Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

