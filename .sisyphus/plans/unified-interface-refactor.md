# Unified Interface Refactor Plan

## TL;DR

> **Refactor PhantastLab from multi-view (QStackedWidget) to unified single-window interface.**
> 
> **Deliverables**:
> - `AppState` - Central observable application state
> - `UnifiedMainWidget` - Single container replacing QStackedWidget
> - `MainController` - Orchestrates workflow phases and panel transitions
> - Fixed Input/PHANTAST nodes with draggable middle nodes
> - Real-time preview pipeline with debounced updates
> - Adaptive left/right panels based on workflow phase
> 
> **Estimated Effort**: Large (5-7 days)
> **Parallel Execution**: YES - 5 waves
> **Critical Path**: State Model → Controller → Unified Widget → Preview Pipeline → Integration

---

## Context

### Current State
Application uses **QStackedWidget** with 3 separate views:
- Image Loading (folder browser, empty state)
- Pipeline Construction (drag-drop nodes)
- Batch Execution (3-panel combined view)

**87 tests passing** with view-switching navigation (F1/F2/F3, nav buttons).

### User Requirements
User clarified there should be **ONE unified window** throughout the workflow:
1. **Initial state**: Empty canvas, no side panels (or minimal)
2. **After image loaded**: Left panel shows pipeline stack, center shows image, right shows metadata
3. **Pipeline building**: User can add nodes (Grayscale, GaussianBlur, CLAHE) between fixed Input and PHANTAST nodes
4. **Drag-drop**: Middle nodes can be reordered; Input (first) and PHANTAST (last) are fixed
5. **Toggle**: Each node can be enabled/disabled (except fixed nodes)
6. **Properties**: Right panel shows editable parameters for selected node
7. **Preview**: Real-time pipeline execution on current image as nodes change

### Metis Analysis Findings

**Components to Unify**:
- 3-Panel layout → Single `UnifiedMainWidget`
- ImageCanvas → Shared instance throughout
- Pipeline Stack → Left panel
- Properties Panel → Right panel (context-aware)

**Components to Keep Separate**:
- `PipelineNodeWidget` - reusable node rendering
- `ToggleSwitch` - pure UI component
- `PipelineStep` classes - business logic
- `ImagePipeline` - execution engine

**State Management**:
- Central `AppState` with workflow phases: EMPTY → IMAGE_LOADED → NODES_ADDED
- Observable pattern: UI components react to state changes
- Selected node ID determines right panel content

**Edge Cases Identified**:
- Fixed nodes cannot be dragged or deleted (enforced in PipelineNodeWidget.is_draggable)
- Drop validation prevents placing before Input (index 0) or after Output
- Empty pipeline state needs "Add Step" placeholder between fixed nodes
- Phase transitions must update all three panels atomically

---

## Work Objectives

### Core Objective
Transform PhantastLab from a multi-view navigation app to a unified single-window image processing pipeline with adaptive panels and real-time preview.

### Concrete Deliverables
1. **State Layer**: `AppState` dataclass with workflow phase enum
2. **Controller Layer**: `MainController` with phase transition logic
3. **UI Layer**: `UnifiedMainWidget` replacing QStackedWidget
4. **Panel Logic**: Adaptive left/right panels based on phase
5. **Fixed Nodes**: Enforce Input/PHANTAST immovability
6. **Preview Pipeline**: Debounced real-time execution (200ms)
7. **Properties Panel**: Dynamic editors per node type
8. **Deprecated Cleanup**: Remove QStackedWidget, nav buttons, F1/F2/F3 shortcuts

### Definition of Done
- [ ] One window throughout entire workflow (no view switching)
- [ ] Left panel: hidden → pipeline stack transition works
- [ ] Right panel: hidden → metadata → node properties transition works
- [ ] Input node (first) and PHANTAST node (last) cannot be dragged or deleted
- [ ] Middle nodes (Grayscale, GaussianBlur, CLAHE) can be reordered via drag-drop
- [ ] Each node has toggle switch (middle nodes) / fixed on (end nodes)
- [ ] Selecting node shows editable properties in right panel
- [ ] Pipeline changes trigger real-time preview update (debounced 200ms)
- [ ] All 87+ existing tests pass + new integration tests added

### Must Have (Non-Negotiable)
- Fixed Input node at position 0
- Fixed PHANTAST node at final position
- Draggable middle nodes between fixed nodes
- Toggle switches for enable/disable (middle nodes only)
- Real-time preview on current image
- Dark theme consistency throughout

### Must NOT Have (Guardrails)
- Multiple windows or dialogs for main workflow
- View-switching buttons or shortcuts
- Separate "Batch Execution" view (integrate into unified flow)
- Blocking UI during pipeline execution (use background thread)
- Allow deleting fixed nodes
- Allow dragging fixed nodes

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest, pytest-qt)
- **Automated tests**: Tests-after (integration tests for new components)
- **Framework**: pytest-qt for GUI testing
- **Coverage target**: Maintain 80%+ coverage

### QA Policy
Every task includes agent-executed QA scenarios:
- **UI Tests**: Use qtbot for widget interactions, signal verification
- **Integration**: Test phase transitions end-to-end
- **Performance**: Preview updates must not block UI (>200ms ops in thread)

### QA Scenarios Template
Each UI task must include:
```python
# Happy Path
Scenario: "Workflow phase transitions correctly"
Tool: pytest-qt (qtbot)
Steps:
  1. Create MainController in EMPTY phase
  2. Call load_image("test.tiff")
  3. Assert state.workflow_phase == IMAGE_LOADED
  4. Assert left panel shows pipeline stack
  5. Assert right panel shows metadata
Expected: All assertions pass

# Edge Case  
Scenario: "Cannot drag fixed nodes"
Tool: pytest-qt
Steps:
  1. Create pipeline with input, grayscale, output nodes
  2. Try to drag input node (simulate mouse events)
  3. Assert drag operation did not start (no mime data)
Expected: is_draggable == False prevents drag
```

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - Independent, can start immediately):
├── Task 1: Create AppState dataclass with workflow phases
├── Task 2: Create WorkflowPhase enum and state transitions
├── Task 3: Add pipeline reordering methods to PipelineModel
└── Task 4: Create property editor base classes

Wave 2 (Controller Core - depends on Wave 1):
├── Task 5: Create MainController skeleton with AppState
├── Task 6: Implement phase transition logic (EMPTY → IMAGE_LOADED → NODES_ADDED)
├── Task 7: Connect controller to existing ImageNavigationController
└── Task 8: Add preview pipeline execution with debouncing

Wave 3 (Unified UI Widget - depends on Wave 2):
├── Task 9: Create UnifiedMainWidget with 3-panel splitter
├── Task 10: Implement adaptive left panel (hidden → folder → pipeline)
├── Task 11: Implement adaptive right panel (hidden → metadata → properties)
├── Task 12: Integrate ImageCanvas as permanent center panel
└── Task 13: Connect panel state to controller signals

Wave 4 (Pipeline Features - depends on Wave 3):
├── Task 14: Migrate drag-drop nodes from pipeline_view.py
├── Task 15: Enforce fixed Input/PHANTAST nodes (not draggable/deletable)
├── Task 16: Add "Add Step" UI between fixed nodes when empty
├── Task 17: Create node-specific property editors (Grayscale, GaussianBlur, CLAHE)
├── Task 18: Connect toggle switches to node enabled state
└── Task 19: Implement real-time preview updates

Wave 5 (Cleanup & Integration - depends on Wave 4):
├── Task 20: Refactor MainWindow to use UnifiedMainWidget
├── Task 21: Remove QStackedWidget and navigation buttons
├── Task 22: Remove/deprecate BatchExecutionIntegrationWidget
├── Task 23: Update keyboard shortcuts (remove F1/F2/F3, repurpose if needed)
├── Task 24: Update main.py entry point
└── Task 25: Create comprehensive integration tests

Wave FINAL (Verification):
├── Task F1: Code quality review (linter, type check)
├── Task F2: Integration tests - full workflow
├── Task F3: UI QA - drag-drop, toggles, properties
└── Task F4: Performance QA - preview responsiveness
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1-4 | - | 5, 6, 7, 8 |
| 5-8 | 1-4 | 9-13 |
| 9-13 | 5-8 | 14-19 |
| 14-19 | 9-13 | 20-25 |
| 20-25 | 14-19 | F1-F4 |
| F1-F4 | 20-25 | - |

### Agent Dispatch Summary

- **Wave 1**: 4 tasks → `quick` (AppState is straightforward dataclass work)
- **Wave 2**: 4 tasks → `deep` (Controller logic requires careful state management)
- **Wave 3**: 5 tasks → `visual-engineering` (UI layout and panel adaptation)
- **Wave 4**: 6 tasks → `deep` + `visual-engineering` (drag-drop logic + property editors)
- **Wave 5**: 6 tasks → `deep` (refactoring existing code, requires understanding current structure)
- **Wave FINAL**: 4 tasks → `unspecified-high` (QA and verification)

---

## TODOs

### Wave 1: Foundation (State & Model)

- [ ] 1. **Create AppState dataclass with workflow phases**

  **What to do**:
  - Create `src/models/app_state.py`
  - Define `WorkflowPhase` enum: `EMPTY`, `IMAGE_LOADED`, `NODES_ADDED`, `PROCESSING`
  - Create `AppState` dataclass with fields:
    - `current_image: Optional[ImageSession]`
    - `pipeline: Pipeline`
    - `selected_node_id: Optional[str]`
    - `workflow_phase: WorkflowPhase`
    - `preview_image: Optional[np.ndarray]`
  - Add QObject wrapper for signals: `state_changed(str)` field name
  
  **Must NOT do**:
  - Do NOT import PyQt in the dataclass file (keep it testable)
  - Do NOT add business logic, just state container

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None needed
  - **Rationale**: Simple dataclass definition

  **Parallelization**: YES - Wave 1
  **Blocked By**: None
  **Blocks**: Task 5 (MainController)

  **References**:
  - Pattern: `src/models/pipeline_model.py:7-44` (PipelineNode dataclass)
  - Type hints: Use `from __future__ import annotations` for forward refs

  **Acceptance Criteria**:
  - [ ] File created: `src/models/app_state.py`
  - [ ] All 5 fields defined with proper types
  - [ ] `WorkflowPhase` enum with 4 values
  - [ ] Can instantiate: `AppState(workflow_phase=WorkflowPhase.EMPTY)`
  - [ ] Tests: `tests/models/test_app_state.py` with 3+ tests

  **QA Scenarios**:
  ```python
  Scenario: "AppState instantiation"
    Tool: pytest
    Steps:
      1. state = AppState()
      2. Assert state.workflow_phase == WorkflowPhase.EMPTY
      3. Assert state.pipeline.nodes == []
    Expected: All assertions pass
  ```

  **Commit**: YES
  - Message: `feat(models): Add AppState with workflow phases`
  - Files: `src/models/app_state.py`, `tests/models/test_app_state.py`

- [ ] 2. **Create WorkflowPhase enum and state transitions**

  **What to do**:
  - Define valid transitions in `AppState`:
    - `EMPTY` → `IMAGE_LOADED` (on image load)
    - `IMAGE_LOADED` → `NODES_ADDED` (on first node add)
    - `NODES_ADDED` → `PROCESSING` (on run)
    - Any → `EMPTY` (on close/clear)
  - Add `can_transition_to(target: WorkflowPhase) -> bool` method
  - Add `transition_to(target: WorkflowPhase)` with validation

  **Must NOT do**:
  - Do NOT allow invalid transitions (e.g., EMPTY → NODES_ADDED directly)
  - Do NOT auto-transition; controller decides when to call

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**: YES - Wave 1

  **Acceptance Criteria**:
  - [ ] `can_transition_to()` returns True for valid transitions
  - [ ] `can_transition_to()` returns False for invalid transitions
  - [ ] `transition_to()` raises ValueError for invalid transition
  - [ ] Tests cover all transition paths

  **Commit**: YES (group with Task 1)

- [ ] 3. **Add pipeline reordering methods to PipelineModel**

  **What to do**:
  - Extend `src/models/pipeline_model.py:Pipeline` class:
    - `move_node(node_id: str, new_index: int) -> bool`
    - `insert_node_at(node: PipelineNode, after_node_id: str) -> bool`
    - `can_move_node(node_id: str, new_index: int) -> bool` (validates not moving fixed nodes)
  - Fixed node protection: nodes with type 'input' or 'output' cannot move
  - Validate indices: must keep input at 0, output at end

  **Must NOT do**:
  - Do NOT allow moving fixed nodes
  - Do NOT allow placing nodes at invalid indices

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**: YES - Wave 1

  **References**:
  - Pattern: `src/core/pipeline.py:25-29` (move_step method)
  - Fixed node check: `src/ui/pipeline_view.py:84-85`

  **Acceptance Criteria**:
  - [ ] `move_node()` respects fixed node boundaries
  - [ ] `can_move_node()` returns False for invalid moves
  - [ ] Tests: move middle node, reject moving input, reject moving output

  **Commit**: YES

- [ ] 4. **Create property editor base classes**

  **What to do**:
  - Create `src/ui/property_editors/__init__.py`
  - Create `src/ui/property_editors/base_editor.py` with:
    - `PropertyEditorBase(QWidget)` abstract class
    - `value_changed` signal
    - `set_value()`, `get_value()` methods
    - `set_parameter_spec(spec: dict)` for configuration
  - Create `src/ui/property_editors/spinbox_editor.py`
  - Create `src/ui/property_editors/combobox_editor.py`

  **Must NOT do**:
  - Do NOT hardcode parameter names
  - Do NOT create full editors yet (just base classes)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`

  **Parallelization**: YES - Wave 1

  **References**:
  - Pattern: `src/ui/pipeline_view.py:485-517` (add_spinbox_row)

  **Acceptance Criteria**:
  - [ ] Base class defines interface
  - [ ] SpinBox editor implements interface
  - [ ] Tests: value_changed signal fires on edit

  **Commit**: YES

### Wave 2: Controller Core

- [ ] 5. **Create MainController skeleton with AppState**

  **What to do**:
  - Create `src/controllers/main_controller.py`
  - Create `MainController(QObject)` class:
    - `__init__()`: create AppState, ImagePipeline
    - `state: AppState` property
    - `load_image(filepath: str)` slot
    - `phase_changed`, `image_loaded`, `preview_updated` signals
  - Wire up to existing ImageNavigationController

  **Must NOT do**:
  - Do NOT implement full phase logic yet (Task 6)
  - Do NOT connect UI yet (Task 9-13)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: None

  **Parallelization**: YES - Wave 2
  **Blocked By**: Task 1, 2

  **References**:
  - Pattern: `src/controllers/image_controller.py:1-103`

  **Acceptance Criteria**:
  - [ ] Controller instantiates with AppState
  - [ ] Signals defined and can connect
  - [ ] Tests: `tests/controllers/test_main_controller.py`

  **Commit**: YES

- [ ] 6. **Implement phase transition logic**

  **What to do**:
  - Implement `MainController.load_image(filepath)`:
    1. Load image into ImageSession
    2. Create default pipeline (Input → Output)
    3. Transition state to IMAGE_LOADED
    4. Emit `image_loaded` and `phase_changed` signals
  - Implement `MainController.add_node(node_type: str)`:
    1. Create PipelineNode
    2. Insert between Input and Output
    3. If first middle node, transition to NODES_ADDED
  - Implement `MainController.clear()`:
    1. Clear state
    2. Transition to EMPTY

  **Must NOT do**:
  - Do NOT allow direct state mutation (use controller methods)
  - Do NOT skip transition validation

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: None

  **Parallelization**: YES - Wave 2

  **Acceptance Criteria**:
  - [ ] `load_image()` transitions EMPTY → IMAGE_LOADED
  - [ ] `add_node()` transitions IMAGE_LOADED → NODES_ADDED
  - [ ] `clear()` transitions to EMPTY
  - [ ] Tests verify all phase transitions

  **Commit**: YES

- [ ] 7. **Connect controller to existing ImageNavigationController**

  **What to do**:
  - Modify `ImageNavigationController` to work with `MainController`
  - On file selected: call `main_controller.load_image()`
  - Keep existing view update logic
  - Ensure no circular dependencies

  **Must NOT do**:
  - Do NOT break existing image loading functionality
  - Do NOT duplicate state between controllers

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: None

  **Parallelization**: YES - Wave 2

  **References**:
  - Current: `src/controllers/image_controller.py:16-30`

  **Acceptance Criteria**:
  - [ ] Image loading still works through ImageNavigationWidget
  - [ ] MainController.state updates on image load
  - [ ] Existing tests still pass

  **Commit**: YES

- [ ] 8. **Add preview pipeline execution with debouncing**

  **What to do**:
  - Add `MainController.trigger_preview()` method
  - Use `QTimer` for 200ms debounce
  - Execute pipeline in background thread (QThreadPool)
  - Cache preview result in `AppState.preview_image`
  - Emit `preview_updated(np.ndarray)` signal

  **Must NOT do**:
  - Do NOT block UI thread during execution
  - Do NOT execute on every parameter change (debounce required)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: None

  **Parallelization**: YES - Wave 2

  **References**:
  - Pattern: `src/core/pipeline.py:35-56` (execute method)
  - Threading: See AGENTS.md threading guidelines

  **Acceptance Criteria**:
  - [ ] Debounce timer (200ms) prevents excessive execution
  - [ ] Execution happens in background thread
  - [ ] `preview_updated` signal emits result
  - [ ] Tests verify debouncing behavior

  **Commit**: YES

### Wave 3: Unified UI Widget

- [ ] 9. **Create UnifiedMainWidget with 3-panel splitter**

  **What to do**:
  - Create `src/ui/unified_main_widget.py`
  - Create `UnifiedMainWidget(QWidget)`:
    - QSplitter with 3 sections (left, center, right)
    - Left: initially hidden/empty placeholder
    - Center: ImageCanvas (always visible)
    - Right: initially hidden/empty placeholder
    - Methods: `set_left_panel(widget)`, `set_right_panel(widget)`

  **Must NOT do**:
  - Do NOT implement panel content yet (Task 10-11)
  - Do NOT use QStackedWidget

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`

  **Parallelization**: YES - Wave 3
  **Blocked By**: Task 5

  **References**:
  - Pattern: `src/ui/pipeline_view.py:228-246` (QSplitter setup)

  **Acceptance Criteria**:
  - [ ] Widget creates with 3-panel layout
  - [ ] Center panel always shows ImageCanvas
  - [ ] Left/right panels can be set dynamically
  - [ ] Tests: panel switching works

  **Commit**: YES

- [ ] 10. **Implement adaptive left panel**

  **What to do**:
  - Create `LeftPanelFactory` in unified widget
  - Phase `EMPTY`: hide left panel (or show placeholder)
  - Phase `IMAGE_LOADED`: show PipelineStackWidget (empty state)
  - Phase `NODES_ADDED`: show PipelineStackWidget (with nodes)
  - Connect to controller's `phase_changed` signal

  **Must NOT do**:
  - Do NOT recreate panel widgets on every phase change (reuse)
  - Do NOT show folder browser in unified flow (not needed)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`

  **Parallelization**: YES - Wave 3

  **Acceptance Criteria**:
  - [ ] Left panel hidden in EMPTY phase
  - [ ] Left panel shows pipeline stack in IMAGE_LOADED
  - [ ] Panel updates on phase change
  - [ ] Tests: phase transitions update left panel

  **Commit**: YES

- [ ] 11. **Implement adaptive right panel**

  **What to do**:
  - Create `RightPanelFactory`:
    - Phase `EMPTY`: hide
    - Phase `IMAGE_LOADED`: show PropertiesPanel (image metadata)
    - Phase `NODES_ADDED` + no selection: show PropertiesPanel
    - Phase `NODES_ADDED` + node selected: show NodePropertiesEditor
  - Connect to `selected_node_id_changed` signal

  **Must NOT do**:
  - Do NOT lose metadata when switching to node properties
  - Do NOT require manual refresh

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`

  **Parallelization**: YES - Wave 3

  **Acceptance Criteria**:
  - [ ] Right panel shows metadata initially
  - [ ] Right panel switches to node properties on selection
  - [ ] Returns to metadata on deselection
  - [ ] Tests: selection changes update right panel

  **Commit**: YES

- [ ] 12. **Integrate ImageCanvas as permanent center panel**

  **What to do**:
  - Use existing `ImageCanvas` in center panel
  - Connect `MainController.preview_updated` to `canvas.load_image()`
  - Handle empty state (no image loaded) with placeholder
  - Handle preview updates (processed image)

  **Must NOT do**:
  - Do NOT create multiple ImageCanvas instances
  - Do NOT reload original image on every preview (pass ndarray)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`

  **Parallelization**: YES - Wave 3

  **References**:
  - Current: `src/ui/image_canvas.py`
  - Pattern: `src/ui/image_navigation.py:187-200`

  **Acceptance Criteria**:
  - [ ] ImageCanvas always visible in center
  - [ ] Loads original image on image load
  - [ ] Shows preview on pipeline change
  - [ ] Tests: canvas updates on signals

  **Commit**: YES

- [ ] 13. **Connect panel state to controller signals**

  **What to do**:
  - Wire up all controller signals to UI updates:
    - `phase_changed` → update left/right panels
    - `selected_node_id_changed` → update right panel
    - `preview_updated` → update canvas
    - `pipeline_changed` → update left panel node list

  **Must NOT do**:
  - Do NOT create memory leaks (disconnect old connections)
  - Do NOT update UI from background threads

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: None

  **Parallelization**: YES - Wave 3

  **Acceptance Criteria**:
  - [ ] All controller signals connected
  - [ ] UI updates correctly on all state changes
  - [ ] Tests: signal → UI update chain works

  **Commit**: YES

### Wave 4: Pipeline Features

- [ ] 14. **Migrate drag-drop nodes from pipeline_view.py**

  **What to do**:
  - Copy `PipelineNodeWidget` class to new location
  - Copy drag-drop logic (mousePressEvent, mouseMoveEvent, dropEvent)
  - Adapt to work with `AppState.pipeline` instead of internal dict
  - Keep visual styling intact

  **Must NOT do**:
  - Do NOT break existing drag-drop behavior
  - Do NOT lose visual styling

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `frontend-ui-ux`

  **Parallelization**: YES - Wave 4
  **Blocked By**: Task 9, 10

  **References**:
  - Source: `src/ui/pipeline_view.py:71-195` (PipelineNodeWidget)
  - Logic: `src/ui/pipeline_view.py:381-426` (drop handling)

  **Acceptance Criteria**:
  - [ ] Nodes render with same styling
  - [ ] Drag-drop works between nodes
  - [ ] Connecting lines render correctly
  - [ ] Tests: drag-drop integration

  **Commit**: YES

- [ ] 15. **Enforce fixed Input/PHANTAST nodes**

  **What to do**:
  - In `PipelineNodeWidget.__init__`:
    - Set `is_draggable = False` for type 'input' or 'output'
    - Set `is_removable = False` for fixed types
    - Hide delete context menu for fixed nodes
    - Disable toggle switch for fixed nodes (or hide it)
  - In drop validation:
    - Reject drops at index 0 (before input)
    - Reject drops at last index (after output)

  **Must NOT do**:
  - Do NOT allow deleting fixed nodes
  - Do NOT allow toggling fixed nodes off

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: None

  **Parallelization**: YES - Wave 4

  **References**:
  - Current logic: `src/ui/pipeline_view.py:84-85`
  - Validation: `src/ui/pipeline_view.py:410-414`

  **Acceptance Criteria**:
  - [ ] Input node cannot be dragged
  - [ ] Output node cannot be dragged
  - [ ] Fixed nodes have no delete menu
  - [ ] Fixed nodes cannot be disabled
  - [ ] Tests: all fixed node constraints

  **Commit**: YES

- [ ] 16. **Add "Add Step" UI between fixed nodes**

  **What to do**:
  - When pipeline has only Input → Output (no middle nodes):
    - Show "+ Add Step" button between them
    - Or show placeholder text "Drag nodes here"
  - Clicking opens menu to add: Grayscale, GaussianBlur, CLAHE
  - After adding, show actual node widgets

  **Must NOT do**:
  - Do NOT show placeholder when middle nodes exist
  - Do NOT allow adding before Input or after Output

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`

  **Parallelization**: YES - Wave 4

  **Acceptance Criteria**:
  - [ ] Placeholder shows when no middle nodes
  - [ ] Clicking adds node between Input/Output
  - [ ] Menu lists available node types
  - [ ] Tests: add node flow

  **Commit**: YES

- [ ] 17. **Create node-specific property editors**

  **What to do**:
  - Create editors for each node type:
    - `GrayscaleEditor`: no parameters (informational only)
    - `GaussianBlurEditor`: kernel_size spinbox, sigma spinbox
    - `CLAHEEditor`: clip_limit spinbox, grid_size spinbox
    - `PHANTASTEditor`: sigma spinbox, epsilon spinbox
  - Each editor emits `value_changed(param_name, value)`
  - Update `AppState.pipeline.nodes[].parameters` on change

  **Must NOT do**:
  - Do NOT create editors for fixed nodes (Input has no params)
  - Do NOT allow invalid parameter values

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`

  **Parallelization**: YES - Wave 4

  **References**:
  - Pattern: `src/ui/pipeline_view.py:485-517`
  - Parameters: `src/core/steps/` (see GaussianBlurStep, etc.)

  **Acceptance Criteria**:
  - [ ] Each node type has matching editor
  - [ ] Editor shows current parameter values
  - [ ] Changing value updates pipeline state
  - [ ] Tests: each editor type

  **Commit**: YES

- [ ] 18. **Connect toggle switches to node enabled state**

  **What to do**:
  - Connect `PipelineNodeWidget.toggled` signal to controller
  - Update `node.enabled` in AppState
  - Trigger preview update (debounced)
  - Visual feedback: disabled nodes grayed out

  **Must NOT do**:
  - Do NOT allow toggling fixed nodes
  - Do NOT skip preview update on toggle

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**: YES - Wave 4

  **Acceptance Criteria**:
  - [ ] Toggle updates node.enabled
  - [ ] Disabled nodes visually distinct
  - [ ] Preview updates when toggled
  - [ ] Tests: toggle → state → preview chain

  **Commit**: YES

- [ ] 19. **Implement real-time preview updates**

  **What to do**:
  - Connect all change signals to `trigger_preview()`:
    - Node reordering
    - Node toggled
    - Parameter changed
  - Ensure debouncing (200ms) prevents excessive execution
  - Show loading indicator during processing
  - Handle errors gracefully (log, don't crash)

  **Must NOT do**:
  - Do NOT block UI during preview generation
  - Do NOT execute pipeline synchronously

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: None

  **Parallelization**: YES - Wave 4

  **References**:
  - Task 8 (debounced execution already implemented)

  **Acceptance Criteria**:
  - [ ] Reordering triggers preview
  - [ ] Toggle triggers preview
  - [ ] Parameter change triggers preview
  - [ ] All debounced 200ms
  - [ ] Tests: preview trigger scenarios

  **Commit**: YES

### Wave 5: Cleanup & Integration

- [ ] 20. **Refactor MainWindow to use UnifiedMainWidget**

  **What to do**:
  - Replace QStackedWidget content with UnifiedMainWidget
  - Keep header bar (logo, title, avatar)
  - Remove navigation buttons (Image Loading, Pipeline, Batch)
  - Keep status bar
  - MainWindow owns MainController and wires it to UnifiedMainWidget

  **Must NOT do**:
  - Do NOT remove header or status bar
  - Do NOT break existing tests completely (update them)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: None

  **Parallelization**: YES - Wave 5
  **Blocked By**: Task 9-19

  **References**:
  - Current: `src/ui/main_window.py`

  **Acceptance Criteria**:
  - [ ] MainWindow uses UnifiedMainWidget
  - [ ] No more view switching
  - [ ] Header and status bar intact
  - [ ] Tests updated and passing

  **Commit**: YES

- [ ] 21. **Remove QStackedWidget and navigation buttons**

  **What to do**:
  - Remove QStackedWidget from MainWindow
  - Remove nav buttons (btn_img, btn_pipe, btn_exec)
  - Remove QButtonGroup
  - Remove switch_view() method
  - Update stylesheets if needed

  **Must NOT do**:
  - Do NOT leave dead code
  - Do NOT break imports

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**: YES - Wave 5

  **Acceptance Criteria**:
  - [ ] No QStackedWidget in MainWindow
  - [ ] No nav buttons in header
  - [ ] No view switching methods
  - [ ] Clean compile, tests pass

  **Commit**: YES

- [ ] 22. **Remove/deprecate BatchExecutionIntegrationWidget**

  **What to do**:
  - Mark `BatchExecutionIntegrationWidget` as deprecated
  - Or remove if not used elsewhere
  - Update any references
  - Functionality merged into unified flow

  **Must NOT do**:
  - Do NOT break shell/ reference app if it uses this

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**: YES - Wave 5

  **Acceptance Criteria**:
  - [ ] Widget deprecated/removed
  - [ ] No broken references
  - [ ] Tests updated

  **Commit**: YES

- [ ] 23. **Update keyboard shortcuts**

  **What to do**:
  - Remove F1/F2/F3 (view switching no longer applies)
  - Keep Ctrl+O (Open Image)
  - Keep Ctrl+Shift+O (Open Folder)
  - Keep Ctrl+S (Save)
  - Keep Ctrl+Q (Quit)
  - Add Ctrl+R (Run Pipeline) - optional
  - Add Delete (Remove selected node) - optional

  **Must NOT do**:
  - Do NOT keep obsolete shortcuts

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**: YES - Wave 5

  **Acceptance Criteria**:
  - [ ] F1/F2/F3 removed
  - [ ] Essential shortcuts still work
  - [ ] Tests updated

  **Commit**: YES

- [ ] 24. **Update main.py entry point**

  **What to do**:
  - Update `src/main.py` to:
    - Create MainController
    - Create MainWindow with UnifiedMainWidget
    - Wire up controller to window
  - Remove deprecated controller creation

  **Must NOT do**:
  - Do NOT break app launch

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**: YES - Wave 5

  **Acceptance Criteria**:
  - [ ] App launches successfully
  - [ ] Controller and window wired up
  - [ ] No deprecation warnings

  **Commit**: YES

- [ ] 25. **Create comprehensive integration tests**

  **What to do**:
  - Test full workflow:
    1. Launch app (EMPTY phase)
    2. Load image (IMAGE_LOADED phase)
    3. Add nodes (NODES_ADDED phase)
    4. Reorder nodes
    5. Toggle nodes
    6. Edit parameters
    7. Verify preview updates
  - Test edge cases:
    - Try to drag fixed nodes (should fail)
    - Try to delete fixed nodes (should fail)
    - Empty pipeline (placeholder visible)

  **Must NOT do**:
  - Do NOT skip edge case testing

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None

  **Parallelization**: YES - Wave 5

  **Acceptance Criteria**:
  - [ ] End-to-end workflow test passes
  - [ ] Edge case tests pass
  - [ ] 20+ new tests added
  - [ ] All 100+ tests passing

  **Commit**: YES

### Wave FINAL: Verification

- [ ] F1. **Code quality review**

  **What to do**:
  - Run linter (ruff/flake8)
  - Check type hints (mypy/pyright)
  - Check import organization
  - Verify no dead code

  **Acceptance Criteria**:
  - [ ] Zero linter errors
  - [ ] Type hints complete
  - [ ] No unused imports

- [ ] F2. **Integration tests - full workflow**

  **What to do**:
  - Run complete workflow test
  - Verify all phase transitions
  - Test with real image files

  **Acceptance Criteria**:
  - [ ] All integration tests pass
  - [ ] No regressions in existing tests

- [ ] F3. **UI QA - drag-drop, toggles, properties**

  **What to do**:
  - Manual verification (agent-assisted):
    - Drag middle nodes (should work)
    - Try drag fixed nodes (should not work)
    - Toggle middle nodes (should work)
    - Try toggle fixed nodes (should not work)
    - Edit parameters (should update preview)

  **Acceptance Criteria**:
  - [ ] All interactions work as specified
  - [ ] Visual feedback correct

- [ ] F4. **Performance QA - preview responsiveness**

  **What to do**:
  - Measure preview update latency
  - Verify no UI blocking
  - Test with large images

  **Acceptance Criteria**:
  - [ ] Preview updates within 500ms of change
  - [ ] UI remains responsive during processing
  - [ ] Debouncing prevents excessive CPU

---

## Commit Strategy

- **Wave 1**: Group tasks 1-2, 3, 4 into 3 commits
- **Wave 2**: Group tasks 5-6, 7, 8 into 3 commits
- **Wave 3**: Group tasks 9-10, 11-13 into 2-3 commits
- **Wave 4**: Individual commits for tasks 14-19 (6 commits)
- **Wave 5**: Group tasks 20-21, 22-23, 24-25 into 3 commits

**Total**: ~15-17 commits over 5 waves

---

## Success Criteria

### Verification Commands
```bash
# All tests pass
python -m pytest tests/ -v

# App launches
python -m src.main

# Linter clean
python -m ruff check src/
```

### Final Checklist
- [ ] Single window throughout workflow (no view switching)
- [ ] Fixed Input node at position 0 (not draggable/removable)
- [ ] Fixed PHANTAST node at final position (not draggable/removable)
- [ ] Middle nodes (Grayscale, GaussianBlur, CLAHE) draggable between fixed nodes
- [ ] Toggle switches for middle nodes work
- [ ] Right panel shows node properties when node selected
- [ ] Real-time preview updates with 200ms debounce
- [ ] All 100+ tests passing
- [ ] Dark theme consistent
- [ ] No UI blocking during processing

### Questions for User (Answer Before Starting)

1. **Batch execution results**: Should batch results table appear in right panel, modal dialog, or separate view?

2. **Preview debounce**: Is 200ms appropriate, or prefer different timing?

3. **Initial pipeline**: Start with Input → Output (empty), or Input → Grayscale → Output (smart default)?

4. **Keyboard shortcuts**: Repurpose F1/F2/F3 for workflow actions, or remove entirely?

5. **Project save**: Single "Save Project" capturing pipeline + images, or separate save actions?

---

*Plan created by Prometheus. Execute with `/start-work unified-interface-refactor`*
