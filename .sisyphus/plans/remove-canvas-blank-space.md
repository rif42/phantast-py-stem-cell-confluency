# Work Plan: Remove Blank Space in Canvas

## TL;DR
Fix the blank space between the floating toolbar and the "Select Input Image" section by giving the empty_overlay widget a stretch factor so it expands to fill the canvas area.

## Context
The main window canvas container has a vertical layout with:
1. `toolbar_container` (floating toolbar at top, with 16px top margin)
2. `image_canvas` (with `stretch=1`) 
3. `empty_overlay` (NO stretch - only takes minimum size)

The blank space occurs because `image_canvas` with `stretch=1` expands, but `empty_overlay` (containing the centered placeholder UI) only takes its minimum size and sits at the bottom of the layout.

## Work Objectives
- Remove blank space between toolbar and centered content
- Keep floating toolbar at top (remove its top margin since overlay will fill)
- Maintain current behavior when image is loaded (canvas displays image)

## Changes Required
**File**: `src/ui/main_window.py`

### Change 1: Remove top margin from toolbar_container
Line ~138: Change `toolbar_layout.setContentsMargins(0, 16, 0, 0)` to `toolbar_layout.setContentsMargins(0, 0, 0, 0)`

### Change 2: Add stretch to empty_overlay  
Line ~223: Change `canvas_layout.addWidget(self.empty_overlay)` to `canvas_layout.addWidget(self.empty_overlay, stretch=1)`

## QA Criteria
1. Launch application - verify toolbar is at very top (no margin)
2. Verify no blank space between toolbar and "Select Input Image" section
3. Click "Open an Image" button - verify it's clickable
4. Click "Open a Folder" button - verify it's clickable
5. Load an image - verify image displays correctly in canvas
6. Verify zoom controls still work on loaded image

## Verification Command
```bash
cd D:\work\phantast-py-stem-cell-confluency && python src/main.py
```

## Success Criteria
- [ ] Toolbar touches top edge (no gap)
- [ ] "Select Input Image" section centered vertically in available space (no blank space above it)
- [ ] Buttons remain functional
- [ ] Image loading still works correctly
