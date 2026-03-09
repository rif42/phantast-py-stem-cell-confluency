# Bug Fix: CLAHE Node Parameters Not Showing in Right Sidebar

## Issue Description
When clicking on a CLAHE node in the pipeline stack, the right sidebar shows the node title and description, but the parameter widgets (epsilon, sigma spinboxes) are not displayed.

**Screenshot Evidence**: Shows "Clahe" title, "Clahe" description, and "Apply Changes" button, but no parameter input fields.

## Root Cause
`main_window.py` has `self.available_nodes = []` initialized but **never populated**. The `show_properties()` method in `unified_right_panel.py` requires `available_nodes` to look up the step definition and generate parameter widgets. Without this data, it falls back to showing only basic info.

The `pipeline_stack_widget.py` already has the correct implementation in `_load_available_nodes()` that loads from `STEP_REGISTRY`, but `main_window.py` has its own separate empty list.

## Fix Required

### File: `src/ui/main_window.py`

**Step 1: Add `_load_available_nodes()` method**
Add this method to load node definitions from the step registry (same pattern as `pipeline_stack_widget.py`):

```python
def _load_available_nodes(self):
    """Load available processing nodes from step registry."""
    try:
        from src.core.steps import STEP_REGISTRY

        self.available_nodes = []
        for step_name, step_meta in STEP_REGISTRY.items():
            node_info = {
                "type": step_name,
                "name": step_meta.description,
                "description": step_meta.description,
                "icon": step_meta.icon,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "default": p.default,
                        "min": p.min,
                        "max": p.max,
                        "step": p.step,
                        "description": p.description,
                    }
                    for p in step_meta.parameters
                ],
            }
            self.available_nodes.append(node_info)
    except Exception:
        self.available_nodes = []
```

**Step 2: Call it in `setup_models()`**
Modify `setup_models()` to call the new method:

```python
def setup_models(self):
    """Initialize data models."""
    self.image_model = ImageSessionModel()
    self.pipeline_model = Pipeline()
    self._load_available_nodes()  # ADD THIS LINE
```

## Verification

After the fix, when clicking on CLAHE node:
1. Right sidebar should show "Clahe" title
2. Should show two parameter fields:
   - **Epsilon**: QDoubleSpinBox (0.1 to 10.0, default 2.0, step 0.1)
   - **Sigma**: QDoubleSpinBox (2.0 to 32.0, default 8.0, step 1.0)
3. Each should have description text below
4. Apply Changes button should enable when values change

## Test Steps

1. Run `python -m src.main`
2. Load an image
3. Add CLAHE node to pipeline
4. Click on CLAHE node
5. **Verify**: Two spinboxes appear (epsilon, sigma)
6. Change epsilon value
7. **Verify**: Apply button enables and shows count
8. Click Apply
9. **Verify**: Parameters are applied
