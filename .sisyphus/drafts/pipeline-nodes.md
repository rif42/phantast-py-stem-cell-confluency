# Draft: Node-Based Pipeline System

## Requirements (from user)

### Core Functionality
1. **Add Button** on left sidebar opens popup list
2. **Popup List** contains processing node options:
   - **CLAHE** - Fully functional processing node
   - **Grayscale** - Placeholder (no implementation)
   - **Crop** - Placeholder (no implementation)
3. **CLAHE Node Features**:
   - Active/deactivate toggle (UI already exists)
   - Draggable reordering (UI already exists)
   - Parameters: clip_limit, tile_grid_size
4. **Node System**:
   - Each node has unique ID
   - Nodes can be reordered by dragging
   - Nodes can be activated/deactivated

### Scope Boundaries
- **INCLUDE**: 
  - CLAHE processing step implementation
  - Node registry/popup population
  - Basic step system architecture
  - Integration with existing pipeline view
- **EXCLUDE**:
  - Grayscale and Crop implementations (placeholders only)
  - Complex parameter UI (just basic CLAHE params)
  - Pipeline execution engine
  - Node connections/edges between nodes

## Current Architecture Discovery

### Already Implemented ✅
1. **Pipeline View** (`src/ui/pipeline_view.py`):
   - `PipelineConstructionWidget` with 3-panel layout
   - `PipelineNodeWidget` with:
     - ToggleSwitch (active/deactivate)
     - Drag-and-drop support (mouseMoveEvent + QDrag)
     - Context menu for delete
     - Styling with badges
   - Drop handling for reordering
   - Add button with QMenu popup (lines 276-288)

2. **Pipeline Model** (`src/models/pipeline_model.py`):
   - `PipelineNode` dataclass
   - `Pipeline` dataclass

3. **CLAHE** (`CLAHE.py`):
   - `apply_clahe()` function with parameters
   - Uses OpenCV's `cv2.createCLAHE()`

### Missing ❌
1. Processing step system (`src/core/steps/`)
2. Step implementations (CLAHE, Grayscale, Crop)
3. Node registry/population
4. Controller integration
5. Main window integration (pipeline view not shown)

## Technical Decisions

### Step System Architecture
- Location: `src/core/steps/`
- Pattern: Base class + concrete implementations
- Each step has: name, description, parameters, process() method
- Parameters as dict for flexibility

### PyQt6 Drag-and-Drop
- **Already implemented** in PipelineNodeWidget:
  - `mouseMoveEvent` starts drag with QMimeData
  - `scroll_dropEvent` handles drop and reordering
  - Uses `application/x-pipeline-node` mime type

### Parameter Storage
- Use `PipelineNode.parameters` dict
- CLAHE: `{"clip_limit": 2.0, "tile_grid_size": [8, 8]}`

## Research Findings

From codebase analysis:
- ToggleSwitch uses custom paintEvent (36x20px, #00B884 green when on)
- Nodes have icon, name, description, badge labels
- Styling uses dark theme (#121415 background, #00B884 accent)
- QMenu for add button with actions

## Open Questions

1. **Test Strategy**: None currently exists in project
   - Decision: No automated tests for this task (keep it simple)

2. **Parameter UI**: How to edit CLAHE parameters?
   - Decision: Basic QLineEdit/QSpinBox in right panel when node selected

3. **Integration**: Does pipeline view need to be in main window?
   - Decision: Yes, add pipeline view as second tab/mode

4. **Node Types**: Just processing nodes or input/output too?
   - Decision: Only processing nodes for now (user said "processing nodes")
