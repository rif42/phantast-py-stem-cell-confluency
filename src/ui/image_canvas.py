import os
import logging
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPixmap, QWheelEvent, QMouseEvent


logger = logging.getLogger(__name__)


class ImageCanvas(QGraphicsView):
    zoom_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup Scene
        self.graphics_scene = QGraphicsScene(self)
        self.setScene(self.graphics_scene)

        # UI Configuration
        self.setRenderHint(self.renderHints().Antialiasing, True)
        self.setRenderHint(self.renderHints().SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: transparent; border: none;")

        # State
        self.pixmap_item = QGraphicsPixmapItem()
        self.pixmap_item.setZValue(0)
        self.graphics_scene.addItem(self.pixmap_item)

        self.overlay_item = QGraphicsPixmapItem()
        self.overlay_item.setZValue(10)
        self.overlay_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.graphics_scene.addItem(self.overlay_item)
        self.overlay_item.hide()

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
        self.clear_overlay()
        self.graphics_scene.setSceneRect(self.pixmap_item.boundingRect())

        # Reset to 100% zoom (1.0 scale) instead of fitting to view
        self.resetTransform()
        self.current_scale = 1.0
        self.zoom_changed.emit(self.get_current_zoom_percentage())
        return True

    def set_overlay_image(self, image_path: str) -> bool:
        """Load and set overlay image. Returns True on success."""
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return False

        base_pixmap = self.pixmap_item.pixmap()
        if not base_pixmap.isNull():
            if (
                pixmap.width() != base_pixmap.width()
                or pixmap.height() != base_pixmap.height()
            ):
                logger.warning(
                    "Overlay size %sx%s doesn't match base %sx%s",
                    pixmap.width(),
                    pixmap.height(),
                    base_pixmap.width(),
                    base_pixmap.height(),
                )

        self.overlay_item.setPos(self.pixmap_item.pos())
        self.overlay_item.setPixmap(pixmap)
        return True

    def show_overlay(self, visible: bool):
        """Show or hide the overlay."""
        if visible:
            self.overlay_item.show()
        else:
            self.overlay_item.hide()

    def has_overlay(self) -> bool:
        """Check if an overlay image is set."""
        return not self.overlay_item.pixmap().isNull()

    def clear_overlay(self):
        """Remove the overlay image."""
        self.overlay_item.setPixmap(QPixmap())
        self.overlay_item.hide()

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

    def wheelEvent(self, event: QWheelEvent | None):
        """Handles zooming with the mouse wheel."""
        if event is None:
            return

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

    def mousePressEvent(self, event: QMouseEvent | None):
        if event is None:
            return

        if self.pan_active and event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = True
            self._pan_start_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent | None):
        if event is None:
            return

        if self._is_panning:
            delta = event.position() - self._pan_start_pos

            # Translate the view (we use horizontal/vertical scrollbars under the hood)
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()

            if h_bar is not None and v_bar is not None:
                h_bar.setValue(int(h_bar.value() - delta.x()))
                v_bar.setValue(int(v_bar.value() - delta.y()))

            self._pan_start_pos = event.position()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent | None):
        if event is None:
            return

        if self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
