
import sys
import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog, QSpinBox, QDoubleSpinBox, 
    QMessageBox, QFrame
)
from PyQt6.QtGui import QPixmap, QImage, QFont
from PyQt6.QtCore import Qt

# Import PHANTAST integration
# Calculate the root directory (2 levels up from src/gui)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

try:
    from phantast_confluency_corrected import process_phantast
except ImportError as e:
    print(f"Error importing PHANTAST: {e}")
    process_phantast = None


class SimplePhantastApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Phantast Lab")
        self.resize(1000, 700)
        
        # State
        self.current_image_path = None
        self.original_image = None
        self.processed_overlay = None # The greenish overlay
        self.confluency_score = 0.0
        self.current_mask = None # Boolean mask
        
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # --- Top: File Selection ---
        file_layout = QHBoxLayout()
        
        self.path_label = QLabel("No image selected")
        self.path_label.setStyleSheet("border: 1px solid #444; padding: 5px; color: #BBB; background: #222;")
        file_layout.addWidget(self.path_label, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_image)
        file_layout.addWidget(browse_btn)
        
        main_layout.addLayout(file_layout)

        # --- Middle: Image Preview ---
        # Split view: Original | Processed
        preview_layout = QHBoxLayout()
        
        # Original
        self.original_view = QLabel()
        self.original_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_view.setStyleSheet("background: #111; border: 1px solid #333;")
        self.original_view.setMinimumSize(400, 400)
        
        # Result
        self.result_view = QLabel()
        self.result_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_view.setStyleSheet("background: #111; border: 1px solid #333;")
        self.result_view.setMinimumSize(400, 400)
        
        preview_layout.addWidget(self.original_view, 1)
        preview_layout.addWidget(self.result_view, 1)
        
        main_layout.addLayout(preview_layout, 1)

        # --- Bottom: Controls ---
        control_frame = QFrame()
        control_frame.setStyleSheet("background: #2A2A2A; border-radius: 5px; padding: 10px;")
        control_layout = QHBoxLayout(control_frame)
        
        # Parameters
        param_layout = QHBoxLayout()
        
        # Sigma
        param_layout.addWidget(QLabel("Sigma:"))
        self.sigma_spin = QDoubleSpinBox()
        self.sigma_spin.setRange(0.1, 20.0)
        self.sigma_spin.setValue(1.5) # Default from batch script
        self.sigma_spin.setSingleStep(0.1)
        param_layout.addWidget(self.sigma_spin)
        
        # Epsilon
        param_layout.addWidget(QLabel("Epsilon:"))
        self.epsilon_spin = QDoubleSpinBox()
        self.epsilon_spin.setRange(0.001, 1.0)
        self.epsilon_spin.setValue(0.025) # Default from batch script
        self.epsilon_spin.setSingleStep(0.005)
        self.epsilon_spin.setDecimals(3)
        param_layout.addWidget(self.epsilon_spin)
        
        control_layout.addLayout(param_layout)
        
        control_layout.addStretch()
        
        # Result Label
        self.confluency_label = QLabel("Confluency: --%")
        self.confluency_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #009B77; margin-right: 20px;")
        control_layout.addWidget(self.confluency_label)
        
        # Buttons
        self.run_btn = QPushButton("Run Phantast")
        self.run_btn.setStyleSheet("""
            QPushButton { background-color: #009B77; color: white; padding: 8px 16px; border: none; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #008060; }
            QPushButton:disabled { background-color: #444; color: #888; }
        """)
        self.run_btn.clicked.connect(self.run_processing)
        self.run_btn.setEnabled(False)
        control_layout.addWidget(self.run_btn)
        
        self.save_btn = QPushButton("Save Output")
        self.save_btn.clicked.connect(self.save_output)
        self.save_btn.setEnabled(False)
        control_layout.addWidget(self.save_btn)
        
        main_layout.addWidget(control_frame)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #333; color: #EEE; font-family: Segoe UI, sans-serif; font-size: 14px; }
            QSpinBox, QDoubleSpinBox { background: #444; border: 1px solid #555; padding: 4px; color: white; }
            QPushButton { background: #555; border: 1px solid #666; padding: 6px 12px; border-radius: 4px; }
            QPushButton:hover { background: #666; }
        """)

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.jpg *.png *.tif *.bmp)")
        if path:
            self.load_image(path)

    def load_image(self, path):
        self.current_image_path = path
        self.path_label.setText(path)
        
        image = cv2.imread(path)
        if image is None:
            QMessageBox.critical(self, "Error", "Could not load image.")
            return

        self.original_image = image
        # Display Original
        self.display_image(image, self.original_view)
        
        # Reset result
        self.result_view.clear()
        self.processed_overlay = None
        self.confluency_label.setText("Confluency: --%")
        
        self.run_btn.setEnabled(True)
        self.save_btn.setEnabled(False)

    def display_image(self, cv_img, label_widget):
        """Scale and display cv2 image on a QLabel."""
        if cv_img is None: return
        
        # Convert to RGB
        if len(cv_img.shape) == 3:
            rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        else:
            rgb = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
            
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        # Scale to fit label
        scaled = pixmap.scaled(label_widget.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        label_widget.setPixmap(scaled)

    def run_processing(self):
        if self.original_image is None: return
        
        sigma = self.sigma_spin.value()
        epsilon = self.epsilon_spin.value()
        
        # Determine if we should maintain original color or use grayscale
        # Phantast works on grayscale.
        # Process directly (phantast_confluency_corrected handles conversion internally)
        
        try:
            # We don't need to specify output paths here, as we just want the return values
            # However, `process_phantast` prints a lot.
            
            confluency, mask = process_phantast(
                self.original_image,
                sigma=sigma,
                epsilon=epsilon,
                output_mask_path=None,
                output_overlay_path=None
            )
            
            self.confluency_score = confluency
            self.current_mask = mask
            self.confluency_label.setText(f"Confluency: {confluency:.2f}%")
            
            # Create Overlay Visualization
            self.processed_overlay = self.create_visual_overlay(self.original_image, mask)
            self.display_image(self.processed_overlay, self.result_view)
            
            self.save_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Processing failed: {str(e)}")
            print(e)

    def create_visual_overlay(self, original, mask):
        """Create BGR overlay similar to batch script."""
        if len(original.shape) == 2:
            base = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
        else:
            base = original.copy()
            
        overlay = base.copy()
        # Green mask
        overlay[mask] = [0, 255, 0]
        
        # AddWeighted
        alpha = 0.4
        result = cv2.addWeighted(overlay, alpha, base, 1 - alpha, 0)
        return result

    def save_output(self):
        if self.current_image_path is None or self.processed_overlay is None: return
        
        try:
            input_dir = os.path.dirname(self.current_image_path)
            filename = os.path.splitext(os.path.basename(self.current_image_path))[0]
            
            # 1. Save Overlay
            overlay_path = os.path.join(input_dir, f"{filename}_overlay.jpg")
            cv2.imwrite(overlay_path, self.processed_overlay)
            
            # 2. Save Comparison (Original | Result)
            # Create composition
            if len(self.original_image.shape) == 2:
                orig_bgr = cv2.cvtColor(self.original_image, cv2.COLOR_GRAY2BGR)
            else:
                orig_bgr = self.original_image
                
            # Resize result to match original if needed (should match)
            comparison = np.hstack([orig_bgr, self.processed_overlay])
            
            # Add separator line
            cv2.line(comparison, (orig_bgr.shape[1], 0), (orig_bgr.shape[1], orig_bgr.shape[0]), (0, 0, 0), 2)
            
            comparison_path = os.path.join(input_dir, f"{filename}_comparison.jpg")
            cv2.imwrite(comparison_path, comparison)
            
            QMessageBox.information(self, "Saved", f"Files saved:\n{overlay_path}\n{comparison_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save files: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimplePhantastApp()
    window.show()
    sys.exit(app.exec())
