# Mask Overlay & Comparison Feature - Simplified Implementation Plan

## Overview
Add before/after toggle and mask overlay for PHANTAST segmentation results. **Simplified approach** with overwrite mode, single PHANTAST node constraint, and modal blocking during processing.

## Constraints
1. **Overwrite mode**: New processing replaces old variants (no history)
2. **Single PHANTAST node**: UI enforces only one PHANTAST step in pipeline
3. **Base name matching**: Use first name (e.g., "cells" from "cells.jpg")
4. **Modal blocking**: "Processing" dialog blocks all interaction during pipeline execution

---

## TL;DR

> **Quick Summary**: Add mask overlay visualization with before/after toggle for PHANTAST results. When user runs pipeline with PHANTAST node, save mask file and enable toggle buttons to switch views.
>
> **Deliverables**:
> - Mask saving in PipelineWorker
> - Enhanced ImageCanvas with overlay support
> - ComparisonControls widget (2 toggle buttons)
> - Modal ProcessingDialog during execution
> - MainWindow integration
>
> **Estimated Effort**: Short (~2-3 hours)
> **Parallel Execution**: NO - 4 sequential tasks
> **Critical Path**: Task 1 → Task 2 → Task 3 → Task 4

---

## Context

### Original Request
User runs PHANTAST pipeline and wants to:
- Toggle between original and processed images
- Show/hide segmentation mask with green overlay (40% opacity)
- View combinations (e.g., processed + mask overlay)

### Simplified Design Decisions
- No variant history (overwrite old results)
- One PHANTAST node maximum (prevents ambiguity)
- Block UI during processing (eliminates race conditions)
- Simple base name matching for file relationships

---

## Work Objectives

### Core Objective
Enable users to visually compare PHANTAST segmentation results with mask overlay toggle.

### Concrete Deliverables
1. `{basename}_mask.png` saved alongside processed image
2. "Original | Processed" toggle button
3. "Show Mask" toggle button with green overlay (40% opacity)
4. Modal "Processing" dialog blocking interaction during execution

### Definition of Done
- [ ] Run pipeline with PHANTAST → mask file created
- [ ] Toggle buttons appear after processing completes
- [ ] "Original | Processed" switches base image
- [ ] "Show Mask" toggles green overlay on/off
- [ ] Processing modal blocks all clicks during execution
- [ ] Toggle buttons hidden when no mask available

### Must Have
- Green mask overlay (RGB: 0, 255, 0, 102 alpha)
- Toggle states persist during session
- Buttons disable appropriately (e.g., no mask = show mask disabled)

### Must NOT Have (Guardrails)
- NO multiple PHANTAST nodes support
- NO mask history/versioning
- NO async UI updates (modal blocking only)
- NO per-image state persistence across sessions

---

## Execution Strategy

### Sequential Execution (No Parallelism)

```
Task 1: Modify PipelineWorker to save masks
        ↓
Task 2: Enhance ImageCanvas with overlay support
        ↓
Task 3: Create ComparisonControls widget
        ↓
Task 4: Integrate into MainWindow with modal dialog
```

**Why sequential:**
- Task 2 depends on Task 1 (mask file format)
- Task 3 depends on Task 2 (canvas API)
- Task 4 depends on all previous (wiring everything)

---

## TODOs

- [ ] 1. Modify PipelineWorker to Save Masks

  **What to do**:
  - In `src/core/pipeline_worker.py`, modify `process_pipeline()` to detect PHANTAST steps
  - When PHANTAST step completes, save mask to `{output_dir}/{base_name}_mask.png`
  - Generate green RGBA overlay: convert binary mask to green with 40% opacity
  - Emit signal: `mask_saved(source_path, mask_path)` after successful save
  - Return mask path in worker results

  **Base name extraction**:
  ```python
  def get_base_name(filepath: str) -> str:
      name = os.path.splitext(os.path.basename(filepath))[0]
      if name.endswith('_processed'):
          name = name[:-10]
      return name
  ```

  **Green overlay creation**:
  ```python
  def create_green_mask_overlay(binary_mask: np.ndarray) -> np.ndarray:
      h, w = binary_mask.shape
      rgba = np.zeros((h, w, 4), dtype=np.uint8)
      rgba[binary_mask > 0] = [0, 255, 0, 102]  # Green, 40% opacity
      return rgba
  ```

  **Must NOT do**:
  - Do NOT save intermediate masks from multiple PHANTAST nodes (we enforce single node)
  - Do NOT use cv2.imwrite for mask (we need RGBA overlay, not binary)
  - Do NOT proceed if mask save fails (log error and continue without mask)

  **References**:
  - `src/core/pipeline_worker.py:40-70` - process_pipeline method
  - `src/core/steps/phantast_step.py:401-427` - PHANTAST returns (confluency, mask)
  - Python `os.path` documentation for path manipulation

  **Acceptance Criteria**:
  - [ ] Mask file saved as `{base_name}_mask.png` alongside processed image
  - [ ] Mask is green RGBA with 40% opacity (visually correct)
  - [ ] `mask_saved` signal emitted after save
  - [ ] Processing continues even if mask save fails (graceful degradation)

  **QA Scenario**:
  ```
  Scenario: PHANTAST pipeline saves mask
    Tool: Python direct test
    Steps:
      1. Create test image "test.jpg"
      2. Run pipeline with PHANTAST node
      3. Check "test_mask.png" exists
      4. Load mask and verify green color, 40% opacity
    Expected: Mask file exists with correct visual properties
    Evidence: .sisyphus/evidence/task-1-mask-saved.png
  ```

  **Commit**: YES
  - Message: `feat(pipeline): save PHANTAST mask as green overlay`
  - Files: `src/core/pipeline_worker.py`

- [ ] 2. Enhance ImageCanvas with Overlay Support

  **What to do**:
  - In `src/ui/image_canvas.py`, add overlay support:
    - Add `self.overlay_item: QGraphicsPixmapItem` (z-index 10)
    - Add `set_overlay_image(mask_path: str)` method
    - Add `show_overlay(visible: bool)` method
    - Add `has_overlay() -> bool` method
  - Ensure overlay doesn't intercept mouse events:
    - `self.overlay_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)`
  - Ensure overlay aligns with base image (same position/scale)
  - Handle overlay visibility independently from base image

  **Must NOT do**:
  - Do NOT make overlay interactive (breaks pan/zoom)
  - Do NOT auto-show overlay when set (let caller control visibility)
  - Do NOT assume overlay matches base image size (check dimensions)

  **References**:
  - `src/ui/image_canvas.py:1-50` - Current ImageCanvas implementation
  - PyQt6 `QGraphicsPixmapItem` documentation
  - `QGraphicsItem.GraphicsItemFlag.ItemDoesntPropagateOpacityToChildren`

  **Acceptance Criteria**:
  - [ ] Overlay item created at z-index 10
  - [ ] `set_overlay_image()` loads and displays mask
  - [ ] `show_overlay()` toggles visibility without affecting base image
  - [ ] Overlay doesn't intercept mouse events
  - [ ] Overlay aligned with base image

  **QA Scenario**:
  ```
  Scenario: Toggle overlay visibility
    Tool: pytest-qt
    Steps:
      1. Load base image to canvas
      2. Set overlay image
      3. Verify overlay is hidden by default
      4. Call show_overlay(True)
      5. Verify overlay visible
      6. Call show_overlay(False)
      7. Verify overlay hidden, base image still visible
    Expected: Overlay toggles independently
    Evidence: .sisyphus/evidence/task-2-overlay-toggle.gif
  ```

  **Commit**: YES
  - Message: `feat(canvas): add mask overlay support to ImageCanvas`
  - Files: `src/ui/image_canvas.py`

- [ ] 3. Create ComparisonControls Widget

  **What to do**:
  - Create new file `src/ui/comparison_controls.py`
  - Implement `ComparisonControls` class (QWidget):
    - "Original | Processed" toggle button (QPushButton with checkable state or two-button group)
    - "Show Mask" toggle button (QPushButton, checkable, disabled when no mask)
  - Define signals:
    - `view_mode_changed(mode: str)`  # 'original' or 'processed'
    - `mask_visibility_changed(visible: bool)`
  - Add methods:
    - `set_mask_available(available: bool)` - enables/disables mask button
    - `set_view_mode(mode: str)` - sets original/processed toggle
    - `reset()` - hides widget, resets to defaults
  - Style buttons to match app theme (dark background, green accent)
  - Hide widget by default (show only when mask available)

  **Must NOT do**:
  - Do NOT show widget before mask is available
  - Do NOT allow mask toggle when no mask (keep button disabled)
  - Do NOT use external images for icons (use text or QtAwesome if available)

  **References**:
  - `src/ui/main_window.py` - Theme colors and styling patterns
  - PyQt6 `QPushButton`, `QButtonGroup`, `QHBoxLayout`
  - Existing button styling in `src/ui/pipeline_stack_widget.py`

  **Acceptance Criteria**:
  - [ ] Widget has two toggle buttons
  - [ ] Signals emitted on toggle changes
  - [ ] Mask button disabled when `set_mask_available(False)`
  - [ ] Widget hidden by default, shown via `show()`
  - [ ] Styling matches app theme

  **QA Scenario**:
  ```
  Scenario: Control states
    Tool: pytest-qt
    Steps:
      1. Create ComparisonControls
      2. Verify mask button disabled initially
      3. Call set_mask_available(True)
      4. Verify mask button enabled
      5. Toggle view mode, verify signal emitted
      6. Toggle mask, verify signal emitted
    Expected: All states and signals work correctly
    Evidence: .sisyphus/evidence/task-3-control-states.txt
  ```

  **Commit**: YES
  - Message: `feat(ui): add ComparisonControls widget for before/after toggle`
  - Files: `src/ui/comparison_controls.py`

- [ ] 4. Integrate into MainWindow with Modal Processing Dialog

  **What to do**:
  - In `src/ui/main_window.py`:
    - Import `ComparisonControls` and `ProcessingDialog` (create simple modal dialog)
    - Create `ProcessingDialog` class (QDialog with spinner and "Processing..." text)
    - Add `self.comparison_controls` below canvas in layout
    - Connect pipeline signals:
      - `started` → show ProcessingDialog (modal, blocks all clicks)
      - `finished` → hide ProcessingDialog, show comparison controls
      - `mask_saved` → enable mask button in comparison controls
    - Implement handlers:
      - `_on_view_mode_changed(mode)` - switch base image
      - `_on_mask_visibility_changed(visible)` - toggle overlay
    - Track original image path separately:
      - `self._original_image_path: str` (set when loading, never changes)
      - `self._processed_image_path: str` (set after processing)
      - `self._mask_image_path: str` (set when mask saved)
    - Enforce single PHANTAST node:
      - In `handle_add_step()`, check if PHANTAST already exists
      - Show error if user tries to add second PHANTAST node

  **ProcessingDialog implementation**:
  ```python
  class ProcessingDialog(QDialog):
      def __init__(self, parent=None):
          super().__init__(parent)
          self.setWindowTitle("Processing")
          self.setModal(True)
          self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
          # Add spinner label and "Processing..." text
          # Center on parent
  ```

  **View mode switching**:
  ```python
  def _on_view_mode_changed(self, mode: str):
      if mode == 'original':
          self.image_canvas.load_image(self._original_image_path)
      else:
          self.image_canvas.load_image(self._processed_image_path)
      # Preserve overlay visibility state
  ```

  **Must NOT do**:
  - Do NOT allow non-modal processing (must block all clicks)
  - Do NOT show comparison controls before processing completes
  - Do NOT allow multiple PHANTAST nodes (enforce constraint)

  **References**:
  - `src/ui/main_window.py:400-500` - Signal wiring and handlers
  - `src/ui/main_window.py:350-380` - handle_add_step method
  - PyQt6 `QDialog`, `QProgressDialog` documentation

  **Acceptance Criteria**:
  - [ ] ProcessingDialog shown during pipeline execution (modal)
  - [ ] Dialog blocks all clicks on main window
  - [ ] ComparisonControls shown after processing completes
  - [ ] View mode toggle switches between original/processed
  - [ ] Mask toggle shows/hides overlay
  - [ ] Only one PHANTAST node allowed in pipeline
  - [ ] State resets when loading new image

  **QA Scenarios**:
  ```
  Scenario: Modal processing dialog
    Tool: pytest-qt
    Steps:
      1. Start pipeline
      2. Verify ProcessingDialog is visible and modal
      3. Try to click main window (should be blocked)
      4. Wait for completion
      5. Verify dialog closed, comparison controls visible
    Expected: Modal blocking works, controls appear after
    Evidence: .sisyphus/evidence/task-4-modal-dialog.gif

  Scenario: Single PHANTAST enforcement
    Tool: pytest-qt
    Steps:
      1. Add PHANTAST node to pipeline
      2. Try to add second PHANTAST node
      3. Verify error message shown
      4. Verify second node not added
    Expected: Constraint enforced
    Evidence: .sisyphus/evidence/task-4-single-phantast.png
  ```

  **Commit**: YES
  - Message: `feat(main): integrate comparison controls and modal processing`
  - Files: `src/ui/main_window.py`

---

## Final Verification Wave

- [ ] F1. **End-to-End Integration Test**
  
  **What to verify**:
  1. Load "cells.jpg"
  2. Add PHANTAST node to pipeline
  3. Click Run Pipeline
  4. Verify ProcessingDialog appears (modal)
  5. Wait for completion
  6. Verify "cells_processed.jpg" and "cells_mask.png" exist
  7. Verify comparison controls visible
  8. Toggle "Original | Processed" - verify image switches
  9. Toggle "Show Mask" - verify green overlay appears
  10. Load new image - verify controls reset/hidden
  
  **Tool**: pytest-qt + manual verification
  **Expected**: All toggles work, mask overlay visible
  **Evidence**: `.sisyphus/evidence/integration-test.gif`

- [ ] F2. **Edge Case Testing**
  
  **What to verify**:
  - Try to add second PHANTAST node → error shown
  - Run pipeline without PHANTAST → no mask, controls hidden
  - Toggle mask off, switch to original, switch back to processed → mask still off
  - Delete mask file externally → graceful handling
  
  **Tool**: pytest-qt
  **Expected**: All edge cases handled gracefully
  **Evidence**: `.sisyphus/evidence/edge-cases.txt`

---

## Commit Strategy

- **Task 1**: `feat(pipeline): save PHANTAST mask as green overlay`
- **Task 2**: `feat(canvas): add mask overlay support to ImageCanvas`
- **Task 3**: `feat(ui): add ComparisonControls widget`
- **Task 4**: `feat(main): integrate comparison controls and modal processing`

---

## Success Criteria

### Verification Commands
```bash
# Run all tests
pytest tests/ -v

# Run specific comparison tests
pytest tests/test_comparison_controls.py -v

# Manual verification
python src/main.py
# 1. Load image
# 2. Add PHANTAST step
# 3. Run pipeline
# 4. Toggle before/after
# 5. Toggle mask overlay
```

### Final Checklist
- [ ] Mask file created with green overlay (40% opacity)
- [ ] Processing modal blocks all clicks during execution
- [ ] Comparison controls appear after processing
- [ ] Original/Processed toggle switches images
- [ ] Show Mask toggle shows/hides overlay
- [ ] Only one PHANTAST node allowed
- [ ] Controls reset when loading new image
- [ ] All tests pass
