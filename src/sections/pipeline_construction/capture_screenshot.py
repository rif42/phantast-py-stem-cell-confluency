import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from PyQt6.QtWidgets import QApplication
from src.sections.pipeline_construction.views.pipeline_view import PipelineConstructionWidget

# Ensure output directory exists
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../product/sections/pipeline-construction"))
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "pipeline_construction-design.png")

# Load sample data
data_path = os.path.join(output_dir, "data.json")

app = QApplication(sys.argv)
window = PipelineConstructionWidget(data_path)
window.resize(1200, 800)
window.show()

# Process events to ensure everything renders properly before capture
app.processEvents()

# Capture the widget
pixmap = window.grab()
pixmap.save(output_path)

print(f"Screenshot saved to {output_path}")

# Close application
window.close()
sys.exit()
