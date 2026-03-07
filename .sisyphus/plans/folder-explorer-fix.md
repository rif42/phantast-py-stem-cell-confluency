# Folder Explorer Fix - Right Sidebar Enhancement

## TL;DR

> **Quick Summary**: Add a folder explorer view to the right sidebar that shows all image files in the currently opened folder, with click-to-load functionality, refresh capability, and green selection highlighting.
>
> **Deliverables**:
> - Folder explorer widget in right sidebar metadata page
> - File list with green border on selected item
> - Refresh button to re-scan folder
> - Integration with existing image loading pipeline
>
> **Estimated Effort**: Quick (2-3 tasks)
> **Parallel Execution**: NO - Sequential dependencies
> **Critical Path**: Task 1 → Task 2 → Task 3

---

## Context

### Original Request
When clicking "Open Folder", the image shows on the main canvas, but the right sidebar only shows image metadata. There should be a folder explorer view in the top right corner showing all images in the folder.

### Requirements Confirmed
1. **Show ALL image files** in the folder (all extensions)
2. **Click on file** → immediately loads that image in main canvas
3. **Always visible** when in folder mode, expands dynamically
4. **Image metadata must still show** below the folder explorer
5. **Add refresh button** to re-scan folder
6. **Selected image** must have green border around the item in the list

### Technical Architecture
- **Main Window**: Uses `UnifiedRightPanel` for right sidebar (currently has NO folder explorer)
- **Controller**: `ImageController` already calls `view.update_file_list(files)` when folder opens
- **Existing Implementation**: `ImageNavigationWidget` in `image_navigation.py` has complete folder explorer code, but it's NOT being used by `MainWindow`
- **The Bug**: `MainWindow.update_file_list()` is a stub that does nothing (`pass`)

### Metis Review Findings
**Identified Gaps** (addressed in plan):
- Missing QListWidget performance settings (`setUniformItemSizes`)
- Signal choice needed: use `itemDoubleClicked` for loading
- Exact CSS syntax for green border (`QListWidget::item:selected`)
- Refresh button behavior specification
- Empty state handling
- Scope lock-down: NO file icons, NO sorting, NO filtering, NO thumbnails

---

## Work Objectives

### Core Objective
Implement a folder explorer widget in the right sidebar that displays all image files in the currently opened folder, allows users to select and load images, and refreshes on demand.

### Concrete Deliverables
- Modified `src/ui/unified_right_panel.py` with folder explorer QListWidget
- Modified `src/ui/main_window.py` with delegation to right panel
- Updated `src/controllers/image_controller.py` with file selection handler
- CSS styling for green selected item border
- Working integration: folder open → list populates → click → image loads

### Definition of Done
- [ ] Click "Open Folder" → folder explorer shows all image files
- [ ] Click on file in list → image loads immediately on canvas
- [ ] Selected file has green border (#00B884) in list
- [ ] Click refresh button → list updates
- [ ] Metadata section still shows below folder explorer
- [ ] Empty folder shows "No images found" message

### Must Have
- [x] QListWidget in metadata page of UnifiedRightPanel
- [x] File list populates when folder opens
- [x] Double-click loads image
- [x] Green border on selected item
- [x] Refresh button functionality
- [x] Empty state handling

### Must NOT Have (Guardrails)
- NO file icons (text-only list)
- NO sorting capabilities (default alphabetical)
- NO filtering (show all files)
- NO thumbnails (text list only)
- NO context menus
- NO drag-drop reordering
- NO file system tree/navigation
- NO breadcrumb path display

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest, pytest-qt)
- **Automated tests**: YES (Tests after implementation)
- **Framework**: pytest + pytest-qt
- **Test approach**: Each task verified via pytest-qt after completion

### QA Policy
Every task includes agent-executed QA scenarios with evidence capture to `.sisyphus/evidence/`.

---

## Execution Strategy

### Sequential Execution (NO Parallelism)

This work requires sequential execution due to tight coupling:

```
Task 1: Add folder explorer widget to UnifiedRightPanel (FOUNDATION)
         ↓
Task 2: Wire MainWindow to delegate to right panel (INTEGRATION)
         ↓
Task 3: Add controller handler and finalize integration (COMPLETION)
```

**Why Sequential**: Task 2 depends on Task 1's `file_list` widget existing. Task 3 depends on Task 2's signal wiring.

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> Every task MUST have: Recommended Agent Profile + QA Scenarios.
> **A task WITHOUT QA Scenarios is INCOMPLETE. No exceptions.**

- [ ] 1. Add folder explorer widget to UnifiedRightPanel

  **What to do**:
  - Add `file_list` (QListWidget) to metadata page in `UnifiedRightPanel`
  - Add refresh button (QPushButton with ↻ icon) in folder header row
  - Add `update_file_list(files)` method to populate the list
  - Add `file_selected = pyqtSignal(str)` signal for file selection
  - Connect `itemDoubleClicked` signal to emit `file_selected`
  - Add empty state: show "No images found" label when list is empty
  - Configure performance: `setUniformItemSizes(True)`, `setLayoutMode(Batched)`, `setBatchSize(100)`
  - Ensure ALL widgets have proper parent assignment (prevent window spawning)

  **Must NOT do**:
  - NO file icons (text-only list)
  - NO sorting capabilities
  - NO filtering
  - NO thumbnails
  - NO context menus
  - NO drag-drop reordering

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI widget creation and layout in PyQt6
  - **Skills**: []
    - No special skills needed for this PyQt6 widget work
  - **Skills Evaluated but Omitted**:
    - None applicable

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential - Task 1 must complete before Task 2
  - **Blocks**: Task 2, Task 3
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `src/ui/image_navigation.py:292-306` - Folder explorer widget creation pattern
  - `src/ui/image_navigation.py:399-405` - `update_file_list()` implementation
  - `src/ui/unified_right_panel.py:1-100` - Metadata page structure and styling

  **API/Type References** (contracts to implement against):
  - `PyQt6.QtWidgets.QListWidget` - File list widget API
  - `PyQt6.QtCore.pyqtSignal(str)` - Signal for file selection

  **External References** (libraries and frameworks):
  - PyQt6 QListWidget docs: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QListWidget.html

  **WHY Each Reference Matters**:
  - `image_navigation.py:292-306` - Shows exact pattern for creating folder explorer with proper parent assignment and layout
  - `image_navigation.py:399-405` - Shows how to populate list, handle empty state, and maintain selection
  - `unified_right_panel.py` - Shows existing metadata page structure where folder explorer should be inserted

  **Acceptance Criteria**:

  **Code Changes**:
  - [ ] `file_list` QListWidget added to metadata page layout (top section, above metadata)
  - [ ] Refresh button added to folder header row
  - [ ] `update_file_list(files)` method implemented
  - [ ] `file_selected = pyqtSignal(str)` signal defined
  - [ ] `itemDoubleClicked` connected to emit `file_selected` with file path
  - [ ] Empty state label shows when `len(files) == 0`
  - [ ] Performance settings applied: `setUniformItemSizes(True)`, `setBatchSize(100)`

  **Test Changes**:
  - [ ] Test file created: `tests/test_folder_explorer.py`
  - [ ] Test: `test_folder_explorer_widget_exists` - verifies QListWidget is created
  - [ ] Test: `test_update_file_list_populates` - verifies list populates with files
  - [ ] Test: `test_empty_folder_shows_message` - verifies empty state

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Folder explorer widget created with proper parent
    Tool: Bash (python REPL)
    Preconditions: None
    Steps:
      1. Import UnifiedRightPanel from src.ui.unified_right_panel
      2. Create QApplication instance
      3. panel = UnifiedRightPanel()
      4. Check panel.file_list exists and is QListWidget
      5. Check panel.file_list.parent() is not None
    Expected Result: file_list exists, is QListWidget, has parent widget
    Failure Indicators: AttributeError (file_list missing), parent() returns None
    Evidence: .sisyphus/evidence/task-1-widget-creation.txt

  Scenario: Folder list populates with files
    Tool: Bash (python REPL)
    Preconditions: Test folder with 3 images exists
    Steps:
      1. Create panel = UnifiedRightPanel()
      2. Call panel.update_file_list(["/path/to/img1.png", "/path/to/img2.jpg", "/path/to/img3.tiff"])
      3. Check panel.file_list.count() == 3
      4. Check panel.file_list.item(0).text() == "img1.png"
    Expected Result: QListWidget shows 3 items with filenames
    Failure Indicators: count() != 3, item text doesn't match filename
    Evidence: .sisyphus/evidence/task-1-populate-list.txt

  Scenario: Empty folder shows "No images found"
    Tool: Bash (python REPL)
    Preconditions: None
    Steps:
      1. Create panel = UnifiedRightPanel()
      2. Call panel.update_file_list([])
      3. Check empty state label is visible
      4. Check file_list is hidden or empty
    Expected Result: Empty state message displayed, file list hidden
    Failure Indicators: No empty state visible, file_list still showing
    Evidence: .sisyphus/evidence/task-1-empty-state.txt
  ```

  **Evidence to Capture**:
  - [ ] Screenshot of folder explorer widget in right panel (if UI visible)
  - [ ] Terminal output from pytest showing tests pass
  - [ ] Evidence files: task-1-widget-creation.txt, task-1-populate-list.txt, task-1-empty-state.txt

  **Commit**: YES
  - Message: `feat(ui): add folder explorer widget to right sidebar`
  - Files: `src/ui/unified_right_panel.py`, `tests/test_folder_explorer.py`
  - Pre-commit: `pytest tests/test_folder_explorer.py -v`

- [ ] 2. Wire MainWindow delegation for folder list updates

  **What to do**:
  - Modify `MainWindow.update_file_list(files)` to delegate to `self.right_panel.update_file_list(files)`
  - Connect `self.right_panel.file_selected` signal to `self.image_controller.handle_file_selected`
  - Ensure this happens in `MainWindow.wire_signals()` method
  - Verify the stub method is removed/replaced with actual delegation

  **Must NOT do**:
  - NO direct model access from MainWindow (use controller)
  - NO duplicate signal connections
  - NO changes to folder explorer widget itself (handled in Task 1)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple delegation wiring, minimal logic
  - **Skills**: []
  - **Skills Evaluated but Omitted**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 3
  - **Blocked By**: Task 1 (right_panel must have update_file_list method)

  **References**:

  **Pattern References**:
  - `src/ui/main_window.py:457-459` - Current stub `update_file_list()` that does nothing
  - `src/ui/main_window.py:180-200` - `wire_signals()` method pattern
  - `src/controllers/image_controller.py:45-52` - `_update_view_from_model()` calls view.update_file_list()

  **API/Type References**:
  - `UnifiedRightPanel.update_file_list(files)` - Method added in Task 1
  - `UnifiedRightPanel.file_selected` - Signal added in Task 1

  **WHY Each Reference Matters**:
  - `main_window.py:457-459` - Shows current stub that must be replaced
  - `main_window.py:180-200` - Shows existing signal wiring pattern to follow
  - `image_controller.py:45-52` - Shows the flow that triggers update_file_list

  **Acceptance Criteria**:

  **Code Changes**:
  - [ ] `MainWindow.update_file_list(files)` calls `self.right_panel.update_file_list(files)`
  - [ ] `MainWindow.wire_signals()` connects `right_panel.file_selected` to controller
  - [ ] No `pass` statement remains in update_file_list

  **Test Changes**:
  - [ ] Test: `test_main_window_delegates_to_right_panel` - verifies delegation works

  **QA Scenarios**:

  ```
  Scenario: MainWindow delegates update_file_list to right panel
    Tool: Bash (pytest)
    Preconditions: Task 1 complete (right_panel has update_file_list)
    Steps:
      1. Mock right_panel.update_file_list
      2. Call main_window.update_file_list(["/path/to/test.png"])
      3. Verify mock was called with correct argument
    Expected Result: right_panel.update_file_list called with ["/path/to/test.png"]
    Failure Indicators: Mock not called, stub still present
    Evidence: .sisyphus/evidence/task-2-delegation.txt

  Scenario: File selection signal is wired to controller
    Tool: Bash (python REPL)
    Preconditions: Task 1 complete
    Steps:
      1. Create MainWindow instance
      2. Check right_panel.file_selected is connected to controller
      3. Emit signal and verify controller receives it
    Expected Result: Signal properly connected and routed
    Failure Indicators: Signal not connected, controller doesn't receive
    Evidence: .sisyphus/evidence/task-2-signal-wiring.txt
  ```

  **Evidence to Capture**:
  - [ ] Terminal output showing delegation test passes
  - [ ] Evidence files: task-2-delegation.txt, task-2-signal-wiring.txt

  **Commit**: YES
  - Message: `feat(ui): wire MainWindow delegation for folder list updates`
  - Files: `src/ui/main_window.py`
  - Pre-commit: `pytest tests/test_folder_explorer.py -v`

- [ ] 3. Add controller handler and finalize integration

  **What to do**:
  - Add `handle_file_selected(file_path)` method to `ImageController`
  - Method should load the selected image: `model.load_image(file_path)`
  - Update view from model after loading: `_update_view_from_model()`
  - Ensure green border styling works on selected QListWidget item
  - Add CSS styling to `MainWindow.apply_styles()` for `#fileList::item:selected`

  **Must NOT do**:
  - NO blocking/synchronous file loading (use existing async pattern if exists)
  - NO error swallowing (log and show error if image fails to load)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple handler method and CSS styling
  - **Skills**: []
  - **Skills Evaluated but Omitted**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: None (final task)
  - **Blocked By**: Task 2 (signal must be wired first)

  **References**:

  **Pattern References**:
  - `src/controllers/image_controller.py:35-42` - `handle_open_image()` pattern
  - `src/ui/main_window.py:80-120` - `apply_styles()` method with CSS
  - `src/ui/main_window.py:20-30` - Theme colors (ACCENT = "#00B884")

  **API/Type References**:
  - `ImageSessionModel.load_image(file_path)` - Load image method
  - `ImageController._update_view_from_model()` - Refresh view

  **External References**:
  - Qt Stylesheet Reference: https://doc.qt.io/qt-6/stylesheet-examples.html#customizing-qlistwidget

  **WHY Each Reference Matters**:
  - `image_controller.py:35-42` - Shows pattern for handling file selection
  - `main_window.py:80-120` - Shows where to add CSS styling for selected items
  - Theme colors - Must use #00B884 for green border to match theme

  **Acceptance Criteria**:

  **Code Changes**:
  - [ ] `ImageController.handle_file_selected(file_path)` method implemented
  - [ ] CSS added to `apply_styles()`:
    ```css
    #fileList::item {
        border: 2px solid transparent;
        padding: 8px 12px;
    }
    #fileList::item:selected {
        background-color: #00B884;
        border: 2px solid #00d69a;
        color: #121415;
    }
    ```
  - [ ] Green border visible on selected item in folder explorer

  **Test Changes**:
  - [ ] Test: `test_file_double_click_loads_image` - verifies double-click loads image
  - [ ] Test: `test_selected_item_has_green_border` - verifies CSS styling

  **QA Scenarios**:

  ```
  Scenario: Double-click on file loads image on canvas
    Tool: interactive_bash (tmux) with pytest-qt
    Preconditions: Folder with images opened
    Steps:
      1. Open folder with test images
      2. Double-click on file in folder explorer
      3. Verify ImageController.handle_file_selected called
      4. Verify model.current_image updated
      5. Verify canvas shows new image
    Expected Result: Image loads on canvas immediately
    Failure Indicators: Image doesn't load, handler not called
    Evidence: .sisyphus/evidence/task-3-double-click.png (screenshot)

  Scenario: Selected item has green border
    Tool: Bash (python REPL)
    Preconditions: Folder explorer populated with files
    Steps:
      1. Select item in file_list (programmatically or via signal)
      2. Check item's stylesheet or visual state
      3. Verify border color is #00B884
    Expected Result: Selected item has green border
    Failure Indicators: No border, wrong color
    Evidence: .sisyphus/evidence/task-3-green-border.png (screenshot)

  Scenario: Refresh button updates file list
    Tool: interactive_bash (tmux)
    Preconditions: Folder opened, file added externally
    Steps:
      1. Open folder in application
      2. Add new image file to folder externally
      3. Click refresh button in UI
      4. Verify new file appears in list
    Expected Result: List updates with new file
    Failure Indicators: List doesn't update, refresh doesn't work
    Evidence: .sisyphus/evidence/task-3-refresh.txt
  ```

  **Evidence to Capture**:
  - [ ] Screenshot showing folder explorer with green selected border
  - [ ] Screenshot showing image loaded after double-click
  - [ ] Terminal output showing all tests pass
  - [ ] Evidence files: task-3-double-click.png, task-3-green-border.png, task-3-refresh.txt

  **Commit**: YES
  - Message: `feat(controller): add file selection handler and finalize integration`
  - Files: `src/controllers/image_controller.py`, `src/ui/main_window.py`
  - Pre-commit: `pytest tests/test_folder_explorer.py -v`

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + linter + `bun test`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (features working together, not isolation). Test edge cases: empty state, invalid input, rapid actions. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1**: `feat(ui): add folder explorer widget to right sidebar` — unified_right_panel.py, pytest tests
- **2**: `feat(ui): wire MainWindow delegation for folder list updates` — main_window.py
- **3**: `feat(controller): add file selection handler and finalize integration` — image_controller.py, wire signals

---

## Success Criteria

### Verification Commands
```bash
# Run tests
pytest tests/test_folder_explorer.py -v

# Manual verification
python src/main.py
# 1. Click "Open Folder" → select folder with images
# 2. Verify folder explorer appears in right sidebar with file list
# 3. Click on file → verify image loads on canvas
# 4. Verify selected file has green border
# 5. Click refresh → verify list updates
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] No window spawning issues (all widgets have parents)
- [ ] Green border styling visible on selected item
