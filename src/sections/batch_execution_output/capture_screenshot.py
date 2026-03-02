import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from PyQt6.QtWidgets import QApplication
from src.sections.batch_execution_output.views.batch_execution_view import BatchExecutionIntegrationWidget

def main():
    app = QApplication(sys.argv)
    
    # Load sample data
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../product/sections/batch-execution-output/data.json"))
    
    window = BatchExecutionIntegrationWidget(data_path)
    window.resize(1300, 800)
    window.show()
    
    app.processEvents()
    
    pixmap = window.grab()
    
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../product/sections/batch-execution-output/batch_execution_view.png"))
    pixmap.save(out_path)
    print(f"Screenshot saved to {out_path}")
    
    sys.exit()

if __name__ == "__main__":
    main()
