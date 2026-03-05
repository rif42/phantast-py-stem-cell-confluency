# Work Plan: Floating Toolbar Implementation

## Overview
Add a floating toolbar with pan, zoom, and ruler tools to `ImageCanvas` that appears when an image is loaded.

## Goal
Replicate the prototype `ImageViewer.floating_toolbar` functionality in the main app's `ImageCanvas`.

---

## Phase 1: Implementation (image_canvas.py)

### 1.1 Add FloatingToolbar Widget
**Location:** `src/ui/image_canvas.py`

**Add to `__init__`:**
```python
# Floating toolbar overlay
self.floating_toolbar = FloatingToolbar(self)
self.floating_toolbar.hide()

# Connect toolbar signals
self.floating_toolbar.pan_clicked.connect(self.set_pan_mode)
self.floating_toolbar.zoom_in_clicked.connect(self.zoom_in)
self.floating_toolbar.zoom_out_clicked.connect(self.zoom_out)
self.floating_toolbar.fit_clicked.connect(self.fit_to_view)
```

**Add FloatingToolbar class:**
- Create as inner class or separate class in same file
- Buttons: Pan (✋), Ruler (📏), Pin (📍), Fit (⛶), Zoom (-/+)
- Zoom label showing percentage
- Dark theme styling matching app (#161C1A bg, #2A3331 border)
- Fixed size: 300x40px

### 1.2 Implement Toolbar Methods
**Add missing methods:**
```python
def fit_to_view(self):
    """Fit image to canvas view."""
    if self.pixmap_item and self.pixmap_item.pixmap():
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.current_scale = self.transform().m11()
        self.zoom_changed.emit(self.get_current_zoom_percentage())

def display_image(self, pixmap: QPixmap):
    """Display a QPixmap directly (for pipeline preview)."""
    self.pixmap_item.setPixmap(pixmap)
    self.scene.setSceneRect(self.pixmap_item.boundingRect())
    self.fit_to_view()
```

### 1.3 Add resizeEvent Override
```python
def resizeEvent(self, event):
    """Position floating toolbar at top-center."""
    super().resizeEvent(event)
    if self.floating_toolbar.isVisible():
        fx = (self.width() - self.floating_toolbar.width()) // 2
        self.floating_toolbar.move(int(fx), 20)
```

### 1.4 Update load_image Method
```python
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
    self.scene.setSceneRect(self.pixmap_item.boundingRect())
    
    # Center and fit the image initially
    self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    self.current_scale = self.transform().m11()
    self.zoom_changed.emit(self.get_current_zoom_percentage())
    
    # Show toolbar
    self.floating_toolbar.show()
    return True
```

### 1.5 Add clear_image Method
```python
def clear_image(self):
    """Clear the canvas and hide toolbar."""
    self.pixmap_item.setPixmap(QPixmap())
    self.floating_toolbar.hide()
```

---

## Phase 2: Integration (unified_main_widget.py)

### 2.1 Update _on_image_cleared
**Current:**
```python
def _on_image_cleared(self):
    if hasattr(self.canvas, "scene") and self.canvas.scene:
        self.canvas.scene.clear()
```

**Change to:**
```python
def _on_image_cleared(self):
    self.canvas.clear_image()
    self.properties_panel.update_metadata()
```

---

## Phase 3: Styling

### Toolbar Style (matching prototype)
```python
"""
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
QPushButton:checked {
    background-color: #009B77;
    color: #FFFFFF;
}
"""
```

---

## Phase 4: Testing Checklist

- [ ] Load image → toolbar appears at top-center
- [ ] Pan button toggles pan mode (cursor changes)
- [ ] Ruler button shows/hides ruler (placeholder)
- [ ] Pin button shows/hides markers (placeholder)
- [ ] Fit button fits image to view
- [ ] Zoom +/- buttons adjust zoom
- [ ] Zoom percentage label updates correctly
- [ ] Clear/close image → toolbar hides
- [ ] Pipeline preview shows toolbar
- [ ] Toolbar stays centered on window resize

---

## Files Modified
1. `src/ui/image_canvas.py` - Add FloatingToolbar class and integration
2. `src/ui/unified_main_widget.py` - Use canvas.clear_image() instead of scene.clear()

## Dependencies
- None (uses existing PyQt6 imports)

## Rollback
If issues arise:
1. Revert `image_canvas.py` to commit before changes
2. Revert `unified_main_widget.py` to commit before changes

## References
- Prototype: `shell/gui/image_viewer.py` lines 144-246
- Styling: AGENTS.md theme colors
