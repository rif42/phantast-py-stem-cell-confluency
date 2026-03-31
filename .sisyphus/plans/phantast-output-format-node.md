# PHANTAST Output Format Node + Confluency Caption

## TL;DR
> **Summary**: Add an auto-inserted `output format` node under each new PHANTAST node, expose a default-enabled `show confluency` toggle in the right sidebar, and burn a confluency caption strip into both `mask` and `processed` saved images.
> **Deliverables**:
> - Auto-insertion rule for `output format` node after PHANTAST node creation
> - Right-panel bool parameter editing for `show confluency`
> - Output rendering path that appends white strip + caption from PHANTAST confluency metadata
> - Focused minimal tests for behavior-critical paths
> **Effort**: Medium
> **Parallel**: YES - 2 waves
> **Critical Path**: Task 1 -> Task 2 -> Task 4 -> Task 6

## Context
### Original Request
Add an `output format` node automatically below PHANTAST; selecting it should show `show confluency` toggle in right sidebar (default ON). If ON, final image gets small white area below image with `confluency xx%` where value comes from PHANTAST segmentation node.

### Interview Summary
- Caption must be burned into saved/exported images, not only preview.
- Apply caption behavior to both `mask` and `processed` output files.
- Test strategy is minimal tests (targeted coverage only).

### Metis Review (gaps addressed)
- Use deterministic caption rendering (fixed format and precision) and avoid locale-dependent formatting.
- Define exact confluency source contract (PHANTAST execution metadata, no recomputation in output stage).
- Define no-value behavior when confluency is unavailable (no caption strip added).
- Define explicit rendering point in worker save pipeline and apply consistently to both output kinds.
- Keep scope limited to single toggle + fixed caption template (no generic annotation system).

## Work Objectives
### Core Objective
Implement a deterministic pipeline/UI extension where PHANTAST automatically gains a paired output-format configuration node controlling confluency caption burn-in for saved outputs.

### Deliverables
- New/registered `output format` step with `show_confluency: bool = True`.
- Node auto-add rule after PHANTAST insertion in pipeline list.
- Right-sidebar bool control for `show_confluency` when output-format node is selected.
- Worker-level caption rendering utility applied to `mask` and `processed` output saves.
- Minimal test additions validating node insertion, parameter toggling, and output burn-in behavior.

### Definition of Done (verifiable conditions with commands)
- `rtk test "pytest tests/test_pipeline_execution.py -k output_format -v"` passes.
- `rtk test "pytest tests/test_pipeline_worker.py -k confluency -v"` passes.
- `rtk test "pytest tests/test_phantast_step.py -k confluency -v"` passes (non-regression).
- `rtk test "pytest tests/ -v"` passes (or expected pre-existing failures documented in evidence).

### Must Have
- Output format node always inserted immediately after each newly added PHANTAST node.
- `show_confluency` is editable from right panel and defaults to enabled.
- Caption text format is fixed and ASCII-safe: `confluency {value:.1f}%`.
- Caption rendering appends a white strip below image, preserving original image pixels.
- Caption burn-in applies to both saved `mask` and `processed` outputs.

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- No popup/dialog-based configuration changes (single-page app rule).
- No parent-child model refactor for pipeline nodes (remain flat ordered list).
- No recomputation of confluency in output-format step/worker.
- No generic label template system or extra toggle options.
- No locale/global formatting changes in worker threads.

## Verification Strategy
> ZERO HUMAN INTERVENTION — all verification is agent-executed.
- Test decision: minimal tests using existing `pytest` + `pytest-qt` patterns.
- QA policy: every task includes agent-executed happy + failure/edge scenario.
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks for max parallelism.

Wave 1: Step contract + auto-insertion + parameter editor support (foundation)
Wave 2: Output rendering + data plumbing + focused tests (including full-suite guard)

### Dependency Matrix (full, all tasks)
- Task 1 blocks Tasks 2, 3, 4.
- Task 2 blocks Task 5.
- Task 3 blocks Task 5.
- Task 4 blocks Tasks 5, 6.
- Task 5 blocks Task 6.
- Task 6 blocks Final Verification Wave.

### Agent Dispatch Summary (wave -> task count -> categories)
- Wave 1 -> 3 tasks -> `quick`, `unspecified-low`
- Wave 2 -> 3 tasks -> `unspecified-high`, `deep`, `quick`

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: Agent Profile + Parallelization + QA Scenarios.

- [ ] 1. Add output-format step contract and registry metadata

  **What to do**: Add a dedicated pipeline step definition for `output format` with parameter schema containing `show_confluency` (bool, default `True`), display name `output format`, and compatibility metadata aligned with existing step registration patterns. Ensure this step is selectable/renderable by existing node + right-panel machinery without introducing new windowed UI.
  **Must NOT do**: Do not add extra output-format parameters, localization options, or template text configuration.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: localized metadata/schema addition.
  - Skills: `[]` — Reason: existing pattern is straightforward.
  - Omitted: `frontend-ui-ux` — Reason: no styling redesign needed.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 2, 3, 4 | Blocked By: none

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/core/steps/__init__.py` — step registration and `StepParameter` schema conventions.
  - Pattern: `src/core/steps/phantast_step.py` — PHANTAST step contract and result metadata conventions.
  - API/Type: `src/models/pipeline_model.py` — node parameter persistence shape.
  - Test: `tests/test_pipeline_execution.py` — integration setup for building pipeline nodes in UI tests.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `output format` step appears in registry and exposes `show_confluency` defaulting to `True`.
  - [ ] Step metadata is consumable by right panel without runtime exceptions.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Step registration happy path
    Tool: Bash
    Steps: python -c "from src.core.steps import STEP_REGISTRY; s=STEP_REGISTRY.get('output format'); assert s is not None; p=next(x for x in s.parameters if x.name=='show_confluency'); assert p.default is True"
    Expected: Command exits 0.
    Evidence: .sisyphus/evidence/task-1-output-format-registry.txt

  Scenario: Missing-param guard
    Tool: Bash
    Steps: python -c "from src.core.steps import STEP_REGISTRY; s=STEP_REGISTRY.get('output format'); assert all(x.name!='showConfluency' for x in s.parameters)"
    Expected: Command exits 0 and only snake_case param exists.
    Evidence: .sisyphus/evidence/task-1-output-format-registry-error.txt
  ```

  **Commit**: YES | Message: `feat(steps): add output format step with confluency toggle` | Files: `src/core/steps/__init__.py`, `src/core/steps/*output*`

- [ ] 2. Auto-insert output-format node directly after PHANTAST node

  **What to do**: Extend PHANTAST node addition flow so each newly added PHANTAST node immediately creates a paired `output format` node at index+1 in the flat pipeline list. Keep behavior deterministic with existing add-node path and preserve current ordering/reordering constraints.
  **Must NOT do**: Do not refactor model to parent-child graph or alter non-PHANTAST insertion behavior.

  **Recommended Agent Profile**:
  - Category: `unspecified-low` — Reason: controller/UI sequencing across several existing methods.
  - Skills: `[]` — Reason: no special external library needed.
  - Omitted: `deep` — Reason: bounded workflow change.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 5 | Blocked By: 1

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/ui/main_window.py` — `handle_add_step`, node creation helpers, selection/update flow.
  - Pattern: `src/controllers/pipeline_controller.py` — `add_node` mutation pathway.
  - Pattern: `src/ui/pipeline_stack_widget.py` — visual ordering and node selection behavior.
  - API/Type: `src/models/pipeline_model.py` — ordered node storage semantics.
  - Test: `tests/test_pipeline_execution.py` — assertions around node ordering and presence.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Adding PHANTAST results in adjacent `output format` node immediately below it.
  - [ ] Adding non-PHANTAST steps does not auto-create output-format nodes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: PHANTAST insertion creates paired node
    Tool: Bash
    Steps: rtk test "pytest tests/test_pipeline_execution.py -k phantast_auto_adds_output_format -v"
    Expected: Test passes and validates adjacent ordering.
    Evidence: .sisyphus/evidence/task-2-auto-insert.txt

  Scenario: Non-PHANTAST insertion unchanged
    Tool: Bash
    Steps: rtk test "pytest tests/test_pipeline_execution.py -k non_phantast_no_output_format_auto_add -v"
    Expected: Test passes and confirms no unintended node creation.
    Evidence: .sisyphus/evidence/task-2-auto-insert-error.txt
  ```

  **Commit**: YES | Message: `feat(pipeline): auto-add output format after phantast` | Files: `src/ui/main_window.py`, `src/controllers/pipeline_controller.py`, `tests/test_pipeline_execution.py`

- [ ] 3. Expose editable show-confluency toggle in right sidebar for output-format node

  **What to do**: Ensure selecting `output format` node shows a boolean editor for `show_confluency` in the right panel, with default `True`, and param changes persisted through existing `node_param_changed` flow.
  **Must NOT do**: Do not introduce dialogs/popups, and do not add read-only label-only control for this parameter.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: focused UI parameter widget behavior.
  - Skills: `[]` — Reason: existing metadata-driven panel should be reused.
  - Omitted: `visual-engineering` — Reason: function over visual redesign.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 5 | Blocked By: 1

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/ui/unified_right_panel.py` — `show_properties`, `_add_parameter_widget`, param change signal wiring.
  - Pattern: `src/ui/main_window.py` — selection forwarding into right panel.
  - Pattern: `src/ui/pipeline_stack_widget.py` — node selection event emission.
  - API/Type: `src/core/steps/__init__.py` — bool parameter metadata source.
  - Test: `tests/test_pipeline_execution.py` — existing sidebar/parameter interaction patterns.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Selecting output-format node renders a clickable bool control for `show_confluency`.
  - [ ] Toggling control emits parameter update and persists value in node params.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Toggle available and defaults true
    Tool: Bash
    Steps: rtk test "pytest tests/test_pipeline_execution.py -k output_format_sidebar_toggle_default_true -v"
    Expected: Test passes and verifies bool editor state is true.
    Evidence: .sisyphus/evidence/task-3-sidebar-toggle.txt

  Scenario: Toggle change persists false
    Tool: Bash
    Steps: rtk test "pytest tests/test_pipeline_execution.py -k output_format_sidebar_toggle_persists_false -v"
    Expected: Test passes and verifies updated node params include show_confluency=False.
    Evidence: .sisyphus/evidence/task-3-sidebar-toggle-error.txt
  ```

  **Commit**: YES | Message: `feat(ui): wire output-format confluency toggle in right panel` | Files: `src/ui/unified_right_panel.py`, `src/ui/main_window.py`, `tests/test_pipeline_execution.py`

- [ ] 4. Implement deterministic caption strip rendering in worker save path

  **What to do**: Add worker-level utility that appends a white bottom strip (using border-based extension) and renders `confluency {value:.1f}%` text. Apply to both saved `mask` and `processed` images at one defined point in output pipeline. Preserve original image content and support grayscale/BGR inputs without color-channel corruption.
  **Must NOT do**: Do not draw over original image pixels; do not rely on locale formatting; do not duplicate rendering logic in multiple save branches.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: image processing behavior and multi-branch output path integration.
  - Skills: `[]` — Reason: OpenCV usage follows existing project patterns.
  - Omitted: `artistry` — Reason: deterministic technical rendering, not creative design.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 5, 6 | Blocked By: 1

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/core/pipeline_worker.py` — save/output branches and image preparation path.
  - Pattern: `src/core/steps/phantast_step.py` — confluency value production contract.
  - Pattern: `src/core/steps/__init__.py` — parameter/read access conventions if step params consulted in worker context.
  - Test: `tests/test_pipeline_worker.py` — worker-level output assertions and file-save checks.
  - External: `https://docs.opencv.org/4.x/d6/d6e/group__imgproc__draw.html` — `getTextSize`/`putText` behavior.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Saved `mask` and `processed` files include appended white strip + caption when enabled and confluency exists.
  - [ ] Output dimensions remain unchanged when toggle is disabled or confluency missing.
  - [ ] Caption text uses fixed one-decimal precision format and ASCII lowercase prefix.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Caption strip appears on both output types
    Tool: Bash
    Steps: rtk test "pytest tests/test_pipeline_worker.py -k confluency_caption_applies_mask_and_processed -v"
    Expected: Test passes; both artifacts have increased height and caption pixels in strip ROI.
    Evidence: .sisyphus/evidence/task-4-render-mask-processed.txt

  Scenario: No caption when disabled/missing value
    Tool: Bash
    Steps: rtk test "pytest tests/test_pipeline_worker.py -k confluency_caption_disabled_or_missing_value -v"
    Expected: Test passes; output dimensions match baseline and no extra strip is added.
    Evidence: .sisyphus/evidence/task-4-render-mask-processed-error.txt
  ```

  **Commit**: YES | Message: `feat(output): render confluency caption strip in worker outputs` | Files: `src/core/pipeline_worker.py`, `tests/test_pipeline_worker.py`

- [ ] 5. Wire PHANTAST confluency metadata to paired output-format toggle behavior

  **What to do**: Define and implement explicit pairing contract: output-format node reads the nearest preceding PHANTAST node execution metadata for confluency value, then applies caption only when that node's `show_confluency` is true. Ensure behavior is stable when multiple PHANTAST/output-format pairs exist.
  **Must NOT do**: Do not recompute confluency from image data and do not cross-wire values between different PHANTAST pairs.

  **Recommended Agent Profile**:
  - Category: `deep` — Reason: data-flow correctness across ordered pipeline execution.
  - Skills: `[]` — Reason: internal architecture reasoning only.
  - Omitted: `quick` — Reason: pairing logic has subtle edge cases.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 6 | Blocked By: 2, 3, 4

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/models/pipeline_model.py` — ordered node list semantics.
  - Pattern: `src/core/pipeline_worker.py` — execution order and inter-step data propagation.
  - Pattern: `src/ui/main_window.py` — insertion position guaranteeing adjacency semantics.
  - Pattern: `src/core/steps/phantast_step.py` — confluency field naming and value source.
  - Test: `tests/test_pipeline_execution.py` — multi-node pipeline behavior assertions.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Each output-format node uses confluency from its intended PHANTAST predecessor.
  - [ ] Multiple PHANTAST segments in one pipeline do not leak/override confluency values.
  - [ ] Missing predecessor PHANTAST or missing confluency value results in no caption strip.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Correct pairing in multi-PHANTAST pipeline
    Tool: Bash
    Steps: rtk test "pytest tests/test_pipeline_execution.py -k output_format_uses_correct_phantast_confluency_pair -v"
    Expected: Test passes; each output file caption reflects the corresponding PHANTAST value.
    Evidence: .sisyphus/evidence/task-5-pairing.txt

  Scenario: Missing PHANTAST predecessor handled gracefully
    Tool: Bash
    Steps: rtk test "pytest tests/test_pipeline_execution.py -k output_format_without_phantast_predecessor_no_caption -v"
    Expected: Test passes; no crash and no strip added.
    Evidence: .sisyphus/evidence/task-5-pairing-error.txt
  ```

  **Commit**: YES | Message: `fix(pipeline): bind output-format caption to matching phantast metadata` | Files: `src/core/pipeline_worker.py`, `src/models/pipeline_model.py`, `tests/test_pipeline_execution.py`

- [ ] 6. Add minimal targeted regression tests and execution evidence capture

  **What to do**: Add/adjust only the smallest set of tests needed to lock behavior: auto-node insertion, right-sidebar toggle persistence, caption burn-in on `mask` + `processed`, disabled/missing-value behavior, and PHANTAST pairing. Capture command outputs/screenshots as evidence artifacts.
  **Must NOT do**: Do not expand into broad refactors or unrelated test rewrites.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: focused test additions and command execution.
  - Skills: `[]` — Reason: existing pytest patterns already established.
  - Omitted: `ultrabrain` — Reason: no novel algorithm design in this task.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: Final Verification Wave | Blocked By: 4, 5

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `tests/test_pipeline_execution.py` — UI/integration setup with node interactions.
  - Pattern: `tests/test_pipeline_worker.py` — output-file assertions.
  - Pattern: `tests/test_phantast_step.py` — confluency non-regression patterns.
  - Command: `AGENTS.md` — canonical project test command patterns.

  **Acceptance Criteria** (agent-executable only):
  - [ ] New/updated focused tests pass for insertion, toggle, and rendering behavior.
  - [ ] `rtk test "pytest tests/ -v"` result is recorded in evidence (pass or documented pre-existing failures).
  - [ ] Evidence files exist for each task QA scenario path in this plan.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Focused suite pass
    Tool: Bash
    Steps: rtk test "pytest tests/test_pipeline_execution.py -k 'output_format or confluency' -v" && rtk test "pytest tests/test_pipeline_worker.py -k confluency -v"
    Expected: Commands exit 0 with target tests passing.
    Evidence: .sisyphus/evidence/task-6-focused-tests.txt

  Scenario: Full-suite guard
    Tool: Bash
    Steps: rtk test "pytest tests/ -v"
    Expected: Exit 0 OR failures are pre-existing and documented with exact failing test IDs.
    Evidence: .sisyphus/evidence/task-6-full-suite.txt
  ```

  **Commit**: YES | Message: `test(output): cover output-format toggle and confluency burn-in` | Files: `tests/test_pipeline_execution.py`, `tests/test_pipeline_worker.py`, `.sisyphus/evidence/*`

## Final Verification Wave (4 parallel agents, ALL must APPROVE)
- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high (+ playwright if UI)
- [ ] F4. Scope Fidelity Check — deep

## Commit Strategy
- Commit 1: `feat(pipeline): auto-add output-format node for phantast`
- Commit 2: `feat(output): burn confluency caption into saved mask and processed images`
- Commit 3: `test(pipeline): add minimal coverage for output-format toggle and caption behavior`

## Success Criteria
- Adding PHANTAST creates adjacent output-format node consistently.
- Selecting output-format shows editable `show confluency` toggle defaulting to ON.
- Enabling toggle adds white strip + `confluency {value:.1f}%` to both saved output types.
- Disabling toggle (or missing confluency value) produces no caption strip.
- All targeted tests pass with evidence artifacts captured.
