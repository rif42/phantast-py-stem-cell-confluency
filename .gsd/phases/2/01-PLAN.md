---
phase: 2
plan: 1
wave: 1
depends_on: []
files_modified: ["src/models/pipeline_model.py", "src/controllers/pipeline_controller.py"]
autonomous: true

must_haves:
  truths:
    - "Pipeline and PipelineNode data structures exist."
    - "PipelineController handles basic list operations (add, remove, reorder, toggle, configure)."
  artifacts:
    - "src/models/pipeline_model.py"
    - "src/controllers/pipeline_controller.py"
---

# Plan 2.1: Pipeline Data Models & Controller

<objective>
To establish the core data models and business logic controller for the image processing sequence.
Purpose: To manage the pipeline state independently of the UI.
Output: The `Pipeline` model, `PipelineNode` model, and `PipelineController`.
</objective>

<context>
Load for context:
- product/sections/pipeline-construction/data.json
- product-plan/docs/instructions/implementation_guide.md
- src/ui/pipeline_view.py
</context>

<tasks>

<task type="auto">
  <name>Create Pipeline Models</name>
  <files>src/models/pipeline_model.py</files>
  <action>
    Create `PipelineNode` dataclass (id, type, name, description, icon, status, enabled, parameters).
    Create `Pipeline` dataclass containing a list of `PipelineNode`s. 
    AVOID: Modifying UI files. Keep models strictly data containers with basic methods.
  </action>
  <verify>python -c "from src.models.pipeline_model import Pipeline, PipelineNode"</verify>
  <done>Models can be imported without errors.</done>
</task>

<task type="auto">
  <name>Create Pipeline Controller</name>
  <files>src/controllers/pipeline_controller.py</files>
  <action>
    Create `PipelineController` class. Implement methods: `add_node`, `remove_node`, `reorder_nodes`, `toggle_node`, `update_node_params`.
    Should emit PyQt signals when the pipeline state changes.
    AVOID: Connecting to PyQt views directly in the controller; views should connect to controller signals.
  </action>
  <verify>python -c "from src.controllers.pipeline_controller import PipelineController"</verify>
  <done>PipelineController exposes state mutation methods and PyQt signals.</done>
</task>

</tasks>

<verification>
After all tasks, verify:
- [ ] Pipeline and PipelineNode data structures exist.
- [ ] PipelineController handles basic list operations.
</verification>

<success_criteria>
- [ ] All tasks verified
- [ ] Must-haves confirmed
</success_criteria>
