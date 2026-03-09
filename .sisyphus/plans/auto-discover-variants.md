# Auto-Discover Existing Processed/Mask Images

## Overview
When loading an image, automatically search for and load existing `_processed` and `_mask` variants from the same directory.

## Problem
Currently when loading `80_-2.JPG`, the app doesn't check if `80_-2_processed.jpg` or `80_-2_mask.png` exist. User has to re-run pipeline to see comparison controls.

## Solution
Modify `MainWindow.load_image_to_canvas()` to:
1. After loading original image, search directory for variants
2. If found, set internal paths and show comparison controls
3. Load processed image by default (if available)
4. Set up mask overlay (if available)

## Implementation

### Task: Add Variant Discovery to Image Loading

**File:** `src/ui/main_window.py`

**What to do:**

1. **Modify `load_image_to_canvas()` method** (~line 938):
   - Add call to new `_discover_existing_variants()` method after loading image

2. **Add `_discover_existing_variants()` method**:
   ```python
   def _discover_existing_variants(self, filepath: str):
       """Search for existing _processed and _mask variants of the image."""
       import os
       
       directory = os.path.dirname(filepath)
       basename = os.path.splitext(os.path.basename(filepath))[0]
       ext = os.path.splitext(filepath)[1].lower()
       
       # Construct paths for potential variants
       processed_path = os.path.join(directory, f"{basename}_processed{ext}")
       mask_path = os.path.join(directory, f"{basename}_mask.png")
       
       found_any = False
       
       # Check for processed image
       if os.path.exists(processed_path):
           self._processed_image_path = processed_path
           found_any = True
       
       # Check for mask image
       if os.path.exists(mask_path):
           self._mask_image_path = mask_path
           self.image_canvas.set_overlay_image(mask_path)
           self.comparison_controls.set_mask_available(True)
           found_any = True
       
       # If we found variants, show comparison controls
       if found_any:
           self.comparison_controls.show()
           # Default to showing processed if available, otherwise original
           if self._processed_image_path:
               self.comparison_controls.set_view_mode('processed')
               self.image_canvas.load_image(self._processed_image_path)
               self.current_image_path = self._processed_image_path
           else:
               self.comparison_controls.set_view_mode('original')
   ```

**Acceptance Criteria:**
- [ ] When loading `80_-2.JPG`, app checks for `80_-2_processed.jpg` and `80_-2_mask.png`
- [ ] If processed exists, loads it by default and shows comparison controls
- [ ] If mask exists, enables mask toggle button
- [ ] If both exist, user can immediately toggle between views
- [ ] If no variants exist, behavior unchanged (no controls shown)

**QA Scenario:**
```
Scenario: Auto-discover existing variants
  Steps:
    1. Create test folder with: test.jpg, test_processed.jpg, test_mask.png
    2. Load test.jpg in app
    3. Verify comparison controls appear automatically
    4. Verify processed image loaded by default
    5. Verify mask toggle is enabled
    6. Toggle view modes - should work immediately
  Expected: Variants discovered and loaded without running pipeline
```

**Commit:**
- Message: `feat(main): auto-discover existing processed/mask variants on image load`
- Files: `src/ui/main_window.py`
