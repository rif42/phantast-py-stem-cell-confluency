# Mask Overlay & Before/After Comparison - Implementation Plan

## Overview
Add interactive mask overlay and before/after comparison for PHANTAST segmentation nodes. Users can toggle between original/processed images and show/hide segmentation masks with visual overlay.

---

## Architecture

### Data Model
```python
# src/models/image_variants.py
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class ImageVariant:
    """Tracks a processed version of an image."""
    path: str
    variant_type: str  # 'original', 'processed', 'mask', 'overlay'
    source_path: Optional[str] = None  # Original image this was derived from
    step_name: Optional[str] = None  # Which step generated this (e.g., 'phantast')

class ImageVariantManager:
    """Manages multiple variants of the same source image."""
    
    def __init__(self):
        self.variants: Dict[str, list[ImageVariant]] = {}  # source_path -> variants
    
    def add_variant(self, source_path: str, variant: ImageVariant):
        """Register a new variant for a source image."""
        if source_path not in self.variants:
            self.variants[source_path] = []
        self.variants[source_path].append(variant)
    
    def get_variants(self, source_path: str) -> list[ImageVariant]:
        """Get all variants for a source image."""
        return self.variants.get(source_path, [])
    
    def get_variant(self, source_path: str, variant_type: str) -> Optional[ImageVariant]:
        """Get specific variant type for a source image."""
        for v in self.variants.get(source_path, []):
            if v.variant_type == variant_type:
                return v
        return None
    
    def has_mask(self, source_path: str) -> bool:
        """Check if mask variant exists for source image."""
        return any(v.variant_type == 'mask' for v in self.variants.get(source_path, []))
```

### Canvas Overlay System
```python
# src/ui/image_canvas.py additions

class ImageCanvas(QGraphicsView):
    def __init__(self, parent=None):
        # ... existing init ...
        
        # Add overlay pixmap item (for mask)
        self.overlay_pixmap = QGraphicsPixmapItem()
        self.overlay_pixmap.setZValue(10)  # Above base image
        self.overlay_pixmap.setOpacity(0.5)  # 50% transparent
        self.scene.addItem(self.overlay_pixmap)
        self.overlay_pixmap.setVisible(False)
        
        # View state
        self.current_base_image: Optional[str] = None  # Path to current base image
        self.overlay_mode: str = 'none'  # 'none', 'mask'
        self.view_mode: str = 'processed'  # 'original', 'processed'
        
    def set_overlay_image(self, image_path: Optional[str], opacity: float = 0.5):
        """Set overlay image (mask) with transparency."""
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.overlay_pixmap.setPixmap(pixmap)
            self.overlay_pixmap.setOpacity(opacity)
            self.overlay_pixmap.setVisible(True)
        else:
            self.overlay_pixmap.setVisible(False)
    
    def show_mask(self, show: bool = True):
        """Toggle mask overlay visibility."""
        self.overlay_mode = 'mask' if show else 'none'
        self.overlay_pixmap.setVisible(show)
    
    def switch_base_image(self, image_path: str):
        """Switch base image while preserving overlay state."""
        self.load_image(image_path)
        self.current_base_image = image_path
        # Restore overlay if it was visible
        if self.overlay_mode == 'mask':
            self.overlay_pixmap.setVisible(True)
```

### Control Panel Widget
```python
# src/ui/comparison_controls.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

class ComparisonControls(QWidget):
    """Toggle controls for before/after and mask overlay."""
    
    # Signals
    view_mode_changed = pyqtSignal(str)  # 'original' | 'processed'
    mask_toggled = pyqtSignal(bool)  # True = show mask
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.view_mode = 'processed'  # Current mode
        self.mask_visible = False
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Before/After toggle button
        self.view_toggle_btn = QPushButton("Show Original", self)
        self.view_toggle_btn.setCheckable(True)
        self.view_toggle_btn.setToolTip("Toggle between original and processed image")
        self.view_toggle_btn.clicked.connect(self._on_view_toggle)
        layout.addWidget(self.view_toggle_btn)
        
        layout.addSpacing(16)
        
        # Mask toggle button  
        self.mask_btn = QPushButton("Show Mask", self)
        self.mask_btn.setCheckable(True)
        self.mask_btn.setToolTip("Toggle PHANTAST segmentation mask overlay")
        self.mask_btn.clicked.connect(self._on_mask_toggle)
        self.mask_btn.setEnabled(False)  # Disabled until mask available
        layout.addWidget(self.mask_btn)
        
        # Status label
        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
    def _on_view_toggle(self, checked: bool):
        """Handle before/after toggle."""
        if checked:
            self.view_mode = 'original'
            self.view_toggle_btn.setText("Show Processed")
        else:
            self.view_mode = 'processed'
            self.view_toggle_btn.setText("Show Original")
        self.view_mode_changed.emit(self.view_mode)
    
    def _on_mask_toggle(self, checked: bool):
        """Handle mask toggle."""
        self.mask_visible = checked
        self.mask_btn.setText("Hide Mask" if checked else "Show Mask")
        self.mask_toggled.emit(checked)
    
    def set_mask_available(self, available: bool):
        """Enable/disable mask button based on availability."""
        self.mask_btn.setEnabled(available)
        if not available:
            self.mask_btn.setChecked(False)
            self.mask_visible = False
            self.mask_btn.setText("Show Mask")
    
    def reset(self):
        """Reset to default state."""
        self.view_toggle_btn.setChecked(False)
        self.view_toggle_btn.setText("Show Original")
        self.view_mode = 'processed'
        self.mask_btn.setChecked(False)
        self.mask_btn.setText("Show Mask")
        self.mask_visible = False
        self.set_mask_available(False)
```

---

## Implementation Tasks

### Task 1: Modify PipelineWorker to Save Masks

**Files:** `src/core/pipeline_worker.py`

**What to do:**
1. Detect when PHANTAST step runs (check step name or type)
2. Save the binary mask as `{output_path}_mask.png` before converting to BGR
3. Emit new signal `mask_saved(source_path, mask_path)` 

**Code changes:**
```python
# Add signal to PipelineWorker
mask_generated = pyqtSignal(str, str)  # source_path, mask_path

# In process_pipeline(), after PHANTAST step:
if step_name == 'phantast' and processed_image is not None:
    # Save mask before converting to BGR
    mask_path = output_path.replace('.png', '_mask.png').replace('.jpg', '_mask.png')
    cv2.imwrite(mask_path, processed_image)
    self.mask_generated.emit(input_path, mask_path)
```

**Acceptance:**
- [ ] Mask file created when PHANTAST runs
- [ ] Mask path emitted via signal
- [ ] Original output still works correctly

---

### Task 2: Create ImageVariantManager Model

**Files:** `src/models/image_variants.py` (new)

**What to do:**
1. Create dataclass `ImageVariant` with path, type, source, step_name
2. Create `ImageVariantManager` class with dict storage
3. Add methods: add_variant, get_variants, get_variant, has_mask
4. Add unit tests

**Acceptance:**
- [ ] Model created and importable
- [ ] Unit tests pass
- [ ] Can store/retrieve variants

---

### Task 3: Enhance ImageCanvas with Overlay Support

**Files:** `src/ui/image_canvas.py`

**What to do:**
1. Add overlay_pixmap item in init (z-index above base, 50% opacity)
2. Add methods: set_overlay_image(), show_mask(), switch_base_image()
3. Track current_base_image path and overlay_mode state
4. Ensure overlay persists when zooming/panning

**Acceptance:**
- [ ] Overlay item renders above base image
- [ ] Opacity adjustable
- [ ] Overlay stays positioned correctly when zooming
- [ ] Overlay hides/shows on demand

---

### Task 4: Create ComparisonControls Widget

**Files:** `src/ui/comparison_controls.py` (new)

**What to do:**
1. Create QWidget subclass with horizontal layout
2. Add two toggle buttons: "Show Original/Processed", "Show/Hide Mask"
3. Emit signals: view_mode_changed, mask_toggled
4. Add methods: set_mask_available(), reset()
5. Style buttons to match app theme

**Acceptance:**
- [ ] Widget displays two buttons
- [ ] Toggle behavior works
- [ ] Signals emitted correctly
- [ ] Mask button enables/disables

---

### Task 5: Integrate into MainWindow

**Files:** `src/ui/main_window.py`

**What to do:**
1. Instantiate `ImageVariantManager` in setup_models()
2. Instantiate `ComparisonControls` in setup_ui_components() 
3. Place controls above or below image canvas
4. Connect signals:
   - `comparison_controls.view_mode_changed` → switch canvas base image
   - `comparison_controls.mask_toggled` → show/hide canvas overlay
   - `pipeline_executor.mask_generated` → register variant + enable mask button
5. Update `_handle_pipeline_finished()` to register processed variant
6. Reset controls when new image loaded

**Wire-up code:**
```python
def setup_models(self):
    # ... existing ...
    self.variant_manager = ImageVariantManager()

def setup_ui_components(self):
    # ... existing ...
    self.comparison_controls = ComparisonControls(parent=self.main_container)
    self.comparison_controls.setVisible(False)  # Hidden until mask available
    
    # Add to layout above canvas or in header
    # Connect signals
    self.comparison_controls.view_mode_changed.connect(self._on_view_mode_changed)
    self.comparison_controls.mask_toggled.connect(self._on_mask_toggled)

def wire_signals(self):
    # ... existing ...
    self.pipeline_executor.mask_generated.connect(self._on_mask_generated)

def _on_mask_generated(self, source_path: str, mask_path: str):
    """Handle mask generation from pipeline."""
    from src.models.image_variants import ImageVariant
    
    # Register mask variant
    self.variant_manager.add_variant(
        source_path, 
        ImageVariant(mask_path, 'mask', source_path, 'phantast')
    )
    
    # Enable mask button
    if source_path == self.current_image_path:
        self.comparison_controls.set_mask_available(True)
        self.comparison_controls.setVisible(True)

def _on_view_mode_changed(self, mode: str):
    """Switch between original and processed view."""
    source = self.current_image_path
    
    if mode == 'original':
        # Find original - might need to track this separately
        original = self.variant_manager.get_variant(source, 'original')
        if original:
            self.image_canvas.switch_base_image(original.path)
    else:
        # Show processed
        processed = self.variant_manager.get_variant(source, 'processed')
        if processed:
            self.image_canvas.switch_base_image(processed.path)

def _on_mask_toggled(self, show: bool):
    """Toggle mask overlay."""
    if show:
        source = self.current_image_path
        mask_variant = self.variant_manager.get_variant(source, 'mask')
        if mask_variant:
            # Load mask with green tint
            self.image_canvas.show_mask(True)
            self.image_canvas.set_overlay_image(mask_variant.path, opacity=0.4)
    else:
        self.image_canvas.show_mask(False)
```

**Acceptance:**
- [ ] Controls appear when mask generated
- [ ] View toggle switches images
- [ ] Mask toggle shows/hides overlay
- [ ] Controls reset on new image load

---

### Task 6: Track Original Image

**Files:** `src/ui/main_window.py`, `src/models/image_variants.py`

**What to do:**
1. When image first loaded, register it as 'original' variant
2. Track original path separately from current_image_path
3. Ensure before/after toggle can always find original

**Acceptance:**
- [ ] Original image registered as variant
- [ ] Can toggle back to original after processing

---

### Task 7: Add Mask Visualization (Green Overlay)

**Files:** `src/ui/image_canvas.py`

**What to do:**
1. When loading mask, convert to colored overlay (green for cells)
2. Apply transparency (40% opacity)
3. Ensure mask aligns with base image

**Code:**
```python
def set_overlay_image(self, image_path: Optional[str], opacity: float = 0.4):
    """Set mask overlay with green tint."""
    if image_path and os.path.exists(image_path):
        # Load mask and convert to green overlay
        mask = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if mask is not None:
            # Create green RGBA image
            h, w = mask.shape
            green_overlay = np.zeros((h, w, 4), dtype=np.uint8)
            green_overlay[mask > 0] = [0, 255, 0, 255]  # Green where mask is white
            
            # Convert to QPixmap
            qimage = QImage(green_overlay.data, w, h, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            
            self.overlay_pixmap.setPixmap(pixmap)
            self.overlay_pixmap.setOpacity(opacity)
            self.overlay_pixmap.setVisible(True)
    else:
        self.overlay_pixmap.setVisible(False)
```

**Acceptance:**
- [ ] Mask displays as green overlay
- [ ] Transparency works
- [ ] Aligns with base image

---

### Task 8: Integration Tests

**Files:** `tests/test_comparison_controls.py`, `tests/test_image_variants.py`

**What to do:**
1. Test ImageVariantManager add/get variants
2. Test ComparisonControls signals
3. Test ImageCanvas overlay functionality
4. Test end-to-end: run pipeline → mask saved → toggle works

**Acceptance:**
- [ ] All tests pass
- [ ] Coverage >80%

---

## UI/UX Specifications

### Button Placement
- Position comparison controls **below the canvas** or **in the floating toolbar**
- Keep controls hidden until a mask is available
- Show subtle animation when controls appear

### Visual Design
```css
/* Buttons should match app theme */
ComparisonControls {
    background: #1a1d21;
    border: 1px solid #2a2e33;
    border-radius: 8px;
}

QPushButton {
    background: #2a2e33;
    color: #E8EAED;
    border: 1px solid #3a3e43;
    border-radius: 4px;
    padding: 6px 12px;
}

QPushButton:checked {
    background: #00B884;  /* Accent green when active */
    border-color: #00d69a;
}

QPushButton:disabled {
    background: #1a1d21;
    color: #5a5e63;
}
```

### User Flow
```
1. User loads image
   ↓
2. User adds PHANTAST step to pipeline
   ↓
3. User clicks Run Pipeline
   ↓
4. Pipeline executes, mask saved as {image}_mask.png
   ↓
5. Comparison controls appear (slide in animation)
   ↓
6. User can:
      - Click "Show Original" to see before
      - Click "Show Processed" to see after  
      - Click "Show Mask" to toggle green overlay
   ↓
7. User loads new image → controls reset
```

---

## Commit Strategy

1. **Task 1-2**: Foundation
   - `feat(pipeline): save PHANTAST masks during processing`
   - `feat(models): add ImageVariantManager for tracking image variants`

2. **Task 3-4**: Core UI
   - `feat(canvas): add overlay support to ImageCanvas`
   - `feat(ui): create ComparisonControls widget`

3. **Task 5-7**: Integration
   - `feat(main): integrate comparison controls into main window`
   - `feat(canvas): add green mask overlay visualization`

4. **Task 8**: Tests
   - `test(comparison): add integration tests for mask overlay`

---

## Success Criteria

- [ ] PHANTAST mask auto-saves when pipeline runs
- [ ] "Show Original/Processed" toggle switches images instantly
- [ ] "Show/Hide Mask" toggle displays green overlay at 40% opacity
- [ ] Both toggles work independently (can show processed + mask)
- [ ] Controls only appear when mask is available
- [ ] Controls reset when new image loaded
- [ ] All tests pass
- [ ] No UI freeze or lag when toggling
- [ ] Mask aligns perfectly with base image
