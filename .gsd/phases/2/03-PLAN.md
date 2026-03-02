---
phase: 2
plan: 3
wave: 3
depends_on: ["2.1", "2.2"]
files_modified: ["src/models/image_processor.py", "src/controllers/pipeline_controller.py", "src/ui/image_canvas.py", "src/ui/pipeline_view.py"]
autonomous: true

must_haves:
  truths:
    - "The pipeline can process an image and generate a segmentation mask."
    - "The canvas can visually overlay the segmentation mask."
  artifacts:
    - "src/models/image_processor.py"
---

# Plan 2.3: OpenCV Execution & Mask Overlay

<objective>
To execute the pipeline algorithms on the active image and display the resulting segmentation mask in the UI.
Purpose: To allow researchers to inspect the cell detection accuracy of their draft pipeline.
Output: Connected OpenCV execution logic and updated canvas overlay.
</objective>

<context>
Load for context:
- src/ui/image_canvas.py
- src/ui/pipeline_view.py
- src/controllers/pipeline_controller.py
</context>

<tasks>

<task type="auto">
  <name>Implement Canvas Mask Overlay</name>
  <files>src/ui/image_canvas.py</files>
  <action>
    Update `ImageCanvas` to support adding a mask overlay.
    Add a `QGraphicsPixmapItem` for the mask above the main image pixmap item.
    Implement `set_mask(file_path)` and `set_mask_visible(visible: bool)` methods.
    AVOID: Replacing the base image. The mask must be an overlay with ~50% opacity or a distinct color.
  </action>
  <verify>python src/main.py</verify>
  <done>Canvas API supports mask overlay loading and visibility toggling.</done>
</task>

<task type="auto">
  <name>Implement Image Processing Logic</name>
  <files>src/models/image_processor.py, src/controllers/pipeline_controller.py, src/ui/pipeline_view.py</files>
  <action>
    Create `ImageProcessor.run_pipeline(pipeline, image_path)` using OpenCV to apply node algorithms and save a mask output.
    Update `PipelineController.run_pipeline()` to execute this on a background thread (using `QRunnable` or `QThread` correctly as per AGENTS.md rules).
    On completion, emit a signal with the path to the mask.
    Update `PipelineConstructionWidget` to receive this mask path and call `ImageCanvas.set_mask()`.
    Add a UI toggle (e.g., eye icon or checkbox) to toggle mask visibility.
    AVOID: Blocking the GUI thread during image processing.
  </action>
  <verify>python src/main.py</verify>
  <done>Clicking 'Run Pipeline' executes algorithms asynchronously and displays a togglable mask overlay.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] The pipeline can process an image and generate a segmentation mask.
- [ ] The canvas can visually overlay the segmentation mask.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
