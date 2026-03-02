import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from PyQt6.QtWidgets import QApplication
from src.sections.pipeline_construction.views.pipeline_view import PipelineConstructionWidget

# Load sample data
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../product/sections/pipeline-construction/data.json"))

app = QApplication(sys.argv)
window = PipelineConstructionWidget(data_path)
window.resize(1200, 800)
window.setWindowTitle("Pipeline Construction Preview")
window.show()

sys.exit(app.exec())
