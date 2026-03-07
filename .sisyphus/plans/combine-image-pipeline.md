# Combine Image Navigation + Pipeline Features

## TL;DR

> **Objective**: Merge the image navigation features (folder loading, image canvas, metadata) with the pipeline construction features (interactive nodes, parameter editing) into a unified single-page MainWindow.
>
> **Deliverables**:
> - Unified MainWindow with both ImageNavigationController and PipelineController
> - Extracted PipelineStackWidget (reusable pipeline stack component)
> - Dynamic right panel that switches between image metadata and node properties
> - Add button disabled when no image is loaded
>
> **Estimated Effort**: Medium (2-3 hours for implementation + testing)
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Extract PipelineStack → Create RightPanel → Integrate in MainWindow

---

## Context

### Original Request
Combine both commits into one single page app:
- **Current commit (HEAD)**: Image navigation with folder loading, image canvas, metadata panel
- **Previous commit (HEAD~1)**: Pipeline construction with interactive nodes, parameter editing

**User Requirements**:
1. Left Panel: Replace simple pipeline with full interactive nodes (add/remove/reorder/drag-drop)
2. Right Panel: Switch dynamically - show image metadata when no node selected, show node properties when node selected
3. Center Canvas: Integrate actual ImageCanvas into the pipeline layout (not placeholder)
4. NO EXTRA WINDOWS - everything embedded in MainWindow
5. NO OVERWRITING FEATURES - both feature sets work together

### Architecture Analysis

**Current MainWindow (HEAD)**:
```
MainWindow
├── ImageSessionModel (model)
├── ImageNavigationWidget (view)
│   ├── Left: Simple Input/Output nodes (placeholders)
│   ├── Center: ImageCanvas + floating toolbar
│   └── Right: Folder explorer + metadata
└── ImageNavigationController (controller)
```

**Previous MainWindow (HEAD~1)**:
```
MainWindow
├── PipelineController (controller)
├── PipelineConstructionWidget (view)
│   ├── Left: Interactive pipeline stack (add/remove/reorder/drag-drop)
│   ├── Center: Placeholder canvas
│   └── Right: Node properties panel (dynamic)
└── PipelineModel (model)
```

**Integration Strategy** (from Metis consultation):
- MainWindow owns the 3-panel layout (not widgets)
- Extract components from both widgets
- Use ImageCanvas from src/ui/image_canvas.py (already exists)
- Extract PipelineStack from PipelineConstructionWidget into PipelineStackWidget
- Create RightPanelWidget with QStackedWidget for dynamic switching

### Metis Review Findings

**Identified Gaps** (addressed):
1. **Layout Ownership**: Both widgets own their own 3-panel layouts - MainWindow must extract components, not embed full widgets
2. **Right Panel Switching**: Needs QStackedWidget or clear/rebuild pattern - must not keep both widgets instantiated
3. **Add Button State**: Should be disabled when no image selected, enabled when image loaded
4. **Signal Collisions**: Both controllers emit signals - need explicit signal contracts via MainWindow
5. **Parent Widget Safety**: Every QWidget MUST have `parent=None` parameter and pass to `super().__init__(parent=parent)`

---

## Work Objectives

### Core Objective
Create a unified MainWindow that combines image navigation and pipeline construction into a single cohesive UI without extra windows or feature loss.

### Concrete Deliverables
1. **PipelineStackWidget** (src/ui/pipeline_stack_widget.py) - Extracted reusable pipeline stack
2. **UnifiedRightPanel** (src/ui/unified_right_panel.py) - QStackedWidget switching metadata/properties
3. **Updated MainWindow** (src/ui/main_window.py) - Assembles components, coordinates controllers
4. **Updated PipelineConstructionWidget** (src/ui/pipeline_view.py) - Refactored to expose pipeline stack

### Definition of Done
- [ ] Image loading works (Open Folder, Open Image buttons)
- [ ] Pipeline node adding/removing/reordering works
- [ ] Right panel switches correctly between metadata and node properties
- [ ] Add button is disabled when no image loaded, enabled when image selected
- [ ] All widgets have proper parent assignment (no window spawning)
- [ ] Controllers don't reference each other directly (via MainWindow)

### Must Have
- Both ImageNavigationController and PipelineController active
- ImageCanvas with zoom/pan/floating toolbar working
- Interactive pipeline stack with all nodes (CLAHE, Blur, Gaussian, etc.)
- Dynamic right panel switching based on selection state
- Add button state tied to image selection

### Must NOT Have (Guardrails from Metis)
- NO embedding full widgets into each other (causes nested layout hell)
- NO duplicate parent assignment (widgets with multiple parents)
- NO controller-to-controller direct references
- NO keeping both metadata and properties widgets instantiated simultaneously
- NO window spawning (every QWidget must have proper parent)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest, pytest-qt configured)
- **Automated tests**: Tests-after (manual QA scenarios, not formal unit tests)
- **Framework**: pytest + pytest-qt
- **QA Method**: Agent-executed scenarios using interactive_bash for CLI and playwright for UI

### QA Policy
Every task MUST include agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright (playwright skill) — Navigate, interact, assert DOM, screenshot
- **TUI/CLI**: Use interactive_bash (tmux) — Run command, validate output

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - Extract Components):
├── Task 1: Extract PipelineStackWidget from PipelineConstructionWidget [quick]
└── Task 2: Create UnifiedRightPanel with QStackedWidget [quick]

Wave 2 (Integration - MainWindow Assembly):
├── Task 3: Refactor MainWindow to use extracted components [deep]
├── Task 4: Wire up controller coordination (image → pipeline) [unspecified-high]
└── Task 5: Implement Add button state management [quick]

Wave 3 (Final Verification):
├── Task 6: Integration testing - all features working together [unspecified-high]
└── Task 7: QA verification - right panel switching, button states [unspecified-high]

Critical Path: Task 1 → Task 2 → Task 3 → Task 6 → Task 7
Parallel Speedup: ~40% faster than sequential
Max Concurrent: 2 (Wave 1 and Wave 2 overlap possible)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 1. Extract PipelineStackWidget | — | 3 |
| 2. Create UnifiedRightPanel | — | 3 |
| 3. Refactor MainWindow | 1, 2 | 4, 5 |
| 4. Wire Controllers | 3 | 6 |
| 5. Add Button State | 3 | 6 |
| 6. Integration Testing | 4, 5 | 7 |
| 7. QA Verification | 6 | — |

### Agent Dispatch Summary

- **1**: 2 agents — T1 → `quick`, T2 → `quick`
- **2**: 3 agents — T3 → `deep`, T4 → `unspecified-high`, T5 → `quick`
- **3**: 2 agents — T6 → `unspecified-high`, T7 → `unspecified-high`

---

## TODOs

- [ ] 1. Extract PipelineStackWidget from PipelineConstructionWidget

  **What to do**:
  - Create new file `src/ui/pipeline_stack_widget.py`
  - Extract the left panel logic from PipelineConstructionWidget:
    - Pipeline stack (scroll area with PipelineNodeWidget items)
    - Add button with QMenu
    - Drag-drop reordering logic
    - Signals: add_step_requested, toggle_node, delete_node, node_reordered, node_selected
  - Keep PipelineConstructionWidget functional (backward compatibility) by importing/using PipelineStackWidget internally
  - Ensure all widget creations have `parent=xxx` parameter

  **Must NOT do**:
  - Do NOT change PipelineConstructionWidget's public API (keep signals/slots same)
  - Do NOT remove PipelineConstructionWidget (keep for reference/compatibility)
  - Do NOT embed PipelineConstructionWidget inside another widget (causes double parent)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Code extraction and refactoring, well-defined scope
  - **Skills**: []
    - No special skills needed - pure PyQt6 widget refactoring

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 3
  - **Blocked By**: None

  **References**:
  - `src/ui/pipeline_view.py:15-80` - HelpTooltip and ToggleSwitch classes (may need to import)
  - `src/ui/pipeline_view.py:90-180` - PipelineNodeWidget class
  - `src/ui/pipeline_view.py:190-290` - PipelineConstructionWidget left panel creation
  - `src/ui/pipeline_view.py:PipelineConstructionWidget.__init__` - Layout structure

  **WHY Each Reference Matters**:
  - HelpTooltip/ToggleSwitch: Reusable components needed by PipelineNodeWidget
  - PipelineNodeWidget: Individual node widget (draggable, toggleable, deletable)
  - Left panel creation: Shows how scroll area + nodes are assembled
  - Layout structure: Understand the QSplitter and widget hierarchy

  **Acceptance Criteria**:
  - [ ] PipelineStackWidget created in src/ui/pipeline_stack_widget.py
  - [ ] Widget has signals: add_step_requested, toggle_node, delete_node, node_reordered, node_selected
  - [ ] All widget creations have parent parameter and pass to super().__init__(parent=parent)
  - [ ] PipelineConstructionWidget still works (imports PipelineStackWidget internally)
  - [ ] No window spawning when creating PipelineStackWidget instance

  **QA Scenarios**:
  ```
  Scenario: PipelineStackWidget can be instantiated without spawning windows
    Tool: interactive_bash (tmux)
    Preconditions: Clean Python environment, PyQt6 installed
    Steps:
      1. Run Python REPL: python -c "from PyQt6.QtWidgets import QApplication, QWidget; from src.ui.pipeline_stack_widget import PipelineStackWidget; app = QApplication([]); parent = QWidget(); stack = PipelineStackWidget(parent=parent); print('SUCCESS: Created without spawning window')"
    Expected Result: "SUCCESS" printed, no separate window appears
    Failure Indicators: Window spawns, import error, AttributeError on signals
    Evidence: .sisyphus/evidence/task-1-instantiation.txt

  Scenario: PipelineConstructionWidget still functional after extraction
    Tool: interactive_bash (tmux)
    Preconditions: Extraction complete
    Steps:
      1. Run: python -c "from src.ui.pipeline_view import PipelineConstructionWidget; print('SUCCESS: PipelineConstructionWidget imports correctly')"
    Expected Result: "SUCCESS" printed, no import errors
    Failure Indicators: ImportError, missing attribute errors
    Evidence: .sisyphus/evidence/task-1-backward-compat.txt
  ```

  **Commit**: YES
  - Message: `refactor(ui): extract PipelineStackWidget from PipelineConstructionWidget`
  - Files: `src/ui/pipeline_stack_widget.py` (new), `src/ui/pipeline_view.py` (modified)

---

- [ ] 2. Create UnifiedRightPanel with QStackedWidget

  **What to do**:
  - Create new file `src/ui/unified_right_panel.py`
  - Implement UnifiedRightPanel widget with QStackedWidget:
    - Page 0: Image metadata panel (extract from ImageNavigationWidget)
    - Page 1: Node properties panel (extract from PipelineConstructionWidget)
  - Add methods: `show_metadata()`, `show_properties(node_data)`
  - Emit signal when page changes (for testing)
  - Proper parent assignment throughout

  **Must NOT do**:
  - Do NOT keep both pages instantiated simultaneously (use QStackedWidget properly)
  - Do NOT duplicate the folder explorer from ImageNavigationWidget (not needed here)
  - Do NOT import ImageNavigationWidget or PipelineConstructionWidget (extract components only)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Component assembly, clear requirements
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 3
  - **Blocked By**: None

  **References**:
  - `src/ui/image_navigation.py:320-400` - Right panel creation (metadata section)
  - `src/ui/image_navigation.py:ImageNavigationWidget._update_metadata_panel` - Metadata update logic
  - `src/ui/pipeline_view.py:300-380` - Right panel creation (properties header)
  - `src/ui/pipeline_view.py:PipelineConstructionWidget._update_properties_panel` - Properties update logic
  - PyQt6 docs: QStackedWidget usage pattern

  **WHY Each Reference Matters**:
  - Right panel creation (image nav): Shows metadata panel structure and fields
  - Metadata update logic: How metadata is populated when image changes
  - Right panel creation (pipeline): Shows properties panel header structure
  - Properties update logic: How node properties are dynamically generated

  **Acceptance Criteria**:
  - [ ] UnifiedRightPanel created in src/ui/unified_right_panel.py
  - [ ] Has QStackedWidget with 2 pages
  - [ ] Has methods: show_metadata(), show_properties(node_data)
  - [ ] Emits signal: panel_changed(str) when switching
  - [ ] All widgets have proper parent assignment
  - [ ] Can switch between pages programmatically

  **QA Scenarios**:
  ```
  Scenario: UnifiedRightPanel switches between metadata and properties
    Tool: interactive_bash (tmux)
    Preconditions: Panel created
    Steps:
      1. Create panel: panel = UnifiedRightPanel(parent=parent)
      2. Call show_metadata()
      3. Verify current page is 0
      4. Call show_properties({'name': 'CLAHE', 'params': {}})
      5. Verify current page is 1
    Expected Result: Page switches correctly, no errors
    Failure Indicators: IndexError, widgets not visible, AttributeError
    Evidence: .sisyphus/evidence/task-2-switching.txt
  ```

  **Commit**: YES
  - Message: `feat(ui): create UnifiedRightPanel for dynamic metadata/properties switching`
  - Files: `src/ui/unified_right_panel.py` (new)

---

- [ ] 3. Refactor MainWindow to use extracted components

  **What to do**:
  - Update `src/ui/main_window.py` to:
    1. Import PipelineStackWidget, UnifiedRightPanel, ImageCanvas
    2. Import both controllers: ImageNavigationController, PipelineController
    3. Create layout: QSplitter with 3 panels
       - Left: PipelineStackWidget
       - Center: ImageCanvas with floating toolbar
       - Right: UnifiedRightPanel
    4. Instantiate both controllers with appropriate models
    5. Wire signals:
       - ImageNavigationController.image_selected → update canvas + show metadata
       - PipelineStackWidget.node_selected → show properties in right panel
       - PipelineStackWidget.node_deselected → show metadata in right panel
  - Remove dependency on ImageNavigationWidget (extract components directly)

  **Must NOT do**:
  - Do NOT embed ImageNavigationWidget or PipelineConstructionWidget (use extracted components only)
  - Do NOT lose any functionality from either feature set
  - Do NOT have controllers reference each other directly
  - Do NOT forget to pass parent= to all widget constructors

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Complex integration requiring understanding of both MVC patterns, signal routing, and careful widget lifecycle management
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (sequential with Task 4, 5)
  - **Blocks**: Task 4, Task 5
  - **Blocked By**: Task 1, Task 2

  **References**:
  - `src/ui/main_window.py` (current HEAD) - Shows current ImageNavigation setup
  - `src/controllers/image_controller.py` - ImageNavigationController signals and interface
  - `src/controllers/pipeline_controller.py` - PipelineController signals and interface
  - `src/ui/image_canvas.py` - ImageCanvas widget (center panel)
  - `src/ui/pipeline_view.py:PipelineConstructionWidget.__init__` - QSplitter usage pattern
  - `src/ui/image_navigation.py:ImageNavigationWidget.__init__` - Layout and toolbar setup

  **WHY Each Reference Matters**:
  - Current main_window.py: Shows how controllers are instantiated and wired
  - ImageNavigationController: Signals like image_loaded, image_list_updated
  - PipelineController: Signals like add_step, toggle_node, node_selected
  - ImageCanvas: Already exists as separate widget, use directly
  - QSplitter usage: How to create 3-panel layout with adjustable sizes
  - Layout setup: How to create floating toolbar and wire it to canvas

  **Acceptance Criteria**:
  - [ ] MainWindow imports both controllers and extracted components
  - [ ] QSplitter layout with PipelineStackWidget, ImageCanvas, UnifiedRightPanel
  - [ ] ImageNavigationController connected to ImageCanvas
  - [ ] PipelineController connected to PipelineStackWidget
  - [ ] Right panel shows metadata when image selected
  - [ ] Right panel shows properties when node selected
  - [ ] No window spawning on startup
  - [ ] Application launches without errors

  **QA Scenarios**:
  ```
  Scenario: MainWindow launches with all components integrated
    Tool: interactive_bash (tmux)
    Preconditions: All components extracted and created
    Steps:
      1. Run: python src/main.py
      2. Wait for window to appear
      3. Verify window title is "PhantastLab"
      4. Take screenshot
      5. Exit application
    Expected Result: Window appears, no errors in console, screenshot shows 3-panel layout
    Failure Indicators: Import errors, window spawning issues, layout broken
    Evidence: .sisyphus/evidence/task-3-launch.png

  Scenario: Image loading updates canvas and metadata
    Tool: interactive_bash (tmux)
    Preconditions: Application running
    Steps:
      1. Click "Open Image" button
      2. Select test image (tests/data/test_image.tiff)
      3. Verify image appears in canvas
      4. Verify metadata panel shows image info
    Expected Result: Canvas shows image, metadata populated
    Failure Indicators: Image not loading, metadata empty, errors
    Evidence: .sisyphus/evidence/task-3-image-load.png
  ```

  **Commit**: YES
  - Message: `feat(ui): refactor MainWindow to combine image navigation and pipeline features`
  - Files: `src/ui/main_window.py` (modified)

---

- [ ] 4. Wire up controller coordination (image → pipeline)

  **What to do**:
  - In MainWindow, implement coordination logic:
    1. When image is loaded (ImageNavigationController.image_selected):
       - Update ImageCanvas
       - Update UnifiedRightPanel metadata page
       - Update internal state: `self.current_image = image_path`
    2. When pipeline stack emits signals:
       - Route to PipelineController for processing
    3. Connect Add button state to image selection (see Task 5)
  - Ensure controllers don't reference each other - MainWindow is the coordinator

  **Must NOT do**:
  - Do NOT have controllers import each other
  - Do NOT put coordination logic in controllers (keep in MainWindow)
  - Do NOT lose signals during wiring (must maintain all existing signal chains)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Complex signal routing and state management
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 5 after Task 3)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 6
  - **Blocked By**: Task 3

  **References**:
  - `src/controllers/image_controller.py:ImageNavigationController` - Available signals
  - `src/controllers/pipeline_controller.py:PipelineController` - Available signals
  - `src/ui/pipeline_stack_widget.py` (from Task 1) - Signals to wire
  - PyQt6 docs: Signal/slot connections with lambda or functools.partial

  **WHY Each Reference Matters**:
  - ImageNavigationController: Shows all signals available for coordination
  - PipelineController: Shows pipeline-related signals
  - PipelineStackWidget signals: What needs to be connected to PipelineController
  - Signal/slot docs: How to pass additional arguments to slots

  **Acceptance Criteria**:
  - [ ] Image selection updates both canvas and metadata panel
  - [ ] Pipeline node operations route to PipelineController
  - [ ] MainWindow tracks current_image state
  - [ ] Controllers don't import each other (check imports)
  - [ ] All signal connections use proper parent references

  **QA Scenarios**:
  ```
  Scenario: Controller coordination works correctly
    Tool: interactive_bash (tmux)
    Preconditions: MainWindow refactored
    Steps:
      1. Load image via ImageNavigationController
      2. Verify MainWindow.current_image is set
      3. Verify canvas shows image
      4. Verify metadata panel updated
      5. Add pipeline node
      6. Verify node appears in stack
    Expected Result: All operations work, state synchronized
    Failure Indicators: State not updated, signals not firing, crashes
    Evidence: .sisyphus/evidence/task-4-coordination.txt
  ```

  **Commit**: NO (groups with Task 3)

---

- [ ] 5. Implement Add button state management

  **What to do**:
  - Implement logic in MainWindow:
    1. When no image is loaded: `pipeline_stack.add_button.setEnabled(False)`
    2. When image is loaded: `pipeline_stack.add_button.setEnabled(True)`
    3. Add tooltip: "Load an image first" when disabled
  - Ensure PipelineStackWidget exposes the add_button reference
  - Handle edge cases: image cleared, folder with no valid images, etc.

  **Must NOT do**:
  - Do NOT disable the entire pipeline stack (just the Add button)
  - Do NOT forget to re-enable when image is loaded
  - Do NOT use hardcoded button references (expose via PipelineStackWidget API)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple state management logic
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 4 after Task 3)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 6
  - **Blocked By**: Task 3

  **References**:
  - `src/ui/pipeline_stack_widget.py` (from Task 1) - Add button reference
  - PyQt6 docs: QPushButton.setEnabled(), setToolTip()
  - `src/controllers/image_controller.py:image_selected` signal

  **WHY Each Reference Matters**:
  - PipelineStackWidget: Need to expose add_button for state management
  - QPushButton methods: How to disable and add tooltip
  - image_selected signal: Trigger for enabling button

  **Acceptance Criteria**:
  - [ ] Add button is disabled when MainWindow starts (no image)
  - [ ] Add button is enabled when image is loaded
  - [ ] Add button is disabled when image is cleared
  - [ ] Tooltip shows "Load an image first" when disabled
  - [ ] Button state updates immediately on image change (no delay)

  **QA Scenarios**:
  ```
  Scenario: Add button state reflects image selection
    Tool: interactive_bash (tmux)
    Preconditions: MainWindow running
    Steps:
      1. Start app, verify Add button is disabled
      2. Load image, verify Add button is enabled
      3. Clear image/folder, verify Add button is disabled
      4. Hover over disabled button, verify tooltip appears
    Expected Result: Button state correctly tracks image availability
    Failure Indicators: Button enabled without image, tooltip missing, state out of sync
    Evidence: .sisyphus/evidence/task-5-button-state.txt
  ```

  **Commit**: NO (groups with Task 3)

---

- [ ] 6. Integration testing - all features working together

  **What to do**:
  - Run full integration test:
    1. Start application
    2. Load folder with images
    3. Select different images (verify canvas updates)
    4. Add pipeline nodes (verify stack updates)
    5. Select nodes (verify properties panel shows)
    6. Deselect nodes (verify metadata panel shows)
    7. Reorder nodes (verify order changes)
    8. Toggle nodes (verify visual state changes)
    9. Delete nodes (verify removed from stack)
    10. Verify no errors in console
  - Check for any signal warnings or Qt warnings

  **Must NOT do**:
  - Do NOT skip any feature - test ALL functionality from both commits
  - Do NOT ignore Qt warnings (fix parent assignment issues)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Comprehensive integration testing
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 7
  - **Blocked By**: Task 4, Task 5

  **References**:
  - All previously created/modified files
  - `tests/` directory for any existing integration tests

  **Acceptance Criteria**:
  - [ ] All image navigation features work (folder load, image select, zoom, pan)
  - [ ] All pipeline features work (add, remove, reorder, toggle nodes)
  - [ ] Right panel switches correctly
  - [ ] Add button state is correct
  - [ ] No Qt warnings in console
  - [ ] No Python exceptions

  **QA Scenarios**:
  ```
  Scenario: Full integration test passes
    Tool: interactive_bash (tmux)
    Preconditions: All previous tasks complete
    Steps:
      1. Launch application
      2. Execute full feature checklist (see Acceptance Criteria)
      3. Capture console output
      4. Check for warnings/errors
    Expected Result: All features work, console clean
    Failure Indicators: Any feature broken, console warnings/errors
    Evidence: .sisyphus/evidence/task-6-integration.log
  ```

  **Commit**: YES (if fixes needed)
  - Message: `fix(ui): integration fixes for combined features`
  - Files: Any files requiring fixes

---

- [ ] 7. QA verification - right panel switching, button states

  **What to do**:
  - Final QA verification with specific focus:
    1. Right panel switching: Test all combinations
       - No image, no node selected → show what?
       - Image loaded, no node selected → show metadata
       - Image loaded, node selected → show properties
       - Node deselected → back to metadata
    2. Add button states: Verify at each step above
    3. Window behavior: Verify no extra windows spawn
    4. Screenshot final state for evidence

  **Must NOT do**:
  - Do NOT skip edge cases
  - Do NOT assume functionality works - verify each scenario

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Detailed verification with edge cases
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (final)
  - **Blocks**: None (last task)
  - **Blocked By**: Task 6

  **Acceptance Criteria**:
  - [ ] Right panel shows correct content in all scenarios
  - [ ] Add button disabled/enabled correctly in all scenarios
  - [ ] No window spawning at any point
  - [ ] Screenshots captured for evidence
  - [ ] QA report generated

  **QA Scenarios**:
  ```
  Scenario: Right panel switching works in all states
    Tool: interactive_bash (tmux)
    Preconditions: App running
    Steps:
      1. State: No image, no node → verify panel state
      2. State: Image loaded, no node → verify metadata shown
      3. State: Image loaded, node selected → verify properties shown
      4. State: Node deselected → verify metadata shown again
    Expected Result: Panel switches correctly in all states
    Failure Indicators: Wrong content shown, no switching, crashes
    Evidence: .sisyphus/evidence/task-7-panel-states.txt

  Scenario: No window spawning throughout usage
    Tool: interactive_bash (tmux)
    Preconditions: App running
    Steps:
      1. Monitor for new windows during all operations
      2. Check after: startup, image load, node add, node select, etc.
    Expected Result: Only MainWindow visible at all times
    Failure Indicators: Any additional window appears
    Evidence: .sisyphus/evidence/task-7-no-windows.txt
  ```

  **Commit**: NO (verification only)

---

## Final Verification Wave (MANDATORY)

> 4 review agents run in PARALLEL. ALL must APPROVE.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `python -m pytest tests/ -v` if tests exist. Review all changed files for: unused imports, missing docstrings, style issues. Check for AI slop: excessive comments, over-abstraction, generic names.
  Output: `Tests [PASS/FAIL/N/A] | Style [PASS/FAIL] | Quality [PASS/FAIL] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill if available)
  Start from clean state. Execute EVERY QA scenario from EVERY task. Test edge cases: empty state, rapid switching, concurrent operations. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git diff HEAD). Verify 1:1 - everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance.
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Task 1**: `refactor(ui): extract PipelineStackWidget from PipelineConstructionWidget`
- **Task 2**: `feat(ui): create UnifiedRightPanel for dynamic metadata/properties switching`
- **Task 3**: `feat(ui): refactor MainWindow to combine image navigation and pipeline features`
- **Task 6**: `fix(ui): integration fixes for combined features` (if needed)

---

## Success Criteria

### Verification Commands
```bash
# Test basic functionality
python src/main.py

# Test imports
python -c "from src.ui.pipeline_stack_widget import PipelineStackWidget; from src.ui.unified_right_panel import UnifiedRightPanel; print('All imports OK')"

# Check for test infrastructure
pytest tests/ -v 2>/dev/null || echo "No tests or pytest not configured"
```

### Final Checklist
- [ ] All "Must Have" present and working
- [ ] All "Must NOT Have" absent (no window spawning, no controller references, etc.)
- [ ] No Qt warnings in console
- [ ] Evidence files exist for all QA scenarios
- [ ] All tasks marked complete
- [ ] Final verification wave passed
