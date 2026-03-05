# Unified Interface - Simplified Plan (No Execution)

## TL;DR

> **Unified single-window interface with pipeline building only.**
> **Stop before actual pipeline execution - just the UI and state management.**
> 
> **Deliverables**:
> - Unified MainWindow (no view switching)
> - Fixed Input/Output nodes with draggable middle nodes
> - Add/remove/reorder nodes with drag-drop
> - Toggle nodes on/off
> - Edit node parameters in right panel
> - 200ms debounce mechanism (execution stubbed)
> 
> **Estimated Effort**: Medium (3-4 days)
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: State → Controller → Unified UI → Node Features

---

## Scope

### IN Scope
- Single unified window throughout workflow
- Left panel: Pipeline stack (Input → [middle nodes] → Output)
- Center panel: ImageCanvas (shows loaded image)
- Right panel: Node properties editor (when node selected)
- Add nodes between Input/Output (Grayscale, GaussianBlur, CLAHE)
- Drag-drop reordering (Input fixed at start, Output fixed at end)
- Toggle switches for middle nodes (on/off)
- Parameter editing in right panel
- 200ms debounce on changes (logs "would execute" instead of actual execution)
- Initial pipeline: Input → Output (empty)

### OUT of Scope (Phase 2 - Execution)
- Actual pipeline execution/processing
- Real-time preview updates
- Batch execution
- Results display
- Save/load project

---

## Execution Strategy

### Wave 1: Foundation (State & Model)

```
Wave 1 (Independent, can start immediately):
├── Task 1: Create AppState with workflow phases
├── Task 2: Add pipeline reordering methods to PipelineModel
└── Task 3: Create node parameter schemas
```

### Wave 2: Controller (Depends on Wave 1)

```
Wave 2:
├── Task 4: Create MainController with AppState
├── Task 5: Implement phase transitions (EMPTY → IMAGE_LOADED)
└── Task 6: Add debounced change handler (stubbed execution)
```

### Wave 3: Unified UI (Depends on Wave 2)

```
Wave 3:
├── Task 7: Create UnifiedMainWidget with 3-panel layout
├── Task 8: Implement adaptive left panel (pipeline stack)
├── Task 9: Implement right panel (node properties)
└── Task 10: Integrate ImageCanvas in center
```

### Wave 4: Node Features (Depends on Wave 3)

```
Wave 4:
├── Task 11: Migrate drag-drop nodes
├── Task 12: Enforce fixed Input/Output nodes
├── Task 13: Add "Add Node" UI between fixed nodes
├── Task 14: Create node property editors
├── Task 15: Connect toggle switches
└── Task 16: Wire up 200ms debounce
```

### Wave 5: Integration (Depends on Wave 4)

```
Wave 5:
├── Task 17: Refactor MainWindow to use UnifiedMainWidget
├── Task 18: Remove QStackedWidget and nav buttons
├── Task 19: Update main.py entry point
└── Task 20: Create integration tests
```

---

## TODOs

### Wave 1: Foundation

- [ ] 1. **Create AppState with workflow phases**

  **What to do**:
  - Create `src/models/app_state.py`
  - Define `WorkflowPhase` enum: `EMPTY`, `IMAGE_LOADED`
  - Create `AppState` dataclass with:
    - `current_image: Optional[ImageSession]`
    - `pipeline: Pipeline`
    - `selected_node_id: Optional[str]`
    - `workflow_phase: WorkflowPhase`
  - Add QObject wrapper with `state_changed` signal

  **Acceptance Criteria**:
  - [ ] Can instantiate AppState
  - [ ] WorkflowPhase enum works
  - [ ] Tests: `tests/models/test_app_state.py`

- [ ] 2. **Add pipeline reordering methods**

  **What to do**:
  - Extend `Pipeline` class in `src/models/pipeline_model.py`:
    - `move_node(node_id, new_index)` - with validation
    - `can_move_node(node_id, new_index)` - checks bounds
    - `insert_node_between(node, after_node_id)`
  - Fixed node protection: type 'input' and 'output' cannot move

  **Acceptance Criteria**:
  - [ ] Middle nodes can be moved
  - [ ] Fixed nodes rejected
  - [ ] Tests cover move/insert

- [ ] 3. **Create node parameter schemas**

  **What to do**:
  - Define parameter specs for each node type:
    - `grayscale`: {} (no params)
    - `gaussian_blur`: {kernel_size: int, sigma: float}
    - `clahe`: {clip_limit: float, grid_size: tuple}
    - `phantast`: {sigma: float, epsilon: float}
  - Create `src/core/parameter_schemas.py`

  **Acceptance Criteria**:
  - [ ] Schemas defined for all 4 node types
  - [ ] Default values specified
  - [ ] Validation functions

### Wave 2: Controller

- [ ] 4. **Create MainController with AppState**

  **What to do**:
  - Create `src/controllers/main_controller.py`
  - `MainController(QObject)`:
    - `state: AppState`
    - `load_image(filepath)` - transitions to IMAGE_LOADED
    - `add_node(node_type)` - inserts between Input/Output
    - `remove_node(node_id)` - removes middle node
    - `reorder_node(node_id, new_index)`
    - `select_node(node_id)` - updates selected_node_id
    - `update_node_parameter(node_id, param, value)`
    - Signals: `image_loaded`, `phase_changed`, `pipeline_changed`, `node_selected`

  **Acceptance Criteria**:
  - [ ] Controller manages state
  - [ ] Signals fire on changes
  - [ ] Tests verify behavior

- [ ] 5. **Implement phase transitions**

  **What to do**:
  - `load_image()`: EMPTY → IMAGE_LOADED
  - Create default pipeline (Input → Output)
  - Emit `phase_changed`

  **Acceptance Criteria**:
  - [ ] Load image triggers phase change
  - [ ] Pipeline initialized correctly
  - [ ] Tests pass

- [ ] 6. **Add debounced change handler**

  **What to do**:
  - Add `on_pipeline_changed()` method
  - Use `QTimer.singleShot(200, self._execute_stub)`
  - `_execute_stub()` logs "Would execute pipeline with X nodes"
  - Connect to: reorder, toggle, parameter change signals

  **Acceptance Criteria**:
  - [ ] 200ms debounce works
  - [ ] Logs on change
  - [ ] Tests verify debounce

### Wave 3: Unified UI

- [ ] 7. **Create UnifiedMainWidget with 3-panel layout**

  **What to do**:
  - Create `src/ui/unified_main_widget.py`
  - `UnifiedMainWidget(QWidget)`:
    - QSplitter with left/center/right
    - Left: PipelineStackWidget
    - Center: ImageCanvas
    - Right: PropertiesPanel

  **Acceptance Criteria**:
  - [ ] Widget creates with 3 panels
  - [ ] ImageCanvas in center
  - [ ] Tests verify layout

- [ ] 8. **Implement adaptive left panel**

  **What to do**:
  - Phase EMPTY: hide or show placeholder
  - Phase IMAGE_LOADED: show PipelineStackWidget
  - Update on phase_changed signal

  **Acceptance Criteria**:
  - [ ] Hidden initially
  - [ ] Shows pipeline after image load
  - [ ] Tests verify adaptation

- [ ] 9. **Implement right panel**

  **What to do**:
  - Phase EMPTY: hide
  - Phase IMAGE_LOADED + no selection: show image metadata
  - Phase IMAGE_LOADED + node selected: show NodePropertiesEditor
  - Update on node_selected signal

  **Acceptance Criteria**:
  - [ ] Shows metadata initially
  - [ ] Shows properties on selection
  - [ ] Tests verify switching

- [ ] 10. **Integrate ImageCanvas**

  **What to do**:
  - Use existing ImageCanvas
  - Connect `image_loaded` signal to load image
  - Keep canvas persistent

  **Acceptance Criteria**:
  - [ ] Canvas loads image on signal
  - [ ] Canvas stays visible
  - [ ] Tests pass

### Wave 4: Node Features

- [ ] 11. **Migrate drag-drop nodes**

  **What to do**:
  - Copy PipelineNodeWidget from pipeline_view.py
  - Copy drag-drop event handlers
  - Adapt to use AppState.pipeline

  **Acceptance Criteria**:
  - [ ] Nodes render correctly
  - [ ] Drag-drop works
  - [ ] Tests pass

- [ ] 12. **Enforce fixed Input/Output**

  **What to do**:
  - In PipelineNodeWidget:
    - `is_draggable = node.type not in ['input', 'output']`
    - `is_removable = node.type not in ['input', 'output']`
    - Hide toggle for fixed nodes
  - In drop validation:
    - Reject drops at index 0 or len-1

  **Acceptance Criteria**:
  - [ ] Fixed nodes not draggable
  - [ ] Fixed nodes not removable
  - [ ] Fixed nodes always enabled
  - [ ] Tests verify constraints

- [ ] 13. **Add "Add Node" UI**

  **What to do**:
  - When only Input → Output (no middle):
    - Show "+ Add Step" button between them
  - Click opens menu: Grayscale, GaussianBlur, CLAHE
  - After add, show node widget

  **Acceptance Criteria**:
  - [ ] Placeholder shows when empty
  - [ ] Menu opens on click
  - [ ] Node adds correctly
  - [ ] Tests verify flow

- [ ] 14. **Create node property editors**

  **What to do**:
  - Create `src/ui/property_editors/`:
    - `GrayscaleEditor` - informational (no params)
    - `GaussianBlurEditor` - kernel_size, sigma spinboxes
    - `CLAHEEditor` - clip_limit, grid_size spinboxes
    - `PHANTASTEditor` - sigma, epsilon spinboxes
  - Each emits `value_changed(param, value)`

  **Acceptance Criteria**:
  - [ ] Each node type has editor
  - [ ] Editors show current values
  - [ ] Changes emit signals
  - [ ] Tests verify editors

- [ ] 15. **Connect toggle switches**

  **What to do**:
  - Add toggle to middle nodes (not fixed)
  - Connect to `node.enabled` in AppState
  - Visual: disabled nodes grayed out

  **Acceptance Criteria**:
  - [ ] Toggle updates enabled state
  - [ ] Visual feedback on toggle
  - [ ] Fixed nodes have no toggle
  - [ ] Tests verify toggling

- [ ] 16. **Wire up 200ms debounce**

  **What to do**:
  - Connect all change signals to debounced handler:
    - Node added/removed
    - Node reordered
    - Node toggled
    - Parameter changed
  - Log "Would execute pipeline" after 200ms

  **Acceptance Criteria**:
  - [ ] All changes trigger debounce
  - [ ] 200ms delay verified
  - [ ] Logs show would-be execution
  - [ ] Tests verify debouncing

### Wave 5: Integration

- [ ] 17. **Refactor MainWindow**

  **What to do**:
  - Replace QStackedWidget with UnifiedMainWidget
  - Keep header, remove nav buttons
  - Keep status bar
  - Wire MainController

  **Acceptance Criteria**:
  - [ ] Uses UnifiedMainWidget
  - [ ] No view switching
  - [ ] Tests updated

- [ ] 18. **Remove QStackedWidget**

  **What to do**:
  - Remove nav buttons
  - Remove switch_view method
  - Clean up stylesheets

  **Acceptance Criteria**:
  - [ ] No stacked widget
  - [ ] No nav buttons
  - [ ] Clean compile

- [ ] 19. **Update main.py**

  **What to do**:
  - Create MainController
  - Create MainWindow with UnifiedMainWidget
  - Wire controller to window

  **Acceptance Criteria**:
  - [ ] App launches
  - [ ] Controller connected
  - [ ] No warnings

- [ ] 20. **Create integration tests**

  **What to do**:
  - Test full workflow:
    1. Launch (EMPTY)
    2. Load image (IMAGE_LOADED)
    3. Add node
    4. Reorder node
    5. Toggle node
    6. Edit parameter
  - Test fixed node constraints

  **Acceptance Criteria**:
  - [ ] End-to-end test passes
  - [ ] Constraint tests pass
  - [ ] 15+ new tests
  - [ ] All tests passing

---

## Verification

### Test Commands
```bash
python -m pytest tests/ -v
python -m src.main
```

### Success Criteria
- [ ] Single window, no view switching
- [ ] Input fixed at position 0
- [ ] Output fixed at final position
- [ ] Middle nodes draggable between fixed nodes
- [ ] Can add nodes (Grayscale, GaussianBlur, CLAHE)
- [ ] Can remove middle nodes
- [ ] Can toggle middle nodes on/off
- [ ] Right panel shows node properties
- [ ] 200ms debounce on all changes
- [ ] Logs "would execute" (no actual execution yet)
- [ ] All tests passing

---

*Simplified plan ready. Execute with `/start-work unified-interface-simplified`*
