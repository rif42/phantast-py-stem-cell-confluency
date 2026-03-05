# Bug Investigation: Missing Floating Toolbar

## Problem Summary
The floating toolbar with pan, zoom, and ruler tools does not appear when loading an image in the main application (`src/`).

## Root Cause Analysis

### Prototype Implementation (WORKING - `shell/gui/image_viewer.py`)
The prototype `ImageViewer` class (lines 144-188) includes:
```python
# Overlay: Floating Toolbar (Top Center)
self.floating_toolbar = QWidget(self)
self.floating_toolbar.setFixedSize(300, 40)
self.floating_toolbar.setStyleSheet("...")
# ... toolbar buttons ...
self.floating_toolbar.hide()  # Hidden initially
```

And shows it when image is loaded (lines 218-223):
```python
def set_image(self, image: np.ndarray):
    if image is None:
        self.floating_toolbar.hide()
        return
    self.stack.setCurrentIndex(1)
    self.floating_toolbar.show()
```

### Main Implementation (MISSING - `src/ui/image_canvas.py`)
The `ImageCanvas` class in the main app has:
- ✅ Zoom/pan functionality (methods: `zoom_in()`, `zoom_out()`, `set_pan_mode()`)
- ✅ Mouse wheel zoom, click-and-drag panning
- ❌ **NO floating toolbar widget**
- ❌ **NO toolbar UI to activate tools**

### Integration Point
`UnifiedMainWidget` uses `ImageCanvas` directly (line 88-89):
```python
self.canvas = ImageCanvas(self.center_panel)
self.center_layout.addWidget(self.canvas)
```

Since `ImageCanvas` doesn't have the toolbar, nothing shows up.

## Toolbar Features in Prototype
- **Hand/Pan tool** (✋) - activates pan mode
- **Ruler tool** (📏) - for measurements
- **Pin tool** (📍) - for annotations/markers
- **Fit view** (⛶) - fits image to canvas
- **Zoom controls** (- 100% +) - shows current zoom level
- **Status label** (bottom right) - shows canvas dimensions

## Proposed Fix Options

### Option A: Add toolbar directly to ImageCanvas
Add the floating toolbar overlay to the existing `ImageCanvas` class, similar to the prototype implementation.

**Pros:**
- Self-contained widget
- Follows prototype pattern exactly
- Simple integration

**Cons:**
- `ImageCanvas` becomes more complex
- Mixed concerns (canvas + toolbar)

### Option B: Create wrapper widget
Create a new `ImageCanvasWithToolbar` widget that wraps `ImageCanvas` and adds the toolbar overlay.

**Pros:**
- Clean separation of concerns
- Canvas stays focused on display
- Easier to test independently

**Cons:**
- Additional wrapper class
- More files to modify

### Option C: Add to UnifiedMainWidget
Add the toolbar to the center panel layout in `UnifiedMainWidget` instead of inside `ImageCanvas`.

**Pros:**
- Keeps canvas simple
- Centralized in unified widget

**Cons:**
- Less reusable
- Breaks the component pattern

## Recommendation
**Option A** (Add toolbar to ImageCanvas) is recommended because:
1. It matches the working prototype pattern
2. The toolbar is logically part of the canvas interaction
3. Minimal changes required
4. Keeps the component self-contained

## Files to Modify
1. `src/ui/image_canvas.py` - Add floating toolbar with buttons
2. Potentially: `src/ui/unified_main_widget.py` - Hook into image loaded signal to show toolbar

## Verification
- Load an image → toolbar appears at top-center
- Clear image → toolbar hides
- Zoom buttons work
- Pan button toggles pan mode
- Zoom percentage updates
