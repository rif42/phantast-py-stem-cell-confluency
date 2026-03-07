# Plan: Node-Based Pipeline System with CLAHE Processing

## TL;DR

> **Quick Summary**: Add a node-based pipeline system to the existing PyQt6 application. Users can click "Add" to see a popup with processing options (CLAHE, Grayscale, Crop), select CLAHE to add a functional node with toggle and drag-reorder capabilities. Grayscale and Crop are placeholders only.
> 
> **Deliverables**:
> - Step registry system in `src/core/steps/`
> - CLAHE processing step (functional)
> - Grayscale and Crop step stubs (placeholders)
> - Pipeline view integration into main window
> - Dynamic parameter UI in right panel
> 
> **Estimated Effort**: Short (4-6 tasks)
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Step system → CLAHE step → Integration → Dynamic UI

---

## Context

### Original Request
User wants to add processing nodes to the pipeline:
1. Add button on left sidebar → popup list
2. Popup options: CLAHE (functional), Grayscale (placeholder), Crop (placeholder)
3. CLAHE node: active/deactivate toggle, draggable reorder
4. "Thats it" - focused MVP scope

### Interview Summary
**Key Discussions**:
- Only CLAHE needs full implementation
- Grayscale and Crop are placeholders (no processing logic)
- Drag-drop and toggle already exist in codebase (partially implemented)
- Integration into main window needed

**Research Findings**:
- `pipeline_view.py` already has: drag-drop (lines 180-202), toggle switch (lines 20-47), popup menu (lines 276-288)
- `pipeline_model.py` has data models for nodes
- `CLAHE.py` has standalone CLAHE implementation
- Drag-drop already implemented using `QDrag` with `QMimeData`
- No `src/core/steps/` directory exists yet

### Metis Review
**Identified Gaps** (addressed):
- Need step registration pattern (decorator vs manual)
- Need parameter schema for dynamic UI generation
- Need to replace hardcoded CLAHE UI (lines 521-525) with dynamic generation
- Need main window integration
- Need serialization for persistence
- Need to explicitly exclude: undo/redo, real-time preview, node branching, complex validation

---

## Work Objectives

### Core Objective
Implement a node-based pipeline system where users can add, toggle, and reorder CLAHE processing nodes via the existing UI framework.

### Concrete Deliverables
- `src/core/steps/__init__.py` with `@register_step` decorator
- `src/core/steps/clahe_step.py` - functional CLAHE processing
- `src/core/steps/grayscale_step.py` - placeholder stub
- `src/core/steps/crop_step.py` - placeholder stub
- Updated `main_window.py` with pipeline view integration
- Updated `pipeline_view.py` with dynamic parameter UI
- Working add/reorder/toggle flow

### Definition of Done
- [ ] Click "Add" → popup shows CLAHE, Grayscale, Crop options
- [ ] Select CLAHE → new node appears with toggle (on by default)
- [ ] Drag node → reorders in the list
- [ ] Click node → right panel shows CLAHE parameters (clip_limit, grid_size)
- [ ] Change parameter → stored in node
- [ ] Toggle off → node shows disabled state

### Must Have
- `@register_step` decorator for step registration
- CLAHE step with parameters: clip_limit (0.1-10.0, default 2.0), grid_size (2-32 even, default 8)
- Dynamic parameter UI generation in right panel
- Main window integration showing pipeline view
- Grayscale and Crop registered as NO-OP placeholders

### Must NOT Have (Guardrails)
- **NO** undo/redo system (out of scope)
- **NO** real-time image preview (placeholder only)
- **NO** node branching/merging (linear pipeline only)
- **NO** complex validation beyond type/range clamping
- **NO** auto-optimization for CLAHE
- **NO** plugin system or dynamic imports
- **NO** database persistence (JSON only)
- **NO** custom parameter widgets beyond standard types

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO - No test framework set up
- **Automated tests**: NO - Skip for this short task
- **Agent-Executed QA**: YES - Manual verification via PyQt6

### QA Policy
Every task includes agent-executed QA scenarios using Playwright (for UI) or interactive_bash (for CLI). No human verification required.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - Infrastructure):
├── Task 1: Create step registration system
├── Task 2: Create CLAHE step implementation
└── Task 3: Create Grayscale and Crop placeholder steps

Wave 2 (After Wave 1 - Integration):
├── Task 4: Integrate pipeline view into main window
├── Task 5: Populate available_nodes from registry
└── Task 6: Implement dynamic parameter UI in right panel
```

### Dependency Matrix

- **1**: — — 2, 3, 1
- **2**: 1 — 4, 5, 2
- **3**: 1 — 4, 5, 2
- **4**: 2, 3 — 5, 6, 3
- **5**: 2, 3, 4 — 6, 3
- **6**: 4, 5 — 4

### Agent Dispatch Summary

- **1**: **3** - T1 → `quick`, T2 → `quick`, T3 → `quick`
- **2**: **3** - T4 → `visual-engineering`, T5 → `quick`, T6 → `visual-engineering`

---

## TODOs

- [ ] 1. Create step registration system in `src/core/steps/`

  **What to do**:
  - Create directory `src/core/steps/`
  - Create `src/core/steps/__init__.py` with `@register_step` decorator
  - Create `src/core/steps/base.py` with `StepParameter` dataclass
  - `STEP_REGISTRY` dict to hold registered steps
  - Each step module must define: STEP_NAME, STEP_DESCRIPTION, STEP_ICON, STEP_PARAMETERS, process() function

  **Must NOT do**:
  - NO plugin system or dynamic imports
  - NO complex metaclasses
  - NO validation beyond basic type hints

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: Straightforward decorator pattern, no complex logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 2 and 3)
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 2, 3, 4, 5, 6
  - **Blocked By**: None (can start immediately)

  **References**:
  - Pattern: Standard Python decorator registry pattern
  - `src/models/pipeline_model.py:PipelineNode.parameters` - stores parameters dict
  - `src/ui/pipeline_view.py:PipelineConstructionWidget.__init__` - loads available_nodes

  **Acceptance Criteria**:
  - [ ] `src/core/steps/__init__.py` exists with `STEP_REGISTRY = {}`
  - [ ] `@register_step` decorator adds decorated class/function to registry
  - [ ] `StepParameter` dataclass has: name, type, default, min, max, step
  - [ ] Test: `from src.core.steps import STEP_REGISTRY; assert isinstance(STEP_REGISTRY, dict)`

  **QA Scenarios**:
  ```
  Scenario: Registry works correctly
    Tool: Bash (python REPL)
    Preconditions: File created
    Steps:
      1. Run: python -c "from src.core.steps import STEP_REGISTRY, register_step; print('Registry:', STEP_REGISTRY); assert isinstance(STEP_REGISTRY, dict)"
    Expected Result: No errors, empty dict printed
    Evidence: .sisyphus/evidence/task-1-registry-ok.txt
  ```

  **Commit**: YES
  - Message: `feat(steps): Add step registration system with @register_step decorator`
  - Files: `src/core/steps/__init__.py`, `src/core/steps/base.py`

- [ ] 2. Create CLAHE processing step

  **What to do**:
  - Create `src/core/steps/clahe_step.py`
  - Import and adapt logic from root `CLAHE.py`
  - Define STEP_NAME = "clahe", STEP_DESCRIPTION, STEP_ICON = "⚙️"
  - Define STEP_PARAMETERS with clip_limit and grid_size
  - Implement `process(image, **params)` function that returns processed image
  - Use `@register_step` decorator

  **Must NOT do**:
  - NO auto-optimization (out of scope)
  - NO GUI code in step (pure processing)
  - NO file I/O (accept/return numpy arrays)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: Adapting existing code, straightforward function

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 1 and 3)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 4, 5, 6
  - **Blocked By**: Task 1 (needs register_step)

  **References**:
  - `CLAHE.py:apply_clahe()` - logic to adapt
  - `src/core/steps/__init__.py` - @register_step decorator
  - Pattern: Keep pure Python, no PyQt imports

  **Acceptance Criteria**:
  - [ ] `clahe_step.py` exists with @register_step
  - [ ] `STEP_PARAMETERS` defines clip_limit (float, 0.1-10.0, default 2.0, step 0.1)
  - [ ] `STEP_PARAMETERS` defines grid_size (int, 2-32, default 8, step 2)
  - [ ] `process(image, clip_limit, grid_size)` applies CLAHE using cv2
  - [ ] Test: Import adds 'clahe' to STEP_REGISTRY

  **QA Scenarios**:
  ```
  Scenario: CLAHE step is registered
    Tool: Bash (python REPL)
    Preconditions: Task 1 complete
    Steps:
      1. Run: python -c "from src.core.steps import STEP_REGISTRY; from src.core.steps.clahe_step import *; print('CLAHE in registry:', 'clahe' in STEP_REGISTRY)"
    Expected Result: True printed
    Evidence: .sisyphus/evidence/task-2-clahe-registered.txt

  Scenario: CLAHE process function works
    Tool: Bash (python REPL)
    Preconditions: Task 1 complete
    Steps:
      1. Run: python -c "import numpy as np; from src.core.steps.clahe_step import process; img = np.random.randint(0, 255, (100, 100), dtype=np.uint8); result = process(img, clip_limit=2.0, grid_size=8); print('Output shape:', result.shape); print('Output dtype:', result.dtype)"
    Expected Result: Shape (100, 100), dtype uint8
    Evidence: .sisyphus/evidence/task-2-clahe-process.txt
  ```

  **Commit**: YES
  - Message: `feat(steps): Add CLAHE processing step with parameters`
  - Files: `src/core/steps/clahe_step.py`

- [ ] 3. Create Grayscale and Crop placeholder steps

  **What to do**:
  - Create `src/core/steps/grayscale_step.py` with NO-OP process() function
  - Create `src/core/steps/crop_step.py` with NO-OP process() function
  - Both registered with @register_step
  - Proper STEP_NAME, STEP_DESCRIPTION, STEP_ICON
  - Empty or minimal STEP_PARAMETERS

  **Must NOT do**:
  - NO actual processing logic (placeholders only)
  - NO complex parameter definitions

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: Copy-paste pattern from CLAHE, minimal logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 1 and 2)
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 4, 5
  - **Blocked By**: Task 1 (needs register_step)

  **References**:
  - `src/core/steps/clahe_step.py` - copy pattern
  - `src/core/steps/__init__.py` - @register_step decorator

  **Acceptance Criteria**:
  - [ ] `grayscale_step.py` exists with process() that returns input unchanged
  - [ ] `crop_step.py` exists with process() that returns input unchanged
  - [ ] Both registered in STEP_REGISTRY
  - [ ] Test: 'grayscale' and 'crop' keys exist in STEP_REGISTRY

  **QA Scenarios**:
  ```
  Scenario: Placeholder steps registered
    Tool: Bash (python REPL)
    Preconditions: Tasks 1, 2 complete
    Steps:
      1. Run: python -c "from src.core.steps import STEP_REGISTRY; from src.core.steps.grayscale_step import *; from src.core.steps.crop_step import *; print('grayscale:', 'grayscale' in STEP_REGISTRY); print('crop:', 'crop' in STEP_REGISTRY)"
    Expected Result: Both True
    Evidence: .sisyphus/evidence/task-3-placeholders-registered.txt
  ```

  **Commit**: YES
  - Message: `feat(steps): Add Grayscale and Crop placeholder steps`
  - Files: `src/core/steps/grayscale_step.py`, `src/core/steps/crop_step.py`

- [ ] 4. Integrate pipeline view into main window

  **What to do**:
  - Modify `src/ui/main_window.py` to include PipelineConstructionWidget
  - Create Pipeline model and controller
  - Use QSplitter or tab interface to show both image navigation and pipeline
  - Or replace image navigation with pipeline view (simpler)
  - Ensure pipeline view is visible when app launches

  **Must NOT do**:
  - NO complex view switching logic (keep it simple)
  - NO attempt to show both simultaneously unless using splitter

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Reason**: PyQt6 UI layout, widget integration
  - **Skills**: `frontend-ui-ux` (for layout and styling)

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Tasks 1, 2, 3 (needs step system)

  **References**:
  - `src/ui/main_window.py:MainWindow.load_views()` - where to add pipeline
  - `src/ui/pipeline_view.py:PipelineConstructionWidget` - widget to embed
  - `src/controllers/pipeline_controller.py` - may need updates
  - Pattern: Similar to image navigation MVC setup (lines 76-80)

  **Acceptance Criteria**:
  - [ ] MainWindow creates PipelineConstructionWidget
  - [ ] Pipeline view visible when app launches
  - [ ] Can import steps without errors

  **QA Scenarios**:
  ```
  Scenario: Pipeline view loads in main window
    Tool: interactive_bash (tmux)
    Preconditions: All previous tasks complete
    Steps:
      1. Run: python src/main.py
      2. Wait for window to appear (2s)
      3. Check that pipeline view with "Add" button is visible
      4. Press Ctrl+C to exit
    Expected Result: Window opens showing pipeline construction UI
    Evidence: .sisyphus/evidence/task-4-window-loads.png (screenshot)
  ```

  **Commit**: YES
  - Message: `feat(ui): Integrate pipeline view into main window`
  - Files: `src/ui/main_window.py`

- [ ] 5. Populate available_nodes from step registry

  **What to do**:
  - Modify `PipelineConstructionWidget._load_available_nodes()` (around line 227)
  - Instead of loading from JSON, import from `src.core.steps.STEP_REGISTRY`
  - Create menu items for each registered step
  - On click, create PipelineNode with proper type and parameters
  - Wire up to controller.add_node()

  **Must NOT do**:
  - NO hardcoded node list (must use registry)
  - NO JSON file loading for node definitions

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: Hooking up existing code, straightforward wiring

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Tasks 1, 2, 3, 4 (needs registry and view)

  **References**:
  - `src/ui/pipeline_view.py:PipelineConstructionWidget._load_available_nodes()` - line 227
  - `src/ui/pipeline_view.py:PipelineConstructionWidget.add_step` - signal
  - `src/controllers/pipeline_controller.py:add_node()` - controller method
  - `src/core/steps/__init__.py:STEP_REGISTRY` - source of nodes

  **Acceptance Criteria**:
  - [ ] Clicking "Add" shows popup with CLAHE, Grayscale, Crop
  - [ ] Selecting option creates node in pipeline
  - [ ] Node has correct type, name, icon from step definition
  - [ ] Node appears between input and output nodes

  **QA Scenarios**:
  ```
  Scenario: Add button shows step options
    Tool: interactive_bash (tmux)
    Preconditions: Task 4 complete
    Steps:
      1. Run: python src/main.py
      2. Click "Add" button (left panel)
      3. Verify popup menu appears with 3 options
      4. Click on "CLAHE"
      5. Verify new CLAHE node appears in list
      6. Press Ctrl+C to exit
    Expected Result: Popup shows CLAHE, Grayscale, Crop; selecting adds node
    Evidence: .sisyphus/evidence/task-5-add-button.png (screenshot)
  ```

  **Commit**: YES
  - Message: `feat(ui): Populate available nodes from step registry`
  - Files: `src/ui/pipeline_view.py`

- [ ] 6. Implement dynamic parameter UI in right panel

  **What to do**:
  - Replace hardcoded CLAHE UI (lines 521-525) with dynamic generation
  - In `update_properties_panel()`, check node type
  - Get STEP_PARAMETERS from registry for selected node type
  - Generate QDoubleSpinBox for float params, QSpinBox for int params
  - Connect valueChanged signals to update node parameters
  - Update controller when parameters change

  **Must NOT do**:
  - NO custom widget types (only standard spinboxes)
  - NO complex validation beyond min/max

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Reason**: Dynamic UI generation, widget creation, signal connections
  - **Skills**: `frontend-ui-ux` (for proper widget layout)

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Tasks 1, 2, 3, 4, 5 (needs working nodes and registry)

  **References**:
  - `src/ui/pipeline_view.py:update_properties_panel()` - lines 469-525
  - `src/core/steps/base.py:StepParameter` - parameter schema
  - `src/core/steps/clahe_step.py:STEP_PARAMETERS` - example params
  - PyQt6: QDoubleSpinBox, QSpinBox, QLabel

  **Acceptance Criteria**:
  - [ ] Selecting CLAHE node shows clip_limit and grid_size inputs
  - [ ] Inputs show correct default values
  - [ ] Changing value updates node.parameters
  - [ ] Values respect min/max constraints
  - [ ] Changes persist when selecting different nodes

  **QA Scenarios**:
  ```
  Scenario: CLAHE parameters editable
    Tool: interactive_bash (tmux)
    Preconditions: Task 5 complete
    Steps:
      1. Run: python src/main.py
      2. Click "Add" → select CLAHE
      3. Click on CLAHE node to select it
      4. Verify right panel shows "Clip Limit" and "Grid Size" inputs
      5. Change Clip Limit to 5.0
      6. Change Grid Size to 16
      7. Click away and back to verify values persist
      8. Press Ctrl+C to exit
    Expected Result: Parameters editable and persist
    Evidence: .sisyphus/evidence/task-6-parameters.png (screenshot)
  ```

  **Commit**: YES
  - Message: `feat(ui): Implement dynamic parameter editing in right panel`
  - Files: `src/ui/pipeline_view.py`

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Verify: All steps registered, dynamic UI works, add/reorder/toggle functional. Check evidence files exist.
  Output: VERDICT: APPROVE/REJECT

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Check: No PyQt imports in steps/, consistent styling, no print statements.
  Output: VERDICT

- [ ] F3. **Integration Test** — `unspecified-high`
  Run app, verify: Add button shows popup, CLAHE adds node, drag reorders, toggle disables, parameters editable.
  Save evidence to `.sisyphus/evidence/integration/`
  Output: VERDICT

---

## Commit Strategy

- **1**: `feat(steps): Add step registration system with @register_step decorator` — base.py, __init__.py
- **2**: `feat(steps): Add CLAHE processing step with parameters` — clahe_step.py
- **3**: `feat(steps): Add Grayscale and Crop placeholder steps` — grayscale_step.py, crop_step.py

---

## Success Criteria

### Verification Commands
```bash
# Test registry
python -c "from src.core.steps import STEP_REGISTRY; print('Steps:', list(STEP_REGISTRY.keys()))"

# Test CLAHE processing
python -c "import numpy as np; from src.core.steps.clahe_step import process; img = np.zeros((100,100), dtype=np.uint8); out = process(img, clip_limit=2.0, grid_size=8); print('OK')"
```

### Final Checklist
- [ ] STEP_REGISTRY contains: clahe, grayscale, crop
- [ ] CLAHE step has clip_limit and grid_size parameters
- [ ] Main window shows pipeline view
- [ ] Add button shows popup with 3 options
- [ ] CLAHE node can be added, toggled, reordered
- [ ] Right panel shows dynamic parameter UI
- [ ] No PyQt imports in src/core/steps/
- [ ] All guardrails respected (no undo, no preview, no branching)
