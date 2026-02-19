
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QRubberBand, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap, QImage, QPainter, QWheelEvent, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QRect
import cv2
import numpy as np

class ImageViewer(QGraphicsView):
    """
    A widget to display images with zoom and pan support.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self._pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self._pixmap_item)
        
        # State
        self._image = None
        self._zoom_factor = 1.0
        
        # Configuration
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(Qt.GlobalColor.black)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)

    def set_image(self, image: np.ndarray):
        """
        Set the image to display.
        Args:
            image: Numpy array (BGR or Gray).
        """
        self._image = image
        if image is None:
            self._pixmap_item.setPixmap(QPixmap())
            return

        # Convert to QImage
        height, width = image.shape[:2]
        
        if len(image.shape) == 2:
            # Grayscale
            qimg = QImage(image.data, width, height, width, QImage.Format.Format_Grayscale8)
        else:
            # BGR to RGB
            # Only convert if 3 channels
            if image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                qimg = QImage(rgb_image.data, width, height, 3 * width, QImage.Format.Format_RGB888)
            elif image.shape[2] == 4:
                # BGRA to RGBA
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
                qimg = QImage(rgb_image.data, width, height, 4 * width, QImage.Format.Format_RGBA8888)
            else:
                 # Fallback
                 return 
        
        pixmap = QPixmap.fromImage(qimg)
        self._pixmap_item.setPixmap(pixmap)
        self.setSceneRect(0, 0, width, height)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        """Zoom with mouse wheel."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)
