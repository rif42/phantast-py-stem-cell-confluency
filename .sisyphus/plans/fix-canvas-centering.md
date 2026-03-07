# Work Plan: Fix Canvas Centering Without Breaking Image View

## TL;DR
Fix the dashed border container to be centered in the canvas WITHOUT breaking image viewing functionality. Both image_canvas and empty_overlay need stretch=1, but empty_overlay needs proper layout spacers to center its content.

## The Problem
1. Original issue: Dashed border container was at bottom instead of centered
2. My incorrect fix: Removed stretch=1 from image_canvas 
3. Result: Image viewing is broken - canvas doesn't expand when image is loaded
4. Root cause: Both widgets need stretch, but empty_overlay needs proper centering via layout spacers

## The Correct Fix

### File: src/ui/main_window.py

**Step 1: Restore stretch to image_canvas**
Line ~183: Ensure `canvas_layout.addWidget(self.image_canvas, stretch=1)`

**Step 2: Add stretch spacers to empty_overlay layout**
The empty_overlay layout needs stretch spacers before and after the dashed_container to push it to center:

```python
# In empty_overlay setup (around line 185-242):
overlay_layout = QVBoxLayout(self.empty_overlay)
overlay_layout.setContentsMargins(16, 16, 16, 16)
overlay_layout.setSpacing(0)

# Add stretch before content
overlay_layout.addStretch(1)

# Add the dashed container (existing code)
overlay_layout.addWidget(
    dashed_container, stretch=0, alignment=Qt.AlignmentFlag.AlignCenter
)

# Add stretch after content  
overlay_layout.addStretch(1)
```

This way:
- Both image_canvas and empty_overlay have stretch=1 in the main canvas_layout
- When empty_overlay is visible, its internal layout uses stretch spacers to center the dashed container
- When empty_overlay is hidden, image_canvas takes all the space
- When image_canvas has an image, it displays properly

## Changes Required

### Change 1: Ensure image_canvas has stretch=1
```python
# Line ~183
# Should already be: canvas_layout.addWidget(self.image_canvas, stretch=1)
# If not, add stretch=1 back
```

### Change 2: Add stretch spacers to empty_overlay layout
```python
# In the empty_overlay setup section (lines ~188-242)
# BEFORE adding dashed_container:
overlay_layout.addStretch(1)

# ... add dashed_container ...

# AFTER adding dashed_container:
overlay_layout.addStretch(1)
```

### Change 3: Remove the explicit alignment from overlay_layout
```python
# Remove this line if present:
# overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
# The stretch spacers handle the centering now
```

## QA Criteria
1. Launch app - verify dashed border container is centered vertically and horizontally
2. Click "Open an Image" - verify file dialog opens
3. Select an image - verify image displays properly in full canvas area
4. Click "Open a Folder" - verify folder dialog opens  
5. Select a folder - verify folder contents are shown in file browser
6. Switch between images - verify canvas updates correctly

## Success Criteria
- [ ] Empty state: Dashed container centered in canvas
- [ ] Image loaded: Image displays full-size in canvas
- [ ] Folder mode: File browser visible in right panel
- [ ] No layout issues or overlapping widgets
