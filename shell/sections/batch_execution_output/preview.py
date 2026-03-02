import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from PyQt6.QtWidgets import QApplication
from src.sections.batch_execution_output.views.batch_execution_view import BatchExecutionIntegrationWidget

# Load sample data
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../product/sections/batch-execution-output/data.json"))

app = QApplication(sys.argv)
window = BatchExecutionIntegrationWidget(data_path)
window.resize(1300, 800)
window.show()

sys.exit(app.exec())
