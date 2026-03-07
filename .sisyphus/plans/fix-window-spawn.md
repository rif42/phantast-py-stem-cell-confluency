# Fix Plan: Stop Node Widgets from Spawning Separate Windows

## Problem
When adding a CLAHE node (or any processing node), it spawns as a separate window instead of appearing inside the left sidebar pipeline stack.

## Root Cause
The `ToggleSwitch` widget in `PipelineNodeWidget` is being created without a proper parent widget:

```python
# Current code (line ~168)
switch = ToggleSwitch(self.node_data.get("enabled", True))
```

This causes the ToggleSwitch to potentially create its own window or cause reparenting issues.

## Fix Required

### File: src/ui/pipeline_view.py

Update line ~168 in `PipelineNodeWidget.init_ui()`:

```python
# Change FROM:
switch = ToggleSwitch(self.node_data.get("enabled", True))
switch.toggled.connect(lambda checked: self.toggled.emit(self.node_id, checked))

# Change TO:
switch = ToggleSwitch(self.node_data.get("enabled", True), parent=self)
switch.toggled.connect(lambda checked: self.toggled.emit(self.node_id, checked))
```

This ensures the ToggleSwitch has the PipelineNodeWidget as its parent, preventing it from creating a separate window.

## QA
1. Run `python src/main.py`
2. Click "Add" button in left sidebar
3. Select "CLAHE" from popup menu
4. **Verify**: CLAHE node appears INSIDE the left sidebar pipeline stack
5. **Verify**: NO separate window spawns
6. **Verify**: Node shows: icon, name, description, PROCESS badge, toggle switch

## Expected Result
- Node appears embedded in the scrollable list
- No additional windows created
- Toggle switch works correctly
