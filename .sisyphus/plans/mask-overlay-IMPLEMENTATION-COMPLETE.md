# Mask Overlay & Comparison Feature - Implementation Complete

## Summary

All 4 tasks completed successfully. Users can now toggle between original/processed images and show/hide PHANTAST segmentation masks with green overlay.

## Commit History

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | - | PipelineWorker saves PHANTAST masks as green overlay PNGs |
| Task 2 | `6b2efb2` | ImageCanvas supports overlay display with z-index layering |
| Task 3 | `cc99282` | ComparisonControls widget with toggle buttons |
| Task 4 | `3df79bb` | MainWindow integration with modal ProcessingDialog |

## What Was Built

### 1. Mask Saving (PipelineWorker)
- Saves PHANTAST mask as `{base_name}_mask.png` with green RGBA overlay (0, 255, 0, 102)
- Emits `mask_saved` signal after successful save
- Graceful error handling (logs failure, continues processing)

### 2. Canvas Overlay (ImageCanvas)
- `overlay_item` at z-index 10 (above base image at z-index 0)
- Non-interactive (doesn't break pan/zoom)
- `set_overlay_image()`, `show_overlay()`, `has_overlay()`, `clear_overlay()` methods
- Auto-clears when loading new image

### 3. Comparison Controls (ComparisonControls)
- "Original | Processed" toggle button
- "Show Mask" toggle button (disabled until mask available)
- Signals: `view_mode_changed`, `mask_visibility_changed`
- Dark theme styling matching app

### 4. MainWindow Integration
- **ProcessingDialog**: Modal blocking dialog with spinner during execution
- **Image path tracking**: Separate tracking for original, processed, mask
- **View toggle**: Switches between original and processed images
- **Mask toggle**: Shows/hides green overlay
- **Single PHANTAST enforcement**: Error if user tries to add second node
- **Reset on new image**: Controls hide when loading different image

## How It Works

```
1. User loads "cells.jpg"
2. User adds PHANTAST node to pipeline
3. User clicks "Run Pipeline"
4. [MODAL DIALOG APPEARS - "Processing..." with spinner]
5. Pipeline executes:
   - PHANTAST step saves mask as "cells_mask.png" (green overlay)
   - Processed image saved as "cells_processed.jpg"
6. [DIALOG CLOSES]
7. Comparison controls appear below canvas:
   
   [Original | Processed]    [Show Mask ☐]
   
8. User can now:
   - Toggle Original/Processed to compare images
   - Toggle Show Mask to overlay green segmentation
```

## Files Modified/Created

- `src/core/pipeline_worker.py` - Mask saving logic
- `src/ui/image_canvas.py` - Overlay support
- `src/ui/comparison_controls.py` - NEW: Toggle buttons widget
- `src/ui/main_window.py` - Integration and modal dialog

## Verification

All tasks verified:
- ✅ LSP diagnostics clean
- ✅ Syntax/build checks passed
- ✅ Component functionality tested

## Usage

```bash
python src/main.py

# 1. Load an image
# 2. Add PHANTAST step to pipeline
# 3. Click "Run Pipeline"
# 4. Wait for modal dialog to close
# 5. Use toggle buttons to compare and view mask
```
