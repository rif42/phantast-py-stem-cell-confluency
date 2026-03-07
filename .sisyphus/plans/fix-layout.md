# Fix Plan: Remove Duplicate View Layout

## Problem
The main window currently shows ImageNavigationWidget side-by-side with PipelineConstructionWidget in a QSplitter. This creates a duplicate layout - the user sees:
- Left: Image Navigation
- Right: Pipeline Stack / Canvas / Properties

But the user wants ONLY the Pipeline view which already has:
- Left: Pipeline Stack
- Center: Canvas
- Right: Properties

## Fix Required

### File: src/ui/main_window.py

Change `load_views()` from:
```python
def load_views(self):
    # Create both views
    self.img_model = ImageSessionModel()
    self.view_img = ImageNavigationWidget()
    self.img_controller = ImageNavigationController(...)
    
    self.view_pipeline = PipelineConstructionWidget()
    self.pipeline_controller = PipelineController()
    # ... wire up signals ...
    
    # Show both in splitter
    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.addWidget(self.view_img)
    splitter.addWidget(self.view_pipeline)
    self.main_layout.addWidget(splitter)
```

To:
```python
def load_views(self):
    # Show only Pipeline view
    self.view_pipeline = PipelineConstructionWidget()
    self.pipeline_controller = PipelineController()
    # ... wire up signals ...
    
    self.main_layout.addWidget(self.view_pipeline)
```

Also remove unused imports:
- ImageNavigationWidget
- ImageSessionModel
- ImageNavigationController
- QSplitter

## Expected Result
Single window showing PipelineConstructionWidget with its existing 3-panel layout:
- Left sidebar: Pipeline Stack (with Add button and nodes)
- Center: Canvas area
- Right sidebar: Properties panel

## QA
Run `python src/main_window.py` and verify:
- [ ] Only one window with Pipeline view
- [ ] Left panel shows "PIPELINE STACK" with Add button
- [ ] Center shows canvas
- [ ] Right shows PROPERTIES panel
- [ ] No duplicate views
