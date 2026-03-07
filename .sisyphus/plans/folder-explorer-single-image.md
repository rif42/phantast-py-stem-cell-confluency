# Folder Explorer Enhancements - Single Image Mode

## TL;DR

> Add behavior to hide folder explorer when opening a single image (instead of a folder), and automatically create a "single image" input node in the pipeline.

**Estimated Effort**: Short (3 tasks, ~30 min)  
**Parallel Execution**: NO - sequential  
**Critical Path**: Task 1 → Task 2 → Task 3

---

## Context

### Original Request
User wants two behaviors added:
1. When clicking "Open an Image" (single file), hide the folder explorer view in the right sidebar
2. When a single image is loaded, create an input node in the pipeline called "single image"

### Current Implementation
- `action_open_image()` opens single image dialog
- `action_open_folder()` opens folder dialog
- Folder explorer was just added to UnifiedRightPanel
- Currently folder explorer shows in both modes

### Research Findings
- `UnifiedRightPanel` has folder explorer at top of metadata page
- `MainWindow.action_open_image()` calls `image_controller.handle_open_single_image(file_path)`
- Pipeline nodes created via `PipelineController.add_node(PipelineNode(...))`
- Need to add method to show/hide folder explorer section

---

## Work Objectives

### Core Objective
Modify the application to distinguish between "folder mode" and "single image mode", hiding the folder explorer and creating a pipeline node in single image mode.

### Concrete Deliverables
- Method to show/hide folder explorer in UnifiedRightPanel
- Logic to call hide when single image is loaded
- "single image" input node created in pipeline when single image is loaded

### Definition of Done
- [ ] Folder explorer hidden when "Open an Image" is used
- [ ] Folder explorer visible when "Open a Folder" is used
- [ ] Pipeline shows "single image" input node after loading single image
- [ ] All existing functionality preserved

### Must Have
- UnifiedRightPanel method to toggle folder explorer visibility
- MainWindow calls hide when single image is loaded
- Pipeline node created for single image input

### Must NOT Have (Guardrails)
- NO changes to folder explorer functionality when folder is opened
- NO changes to existing pipeline step types
- NO modifications to how folder mode works

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Sequential - 3 tasks):
├── Task 1: Add show/hide method to UnifiedRightPanel [quick]
│   └── Add set_folder_explorer_visible(visible) method
├── Task 2: Hide folder explorer in single image mode [quick]
│   └── Call set_folder_explorer_visible(False) from action_open_image
└── Task 3: Create single image input node in pipeline [quick]
    └── Add logic to create PipelineNode with type="input_single_image"
```

### Agent Dispatch Summary

- **Task 1**: `quick` - Add visibility toggle method
- **Task 2**: `quick` - Integrate visibility toggle into MainWindow
- **Task 3**: `quick` - Add pipeline node creation logic

---

## TODOs

- [ ] 1. Add show/hide method to UnifiedRightPanel

  **What to do**:
  - Add `set_folder_explorer_visible(visible: bool)` method to `UnifiedRightPanel` class
  - Method should find and toggle visibility of:
    - Folder header row (with "📁 Folder Explorer" label and refresh button)
    - File list widget (`self.file_list`)
    - Empty state label (`self.empty_label`)
  - When `visible=False`, hide all folder explorer components
  - When `visible=True`, show folder explorer (respecting empty state)

  **Must NOT do**:
  - NO changes to other panel content (metadata section stays visible)
  - NO changes to properties page
  - NO modifications to existing folder explorer logic

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Parallelization**: Sequential (Task 1 of 3)
  - **Blocked By**: None
  - **Blocks**: Task 2

  **References**:
  - `src/ui/unified_right_panel.py:85-150` - Folder explorer section layout
  - `src/ui/unified_right_panel.py:140-145` - file_list widget
  - `src/ui/unified_right_panel.py:110-125` - Folder header with refresh button

  **Acceptance Criteria**:
  - [ ] `set_folder_explorer_visible()` method added to UnifiedRightPanel
  - [ ] Calling with `visible=False` hides folder header, file list, and empty label
  - [ ] Calling with `visible=True` restores visibility (respecting empty state for label)
  - [ ] Method has type hints and docstring

  **QA Scenarios**:
  ```
  Scenario: Hide folder explorer
    Tool: Bash (python REPL)
    Steps:
      1. Create UnifiedRightPanel instance
      2. Populate with test files
      3. Call set_folder_explorer_visible(False)
      4. Verify file_list is hidden
      5. Verify refresh_btn is hidden
      6. Verify folder header is hidden
    Expected: All folder explorer components hidden

  Scenario: Show folder explorer
    Tool: Bash (python REPL)
    Steps:
      1. Create UnifiedRightPanel instance
      2. Call set_folder_explorer_visible(False) then set_folder_explorer_visible(True)
      3. Verify components are visible
    Expected: Folder explorer visible again
  ```

  **Commit**: YES
  - Message: `feat(ui): add method to show/hide folder explorer`
  - Files: `src/ui/unified_right_panel.py`

- [ ] 2. Integrate folder explorer visibility with single image mode

  **What to do**:
  - In `MainWindow.action_open_image()`, after successful image load:
    - Call `self.right_panel.set_folder_explorer_visible(False)`
  - In `MainWindow.action_open_folder()`, after successful folder load:
    - Call `self.right_panel.set_folder_explorer_visible(True)`
  - Ensure folder explorer starts visible by default

  **Must NOT do**:
  - NO changes to folder opening logic
  - NO changes to image loading logic
  - Only add visibility toggle calls

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Parallelization**: Sequential (Task 2 of 3)
  - **Blocked By**: Task 1
  - **Blocks**: Task 3

  **References**:
  - `src/ui/main_window.py:309-315` - action_open_image method
  - `src/ui/main_window.py:317-321` - action_open_folder method

  **Acceptance Criteria**:
  - [ ] `action_open_image()` calls `set_folder_explorer_visible(False)` after load
  - [ ] `action_open_folder()` calls `set_folder_explorer_visible(True)` after load
  - [ ] Folder explorer visibility correctly toggles between modes

  **QA Scenarios**:
  ```
  Scenario: Single image hides folder explorer
    Tool: Code review
    Verification: Check action_open_image calls set_folder_explorer_visible(False)

  Scenario: Folder mode shows folder explorer
    Tool: Code review
    Verification: Check action_open_folder calls set_folder_explorer_visible(True)
  ```

  **Commit**: YES
  - Message: `feat(ui): hide folder explorer in single image mode`
  - Files: `src/ui/main_window.py`

- [ ] 3. Create single image input node in pipeline

  **What to do**:
  - In `MainWindow.action_open_image()`, after successful image load:
    - Create a new PipelineNode with:
      - type="input_single_image"
      - name="Single Image"
      - icon="🖼️"
      - Add to pipeline controller
  - Check if input node already exists (avoid duplicates on re-open)
  - Refresh pipeline view after adding node

  **Must NOT do**:
  - NO changes to folder mode (no node for folder mode)
  - NO changes to other pipeline step types
  - Only add single image input node logic

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Parallelization**: Sequential (Task 3 of 3)
  - **Blocked By**: Task 2
  - **Blocks**: None

  **References**:
  - `src/ui/main_window.py:345-363` - handle_add_step pattern for creating nodes
  - `src/models/pipeline_model.py` - PipelineNode class structure
  - `src/controllers/pipeline_controller.py:14-16` - add_node method

  **Acceptance Criteria**:
  - [ ] Single image input node created when image is opened
  - [ ] Node has correct type, name, and icon
  - [ ] Node appears in pipeline stack
  - [ ] No duplicate nodes created on re-opening same image

  **QA Scenarios**:
  ```
  Scenario: Single image creates input node
    Tool: Code review / Manual test
    Steps:
      1. Open single image
      2. Verify pipeline contains node with type="input_single_image"
    Expected: Input node visible in pipeline

  Scenario: No duplicate nodes
    Tool: Code review
    Verification: Check if existing input node is cleared before adding new one
  ```

  **Commit**: YES
  - Message: `feat(pipeline): create input node for single image mode`
  - Files: `src/ui/main_window.py`

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** - `oracle`
  Verify all 3 tasks implemented correctly, folder explorer hides in single image mode, input node created.

- [ ] F2. **Code Quality Review** - `quick`
  Check for type errors, unused imports, proper docstrings.

- [ ] F3. **Real Manual QA** - `quick`
  Test both modes: Open Folder (shows explorer) vs Open Image (hides explorer + creates node).

---

## Success Criteria

### Verification Commands
```bash
# Manual test
python src/main.py
# Click "Open an Image" → verify folder explorer hidden, node created
# Click "Open a Folder" → verify folder explorer visible
```

### Final Checklist
- [ ] Folder explorer hidden when opening single image
- [ ] Folder explorer visible when opening folder
- [ ] "single image" input node appears in pipeline
- [ ] No duplicate nodes on re-open
- [ ] All tests pass
