---
phase: 2
plan: 2
wave: 2
depends_on: ["2.1"]
files_modified: ["src/ui/pipeline_view.py", "src/main.py"]
autonomous: true

must_haves:
  truths:
    - "The UI reflects the state of the PipelineController instead of data.json."
    - "UI interactions correctly mutate the pipeline state."
  artifacts:
    - "src/ui/pipeline_view.py"
---

# Plan 2.2: Pipeline UI Integration

<objective>
To connect the visual pipeline editor to the backend PipelineController.
Purpose: To allow researchers to manipulate the pipeline state using the UI.
Output: Updated `PipelineConstructionWidget` reading from and writing to the controller.
</objective>

<context>
Load for context:
- src/ui/pipeline_view.py
- src/controllers/pipeline_controller.py
</context>

<tasks>

<task type="auto">
  <name>Integrate PipelineController with PipelineConstructionWidget</name>
  <files>src/ui/pipeline_view.py, src/main.py</files>
  <action>
    Update `PipelineConstructionWidget` to accept a `PipelineController` instance.
    Remove static `data.json` loading. Render `PipelineNodeWidget`s directly from the controller's pipeline state.
    Connect `PipelineNodeWidget` signals (toggle, delete, reorder) directly to controller methods.
    Connect controller state change signals to UI re-rendering.
    AVOID: Duplicating state in the view. The view must reflect the controller's source of truth.
  </action>
  <verify>python src/main.py</verify>
  <done>UI correctly renders nodes from the controller, and interactions update the controller state.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] The UI reflects the state of the PipelineController instead of data.json.
- [ ] UI interactions correctly mutate the pipeline state.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
