import os
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPixmap, QWheelEvent, QMouseEvent

class ImageCanvas(QGraphicsView):
    zoom_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup Scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # UI Configuration
        self.setRenderHint(self.renderHints().Antialiasing, True)
        self.setRenderHint(self.renderHints().SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: transparent; border: none;")
        
        # State
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        
        self.zoom_factor = 1.15
        self.current_scale = 1.0
        
        self.pan_active = False
        self._is_panning = False
        self._pan_start_pos = QPointF()
        
    def load_image(self, file_path: str):
        """Loads an image into the canvas."""
        if not os.path.exists(file_path):
            return False
            
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            return False
            
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        
        # Center and fit the image initially
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.current_scale = self.transform().m11()
        self.zoom_changed.emit(self.get_current_zoom_percentage())
        return True
        
    def set_pan_mode(self, active: bool):
        """Toggles panning mode on or off."""
        self.pan_active = active
        if active:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def zoom_in(self):
        self.scale_view(self.zoom_factor)

    def zoom_out(self):
        self.scale_view(1 / self.zoom_factor)
        
    def scale_view(self, factor):
        """Scales the view by a given factor."""
        # Optional: Add boundary limits here (e.g. 0.1 to 10.0)
        self.scale(factor, factor)
        self.current_scale = self.transform().m11()
        self.zoom_changed.emit(self.get_current_zoom_percentage())
        
    def get_current_zoom_percentage(self) -> int:
        """Returns the zoom percentage as an integer."""
        # This is an approximation relative to original image size
        # A more robust approach would compare viewport size to scene rect
        return int(self.current_scale * 100)

    # --- Event Overrides for Interaction ---

    def wheelEvent(self, event: QWheelEvent):
        """Handles zooming with the mouse wheel."""
        # Calculate cursor position in scene coords before zoom
        mouse_pos = event.position()
        scene_pos_before = self.mapToScene(mouse_pos.toPoint())
        
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
            
        # Re-center accurately on mouse cursor
        scene_pos_after = self.mapToScene(mouse_pos.toPoint())
        delta = scene_pos_after - scene_pos_before
        
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event: QMouseEvent):
        if self.pan_active and event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = True
            self._pan_start_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            delta = event.position() - self._pan_start_pos
            
            # Translate the view (we use horizontal/vertical scrollbars under the hood)
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            
            h_bar.setValue(int(h_bar.value() - delta.x()))
            v_bar.setValue(int(v_bar.value() - delta.y()))
            
            self._pan_start_pos = event.position()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
