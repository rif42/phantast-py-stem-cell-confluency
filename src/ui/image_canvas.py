import os
from PyQt6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPixmap, QWheelEvent, QMouseEvent


class FloatingToolbar(QWidget):
    """Floating toolbar with pan, zoom, and ruler tools."""

    pan_clicked = pyqtSignal(bool)  # active state
    zoom_in_clicked = pyqtSignal()
    zoom_out_clicked = pyqtSignal()
    fit_clicked = pyqtSignal()
    ruler_clicked = pyqtSignal(bool)  # active state
    pin_clicked = pyqtSignal(bool)  # active state

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(300, 40)

        # Enable transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(22, 28, 26, 200);
                border: 1px solid rgba(42, 51, 49, 150);
                border-radius: 8px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #889996;
                font-weight: bold;
                font-size: 14px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: rgba(35, 43, 41, 180);
                border-radius: 4px;
            }
            QPushButton:checked {
                background-color: #009B77;
                color: #FFFFFF;
                border-radius: 4px;
            }
            QLabel {
                color: #889996;
                font-size: 11px;
                border: none;
            }
            QLabel#separator {
                color: #2A3331;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        # Tool buttons
        self.btn_hand = QPushButton("✋")
        self.btn_hand.setCheckable(True)
        self.btn_hand.setToolTip("Pan tool")
        self.btn_hand.clicked.connect(self._on_pan_clicked)

        self.btn_ruler = QPushButton("📏")
        self.btn_ruler.setCheckable(True)
        self.btn_ruler.setToolTip("Ruler tool")
        self.btn_ruler.clicked.connect(self._on_ruler_clicked)

        self.btn_pin = QPushButton("📍")
        self.btn_pin.setCheckable(True)
        self.btn_pin.setToolTip("Marker tool")
        self.btn_pin.clicked.connect(self._on_pin_clicked)

        self.btn_fit = QPushButton("⛶")
        self.btn_fit.setToolTip("Fit to view")
        self.btn_fit.clicked.connect(self.fit_clicked.emit)

        # Separator
        sep = QLabel("|")
        sep.setObjectName("separator")

        # Zoom controls
        self.btn_minus = QPushButton("－")
        self.btn_minus.setToolTip("Zoom out")
        self.btn_minus.clicked.connect(self.zoom_out_clicked.emit)

        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setFixedWidth(45)
        self.lbl_zoom.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_plus = QPushButton("＋")
        self.btn_plus.setToolTip("Zoom in")
        self.btn_plus.clicked.connect(self.zoom_in_clicked.emit)

        # Add widgets to layout
        layout.addWidget(self.btn_hand)
        layout.addWidget(self.btn_ruler)
        layout.addWidget(self.btn_pin)
        layout.addWidget(self.btn_fit)
        layout.addWidget(sep)
        layout.addWidget(self.btn_minus)
        layout.addWidget(self.lbl_zoom)
        layout.addWidget(self.btn_plus)

    def _on_pan_clicked(self, checked):
        """Handle pan button click."""
        self.pan_clicked.emit(checked)
        # Uncheck other tools
        if checked:
            self.btn_ruler.setChecked(False)
            self.btn_pin.setChecked(False)

    def _on_ruler_clicked(self, checked):
        """Handle ruler button click."""
        self.ruler_clicked.emit(checked)
        # Uncheck other tools
        if checked:
            self.btn_hand.setChecked(False)
            self.btn_pin.setChecked(False)

    def _on_pin_clicked(self, checked):
        """Handle pin button click."""
        self.pin_clicked.emit(checked)
        # Uncheck other tools
        if checked:
            self.btn_hand.setChecked(False)
            self.btn_ruler.setChecked(False)

    def set_zoom_percentage(self, percentage: int):
        """Update the zoom percentage label."""
        self.lbl_zoom.setText(f"{percentage}%")

    def reset_tools(self):
        """Uncheck all tool buttons."""
        self.btn_hand.setChecked(False)
        self.btn_ruler.setChecked(False)
        self.btn_pin.setChecked(False)


class ImageCanvas(QGraphicsView):
    zoom_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup Scene
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        # UI Configuration
        self.setRenderHint(self.renderHints().Antialiasing, True)
        self.setRenderHint(self.renderHints().SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: transparent; border: none;")

        # State
        self.pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self.pixmap_item)

        self.zoom_factor = 1.15
        self.current_scale = 1.0

        self.pan_active = False
        self._is_panning = False
        self._pan_start_pos = QPointF()

        # Floating toolbar
        self.floating_toolbar = FloatingToolbar(self)
        self.floating_toolbar.hide()

        # Connect toolbar signals
        self.floating_toolbar.pan_clicked.connect(self.set_pan_mode)
        self.floating_toolbar.zoom_in_clicked.connect(self.zoom_in)
        self.floating_toolbar.zoom_out_clicked.connect(self.zoom_out)
        self.floating_toolbar.fit_clicked.connect(self.fit_to_view)

    def load_image(self, file_path: str):
        """Loads an image into the canvas."""
        if not os.path.exists(file_path):
            self.floating_toolbar.hide()
            return False

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            self.floating_toolbar.hide()
            return False

        self.pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(self.pixmap_item.boundingRect())

        # Center and fit the image initially
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.current_scale = self.transform().m11()
        self.zoom_changed.emit(self.get_current_zoom_percentage())

        # Show toolbar
        self.floating_toolbar.show()
        self._update_toolbar_position()

        return True

    def display_image(self, pixmap: QPixmap):
        """Display a QPixmap directly (for pipeline preview)."""
        if pixmap.isNull():
            self.floating_toolbar.hide()
            return

        self.pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(self.pixmap_item.boundingRect())
        self.fit_to_view()

        # Show toolbar
        self.floating_toolbar.show()
        self._update_toolbar_position()

    def clear_image(self):
        """Clear the canvas and hide toolbar."""
        self.pixmap_item.setPixmap(QPixmap())
        self.floating_toolbar.hide()
        self.floating_toolbar.reset_tools()
        self.set_pan_mode(False)

    def set_pan_mode(self, active: bool):
        """Toggles panning mode on or off."""
        self.pan_active = active
        if active:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self._is_panning = False

    def zoom_in(self):
        self.scale_view(self.zoom_factor)

    def zoom_out(self):
        self.scale_view(1 / self.zoom_factor)

    def scale_view(self, factor):
        """Scales the view by a given factor."""
        # Optional: Add boundary limits here (e.g. 0.1 to 10.0)
        self.scale(factor, factor)
        self.current_scale = self.transform().m11()
        zoom_pct = self.get_current_zoom_percentage()
        self.zoom_changed.emit(zoom_pct)
        self.floating_toolbar.set_zoom_percentage(zoom_pct)

    def fit_to_view(self):
        """Fit image to canvas view."""
        if self.pixmap_item and not self.pixmap_item.pixmap().isNull():
            self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.current_scale = self.transform().m11()
            zoom_pct = self.get_current_zoom_percentage()
            self.zoom_changed.emit(zoom_pct)
            self.floating_toolbar.set_zoom_percentage(zoom_pct)

    def get_current_zoom_percentage(self) -> int:
        """Returns the zoom percentage as an integer."""
        # This is an approximation relative to original image size
        # A more robust approach would compare viewport size to scene rect
        return int(self.current_scale * 100)

    def _update_toolbar_position(self):
        """Position floating toolbar at top-center."""
        if self.floating_toolbar.isVisible():
            fx = (self.width() - self.floating_toolbar.width()) // 2
            self.floating_toolbar.move(int(fx), 20)

    def resizeEvent(self, event):
        """Handle resize and reposition toolbar."""
        super().resizeEvent(event)
        self._update_toolbar_position()

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
            super().mousePressEvent(event)
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
            super().mouseMoveEvent(event)
            return

        if self._is_panning:
            delta = event.position() - self._pan_start_pos

            # Translate the view (we use horizontal/vertical scrollbars under the hood)
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()

            if h_bar is not None:
                h_bar.setValue(int(h_bar.value() - delta.x()))
            if v_bar is not None:
                v_bar.setValue(int(v_bar.value() - delta.y()))

            self._pan_start_pos = event.position()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent | None):
        if event is None:
            super().mouseReleaseEvent(event)
            return

        if self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
