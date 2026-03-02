import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QLabel, QPushButton, QFrame, QSizePolicy, QButtonGroup
)
from PyQt6.QtCore import Qt

# Import our custom components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from src.sections.image_navigation_inspection.views.image_navigation import ImageNavigationWidget
from src.sections.pipeline_construction.views.pipeline_view import PipelineConstructionWidget
from src.sections.batch_execution_output.views.batch_execution_view import BatchExecutionIntegrationWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phantast Lab")
        self.resize(1300, 850)

        self.apply_stylesheet()

        # Core Container
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        self.setup_header()

        # Navigation Stack
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        self.load_views()

    def apply_stylesheet(self):
        style = """
        QMainWindow, QWidget {
            background-color: #121415;
            color: #E8EAED;
            font-family: "Inter", "Segoe UI", sans-serif;
            font-size: 13px;
        }
        
        /* HEADER */
        #AppHeader {
            background-color: #121415;
            border-bottom: 1px solid #2D3336;
        }

        /* BUTTONS */
        #navBtn {
            border: none;
            color: #9AA0A6;
            font-size: 13px;
            font-weight: 500;
            padding: 8px 16px;
            background-color: transparent;
        }
        #navBtn:hover {
            color: #E8EAED;
        }
        #navBtn:checked {
            color: #00B884;
            font-weight: bold;
            border-bottom: 2px solid #00B884;
        }
        """
        self.setStyleSheet(style)

    def setup_header(self):
        header = QFrame()
        header.setObjectName("AppHeader")
        header.setFixedHeight(56)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)
        
        # Left side
        logo = QLabel("🔬")
        logo.setStyleSheet("font-size: 20px; color: #00B884;")
        
        title = QLabel("Phantast Lab")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #E8EAED;")
        
        layout.addWidget(logo)
        layout.addWidget(title)
        
        # Navigation Tabs
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(32, 0, 0, 0)
        self.nav_group = QButtonGroup(self)
        
        self.btn_img = QPushButton("Image Loading")
        self.btn_img.setObjectName("navBtn")
        self.btn_img.setCheckable(True)
        self.btn_img.setChecked(True)
        self.nav_group.addButton(self.btn_img, 0)
        
        self.btn_pipe = QPushButton("Pipeline Construction")
        self.btn_pipe.setObjectName("navBtn")
        self.btn_pipe.setCheckable(True)
        self.nav_group.addButton(self.btn_pipe, 1)
        
        self.btn_exec = QPushButton("Batch Execution")
        self.btn_exec.setObjectName("navBtn")
        self.btn_exec.setCheckable(True)
        self.nav_group.addButton(self.btn_exec, 2)
        
        self.nav_group.idClicked.connect(self.switch_view)
        
        nav_layout.addWidget(self.btn_img)
        nav_layout.addWidget(self.btn_pipe)
        nav_layout.addWidget(self.btn_exec)
        
        layout.addLayout(nav_layout)
        layout.addStretch()
        
        # Right side -> Avatar
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet("background-color: #E8A317; border-radius: 16px;")
        layout.addWidget(avatar)
        
        self.main_layout.addWidget(header)

    def load_views(self):
        # Base paths for data
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../product/sections/"))
        
        # 1. Image Navigation View
        data_path_img = os.path.join(base_dir, "image-navigation-inspection/data.json")
        self.view_img = ImageNavigationWidget(data_path_img)
        self.stacked_widget.addWidget(self.view_img)
        
        # 2. Pipeline Construction View
        data_path_pipe = os.path.join(base_dir, "pipeline-construction/data.json")
        self.view_pipe = PipelineConstructionWidget(data_path_pipe)
        # Connect the Run button to switch to Execution view
        self.view_pipe.run_pipeline.connect(self.jump_to_execution)
        self.stacked_widget.addWidget(self.view_pipe)
        
        # 3. Batch Execution View
        data_path_exec = os.path.join(base_dir, "batch-execution-output/data.json")
        self.view_exec = BatchExecutionIntegrationWidget(data_path_exec)
        self.stacked_widget.addWidget(self.view_exec)

    def switch_view(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
    def jump_to_execution(self):
        # Check the nav button visually
        self.btn_exec.setChecked(True)
        # Switch the stack
        self.switch_view(2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
