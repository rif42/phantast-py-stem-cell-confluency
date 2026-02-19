import sys
import os
import json
from PySide6.QtWidgets import QApplication
from views.ImageAnalysisWorkspace import ImageAnalysisWorkspace

# Load sample data
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../product/sections/image-analysis-workspace/data.json'))
try:
    with open(data_path, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Warning: Data file not found at {data_path}. Using empty data.")
    data = {}

app = QApplication(sys.argv)
app.setStyle("Fusion")

# Apply global dark theme to match design
app.setStyleSheet("""
    QWidget {
        background-color: #333;
        color: #EEE;
        font-family: 'Segoe UI';
    }
    QScrollBar:vertical {
        border: none;
        background: #2A2A2A;
        width: 10px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: #555;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
""")

window = ImageAnalysisWorkspace(data)
window.resize(1280, 800)
window.show()

sys.exit(app.exec())
