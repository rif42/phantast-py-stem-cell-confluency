import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QFrame, QSplitter, QSlider,
    QCheckBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsLineItem, QGraphicsRectItem, QGraphicsItem, QToolButton
)
from PySide6.QtCore import Qt, Signal, QRectF, QSize, QPointF
from PySide6.QtGui import QPixmap, QColor, QPainter, QPen, QBrush, QIcon, QFont, QAction

# ==============================================================================
# Helper Widgets
# ==============================================================================

class PipelineStepItem(QFrame):
    def __init__(self, step_data, is_active=False):
        super().__init__()
        self.step_id = step_data['id']
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon placeholder (circle)
        icon = QLabel()
        icon.setFixedSize(24, 24)
        icon.setStyleSheet(f"""
            background-color: {'#009B77' if is_active else '#444'};
            border-radius: 12px;
        """)
        layout.addWidget(icon)
        
        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        name_lbl = QLabel(step_data['name'])
        name_lbl.setStyleSheet(f"font-weight: {'bold' if is_active else 'normal'}; color: {'#FFF' if is_active else '#BBB'}; font-size: 14px;")
        
        desc_lbl = QLabel(step_data.get('type', 'Process'))
        desc_lbl.setStyleSheet("color: #666; font-size: 11px;")
        
        text_layout.addWidget(name_lbl)
        text_layout.addWidget(desc_lbl)
        layout.addLayout(text_layout)
        
        # Styling
        if is_active:
            self.setStyleSheet("""
                PipelineStepItem {
                    background-color: rgba(0, 155, 119, 0.1);
                    border-left: 3px solid #009B77;
                    border-radius: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                PipelineStepItem:hover {
                    background-color: rgba(255, 255, 255, 0.05);
                }
            """)

class FloatingToolbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(16)
        self.setStyleSheet("""
            FloatingToolbar {
                background-color: rgba(30, 30, 30, 0.9);
                border: 1px solid #444;
                border-radius: 20px;
            }
            QToolButton {
                border: none;
                background: transparent;
                color: #AAA;
                padding: 4px;
            }
            QToolButton:checked {
                color: #009B77;
            }
            QToolButton:hover {
                color: #FFF;
            }
        """)

    def add_tool(self, name, icon_char, is_checked=False):
        btn = QToolButton()
        btn.setText(icon_char) # Using text as icon placeholder for now
        btn.setCheckable(True)
        btn.setChecked(is_checked)
        btn.setFixedSize(32, 32)
        self.layout.addWidget(btn)
        return btn

class ComparisonCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setBackgroundBrush(QColor("#111"))
        self.setFrameShape(QFrame.NoFrame)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Placeholders
        text = self.scene.addText("Image Canvas Placeholder")
        text.setDefaultTextColor(QColor("#555"))
        text.setScale(2)
        
        # Split line simulation
        line = self.scene.addLine(400, 0, 400, 800, QPen(QColor("#00FFFF"), 2))
        line.setZValue(10)

# ==============================================================================
# Main Component
# ==============================================================================

class ImageAnalysisWorkspace(QWidget):
    # Signals
    select_step = Signal(str)
    
    def __init__(self, data=None):
        super().__init__()
        self.data = data or {}
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ----------------------------------------------------------------------
        # LEFT SIDEBAR: PIPELINE
        # ----------------------------------------------------------------------
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("background-color: #1E1E1E; border-right: 1px solid #333;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        # Header
        header_lbl = QLabel("PIPELINE")
        header_lbl.setStyleSheet("color: #AAA; font-size: 12px; font-weight: bold; padding-left: 16px; margin-bottom: 10px;")
        sidebar_layout.addWidget(header_lbl)
        
        # Steps List
        self.steps_container = QVBoxLayout()
        self.steps_container.setSpacing(4)
        self.steps_container.setAlignment(Qt.AlignTop)
        
        pipeline = self.data.get('pipeline', {})
        steps = pipeline.get('steps', [])
        
        for i, step in enumerate(steps):
            w = PipelineStepItem(step, is_active=(i == len(steps)-1))
            self.steps_container.addWidget(w)
            
            # Vertical connector line (except last)
            if i < len(steps) - 1:
                line = QFrame()
                line.setFixedWidth(2)
                line.setFixedHeight(12)
                line.setStyleSheet("background-color: #444; margin-left: 27px;")
                self.steps_container.addWidget(line)
                
        sidebar_layout.addLayout(self.steps_container)
        sidebar_layout.addStretch()
        
        # Add Button
        add_btn = QPushButton("+ Add Step")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px dashed #555;
                color: #AAA;
                border-radius: 4px;
                margin: 16px;
            }
            QPushButton:hover {
                border-color: #777;
                color: #FFF;
            }
        """)
        sidebar_layout.addWidget(add_btn)
        
        main_layout.addWidget(sidebar)
        
        # ----------------------------------------------------------------------
        # CENTER: CANVAS
        # ----------------------------------------------------------------------
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Canvas Container (Z-stacking via parenting)
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        
        self.canvas = ComparisonCanvas()
        canvas_layout.addWidget(self.canvas)
        
        # Top Floating Toolbar
        self.top_toolbar = FloatingToolbar(canvas_container)
        self.top_toolbar.add_tool("H", "✋", True) # Hand
        self.top_toolbar.add_tool("M", "📏", False) # Ruler
        self.top_toolbar.add_tool("P", "📍", False) # Pin
        self.top_toolbar.add_tool("Z", "🔍", False) # Zoom
        self.top_toolbar.move(200, 20) # Position manually or use layout
        # Note: In a real implementation, we'd resize this on resizeEvent
        
        # Bottom Info Pill
        self.bottom_info = QFrame(canvas_container)
        self.bottom_info.setStyleSheet("""
            background-color: #000; border-radius: 16px; padding: 4px 16px;
        """)
        bi_layout = QHBoxLayout(self.bottom_info)
        bi_layout.setContentsMargins(8, 4, 8, 4)
        
        info_lbl = QLabel(f"Zoom: 100%  |  Image: {self.data.get('image', {}).get('filename', 'Unknown')}  |  1024x1024 px")
        info_lbl.setStyleSheet("color: #AAA; font-family: 'Cascadia Code'; font-size: 11px;")
        bi_layout.addWidget(info_lbl)
        
        # Position bottom pill (requires resizeEvent logic for real centering)
        self.bottom_info.move(200, 700) 

        center_layout.addWidget(canvas_container)
        main_layout.addWidget(center_panel)
        
        # ----------------------------------------------------------------------
        # RIGHT SIDEBAR: INSPECTOR
        # ----------------------------------------------------------------------
        inspector = QFrame()
        inspector.setFixedWidth(300)
        inspector.setStyleSheet("background-color: #1E1E1E; border-left: 1px solid #333;")
        inspector_layout = QVBoxLayout(inspector)
        inspector_layout.setContentsMargins(20, 20, 20, 20)
        inspector_layout.setSpacing(24)
        
        insp_header = QLabel("INSPECTOR")
        insp_header.setStyleSheet("color: #AAA; font-size: 12px; font-weight: bold;")
        inspector_layout.addWidget(insp_header)
        
        # Properties Panel
        props_frame = QFrame()
        props_frame.setStyleSheet("""
            QFrame { background-color: #252525; border-radius: 8px; }
            QLabel { color: #DDD; }
        """)
        props_layout = QVBoxLayout(props_frame)
        
        props_title = QLabel("Properties")
        props_title.setStyleSheet("font-weight: bold; margin-bottom: 8px; color: #009B77;")
        props_layout.addWidget(props_title)
        
        # Threshold Slider
        props_layout.addWidget(QLabel("Threshold"))
        slider = QSlider(Qt.Horizontal)
        slider.setValue(15)
        slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 4px; background: #444; border-radius: 2px; }
            QSlider::handle:horizontal { background: #009B77; width: 16px; margin: -6px 0; border-radius: 8px; }
        """)
        props_layout.addWidget(slider)
        
        # Radius Slider
        props_layout.addWidget(QLabel("Radius"))
        r_slider = QSlider(Qt.Horizontal)
        r_slider.setValue(30)
        r_slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 4px; background: #444; border-radius: 2px; }
            QSlider::handle:horizontal { background: #009B77; width: 16px; margin: -6px 0; border-radius: 8px; }
        """)
        props_layout.addWidget(r_slider)
        
        inspector_layout.addWidget(props_frame)
        
        # Histogram
        hist_frame = QFrame()
        hist_frame.setStyleSheet("background-color: #252525; border-radius: 8px;")
        hist_layout = QVBoxLayout(hist_frame)
        hist_title = QLabel("Histogram")
        hist_title.setStyleSheet("font-weight: bold; color: #009B77;")
        hist_layout.addWidget(hist_title)
        
        # Placeholder bars
        bars_widget = QWidget()
        bars_widget.setFixedHeight(120)
        bars_widget.setStyleSheet("background-color: transparent;")
        # (In real app, draw bars here with QPainter)
        hl = QHBoxLayout(bars_widget)
        hl.setSpacing(2)
        hl.setAlignment(Qt.AlignBottom)
        for h in [20, 40, 60, 90, 45, 30, 10]:
            bar = QFrame()
            bar.setFixedWidth(20)
            bar.setFixedHeight(h)
            bar.setStyleSheet("background-color: #D4AF37; opacity: 0.6; border-radius: 2px;")
            hl.addWidget(bar)
            
        hist_layout.addWidget(bars_widget)
        
        inspector_layout.addWidget(hist_frame)
        
        # Data Grid
        data_frame = QFrame()
        data_frame.setStyleSheet("background-color: #111; border-radius: 4px; padding: 10px;")
        grid = QHBoxLayout(data_frame)
        
        val_layout = QVBoxLayout()
        val_lbl = QLabel("PIXEL INTENSITY")
        val_lbl.setStyleSheet("color: #666; font-size: 10px;")
        val_val = QLabel("142")
        val_val.setStyleSheet("color: #D4AF37; font-size: 18px; font-weight: bold;")
        val_layout.addWidget(val_lbl)
        val_layout.addWidget(val_val)
        
        coord_layout = QVBoxLayout()
        coord_lbl = QLabel("COORDINATES")
        coord_lbl.setStyleSheet("color: #666; font-size: 10px;")
        coord_val = QLabel("(512, 512)")
        coord_val.setStyleSheet("color: #009B77; font-size: 18px; font-weight: bold;")
        coord_layout.addWidget(coord_lbl)
        coord_layout.addWidget(coord_val)
        
        grid.addLayout(val_layout)
        grid.addLayout(coord_layout)
        
        inspector_layout.addWidget(data_frame)
        inspector_layout.addStretch()

        main_layout.addWidget(inspector)

    def resizeEvent(self, event):
        # Keep floating widgets centered/positioned
        if hasattr(self, 'top_toolbar'):
            self.top_toolbar.move((self.canvas.width() - self.top_toolbar.width()) // 2, 20)
        if hasattr(self, 'bottom_info'):
            self.bottom_info.move((self.canvas.width() - self.bottom_info.width()) // 2, self.canvas.height() - 60)
        super().resizeEvent(event)
