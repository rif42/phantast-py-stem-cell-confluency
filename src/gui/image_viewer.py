from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, 
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget
)
from PyQt6.QtGui import QPixmap, QImage, QWheelEvent, QMouseEvent, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import cv2
import numpy as np

class ImageGraphicsView(QGraphicsView):
    """Internal graphics view for zooming/panning."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self._pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self._pixmap_item)
        
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Background color for the canvas
        self.setBackgroundBrush(QColor("#0D1110")) 
        self.setFrameShape(QGraphicsView.Shape.NoFrame)

    def wheelEvent(self, event: QWheelEvent):
        """Zoom with mouse wheel."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

    def set_pixmap(self, pixmap, width, height):
        self._pixmap_item.setPixmap(pixmap)
        self.setSceneRect(0, 0, width, height)
        # Assuming we want to reset zoom on new image
        self.resetTransform()
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


class ImageViewer(QWidget):
    """
    A widget to display images with zoom and pan support, 
    including an empty state and floating overlays.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image = None
        
        self.setStyleSheet("background-color: #0D1110;") # Deepest dark for canvas
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # We need relative positioning for the floating toolbar, 
        # so we'll use a QVBoxLayout for the main stack, and add the floating controls later 
        # (or just use absolute positioning in resizeEvent for true floating).
        # For simplicity, we can just put a top bar layout and stack below it, if it doesn't need to absolutely float over the image.
        # But the design shows it floating over the canvas. We'll use absolute positioning for overlays.

        self.stack = QStackedWidget(self)
        main_layout.addWidget(self.stack)

        # 1. Empty State
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Dash Border Box
        drop_box = QWidget()
        drop_box.setFixedSize(600, 500)
        drop_box.setStyleSheet("""
            QWidget {
                border: 2px dashed #2A3331;
                border-radius: 12px;
                background-color: transparent;
            }
        """)
        db_layout = QVBoxLayout(drop_box)
        db_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_lbl = QLabel("+")
        icon_lbl.setStyleSheet("font-size: 32px; color: #009B77; background-color: #162420; border-radius: 32px; border: none;")
        icon_lbl.setFixedSize(64, 64)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_lbl = QLabel("Drag and drop an image here")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF; border: none;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc_lbl = QLabel("or <span style='color: #009B77; text-decoration: underline;'>click to browse</span> your local files")
        desc_lbl.setStyleSheet("font-size: 14px; color: #889996; border: none;")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        fmt_lbl = QLabel("Supports JPG, PNG, TIFF & RAW formats up to 100MB")
        fmt_lbl.setStyleSheet("font-size: 11px; color: #556663; border: none;")
        fmt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Sample Thumbnails...
        samples_layout = QHBoxLayout()
        samples_layout.setSpacing(16)
        samples_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mock thumbnails (using colored squares)
        for i in range(2):
            th = QLabel()
            th.setFixedSize(80, 80)
            th.setStyleSheet("background-color: #2A3331; border-radius: 8px; border: none;")
            samples_layout.addWidget(th)
            
        load_sample = QPushButton("Load Sample")
        load_sample.setFixedSize(80, 80)
        load_sample.setStyleSheet("background-color: #1E2523; color: #889996; border-radius: 8px; font-size: 10px; border: 1px solid #2A3331;")
        samples_layout.addWidget(load_sample)
        
        db_layout.addStretch()
        db_layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        db_layout.addSpacing(24)
        db_layout.addWidget(title_lbl)
        db_layout.addSpacing(8)
        db_layout.addWidget(desc_lbl)
        db_layout.addSpacing(16)
        db_layout.addWidget(fmt_lbl)
        db_layout.addSpacing(40)
        db_layout.addLayout(samples_layout)
        db_layout.addStretch()
        
        empty_layout.addWidget(drop_box)
        self.stack.addWidget(self.empty_widget)

        # 2. Graphics View State
        self.graphics_view = ImageGraphicsView()
        self.stack.addWidget(self.graphics_view)
        
        # Overlay: Floating Toolbar (Top Center)
        self.floating_toolbar = QWidget(self)
        self.floating_toolbar.setFixedSize(300, 40)
        self.floating_toolbar.setStyleSheet("""
            QWidget {
                background-color: #161C1A;
                border: 1px solid #2A3331;
                border-radius: 8px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #889996;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #232B29;
            }
        """)
        ft_layout = QHBoxLayout(self.floating_toolbar)
        ft_layout.setContentsMargins(8, 4, 8, 4)
        ft_layout.setSpacing(4)
        
        btn_hand = QPushButton("✋")
        btn_ruler = QPushButton("📏")
        btn_pin = QPushButton("📍")
        btn_fit = QPushButton("⛶")
        sep = QLabel(" | ")
        sep.setStyleSheet("color: #2A3331; border: none;")
        btn_minus = QPushButton("－")
        lbl_zoom = QLabel("100%")
        lbl_zoom.setStyleSheet("color: #889996; font-size: 11px; border: none;")
        btn_plus = QPushButton("＋")
        
        ft_layout.addWidget(btn_hand)
        ft_layout.addWidget(btn_ruler)
        ft_layout.addWidget(btn_pin)
        ft_layout.addWidget(btn_fit)
        ft_layout.addWidget(sep)
        ft_layout.addWidget(btn_minus)
        ft_layout.addWidget(lbl_zoom)
        ft_layout.addWidget(btn_plus)
        
        self.floating_toolbar.hide() # Hidden initially
        
        # Overlay: Status Bottom Right
        self.status_lbl = QLabel("Canvas: 1920x1080 • Zoom: 100%", self)
        self.status_lbl.setStyleSheet("color: #556663; font-size: 11px; font-family: 'Cascadia Code', monospace; background-color: transparent;")
        self.status_lbl.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position floating toolbar top-center
        fx = (self.width() - self.floating_toolbar.width()) // 2
        self.floating_toolbar.move(int(fx), 20)
        
        # Position status bottom-right
        self.status_lbl.adjustSize()
        self.status_lbl.move(
            int(self.width() - self.status_lbl.width() - 20), 
            int(self.height() - self.status_lbl.height() - 10)
        )

    def set_image(self, image: np.ndarray):
        """
        Set the image to display.
        Args:
            image: Numpy array (BGR or Gray).
        """
        self._image = image
        if image is None:
            self.stack.setCurrentIndex(0)
            self.floating_toolbar.hide()
            self.status_lbl.hide()
            return

        self.stack.setCurrentIndex(1)
        self.floating_toolbar.show()
        self.status_lbl.show()
        
        height, width = image.shape[:2]
        self.status_lbl.setText(f"Canvas: {width}x{height} • Zoom: 100%")
        
        # Convert to QImage
        from PyQt6.QtGui import QColor # Ensure QColor is available here too if needed, actually imported at top
        
        if len(image.shape) == 2:
            # Grayscale
            qimg = QImage(image.data, width, height, width, QImage.Format.Format_Grayscale8)
        else:
            if image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                qimg = QImage(rgb_image.data, width, height, 3 * width, QImage.Format.Format_RGB888)
            elif image.shape[2] == 4:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
                qimg = QImage(rgb_image.data, width, height, 4 * width, QImage.Format.Format_RGBA8888)
            else:
                 return 
        
        pixmap = QPixmap.fromImage(qimg)
        self.graphics_view.set_pixmap(pixmap, width, height)

