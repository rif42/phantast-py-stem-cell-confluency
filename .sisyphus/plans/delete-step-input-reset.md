# Delete Step Styling and Input Deletion Reset

## TL;DR
> **Summary**: Apply a destructive visual style to the `Delete Step` context-menu action and add deterministic reset behavior when deleting input nodes (`input_single_image`, `input_image_folder`).
> **Deliverables**:
> - Updated delete-action styling in active pipeline stack UI
> - Input-node-specific reset routine in main window deletion flow
> - Automated pytest-qt coverage for input-delete reset and non-input-delete preservation
> **Effort**: Short
> **Parallel**: YES - 2 waves
> **Critical Path**: Task 1 -> Task 2 -> Task 4

## Context
### Original Request
- Make the `Delete Step` control have opaque red background and bold black text.
- When deleting input nodes (`open image`, `open folder`), reset the center view and right properties sidebar.
- Consult Momus for insights/conflicts.

### Interview Summary
- Active deletion path is `PipelineNodeWidget.deleted -> PipelineStackWidget.delete_node -> MainWindow.handle_delete_node`.
- `Delete Step` is currently a `QMenu` action (not a standalone button), so styling must target menu item rendering.
- Right sidebar full reset is available via `UnifiedRightPanel.clear()`.
- Existing handler in `MainWindow.handle_delete_node` currently removes node and refreshes metadata only.

### Metis Review (gaps addressed)
- Guardrail added: branch behavior by node type before removal to avoid resetting on non-input deletions.
- Guardrail added: include run-gating assertions to prevent stale `current_image_path` from keeping Run enabled.
- Scope narrowed to active path files only; legacy `src/ui/pipeline_view.py` explicitly excluded.

## Work Objectives
### Core Objective
Implement destructive delete-action styling and input-node delete reset behavior without regressions to non-input deletion flow.

### Deliverables
- `src/ui/pipeline_stack_widget.py` updated to render `Delete Step` as opaque red with bold black text.
- `src/ui/main_window.py` updated with input-node-specific reset logic in deletion flow.
- `tests/test_pipeline_execution.py` expanded with explicit delete-reset behavior tests.

### Definition of Done (verifiable conditions with commands)
- `pytest tests/test_pipeline_execution.py -k "delete_input_node_resets_center_and_right_panel" -v` passes.
- `pytest tests/test_pipeline_execution.py -k "delete_non_input_node_preserves_current_image_context" -v` passes.
- `pytest tests/test_pipeline_execution.py -k "delete_input_folder_node_disables_run_gate_and_hides_folder_explorer" -v` passes.
- `pytest tests/test_pipeline_execution.py -k "run" -v` passes (no run-gate regressions in touched area).

### Must Have
- Input-node delete path clears center view state and properties sidebar state.
- Non-input delete path does not clear center/right state.
- Folder explorer visibility is reset for input deletion scenarios.
- No new windows/dialogs/popups introduced.

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- Do NOT modify `src/ui/pipeline_view.py` (legacy).
- Do NOT change controller/model architecture for this task.
- Do NOT apply global stylesheet redesign; only targeted delete-action styling.
- Do NOT require human/manual verification in acceptance criteria.

## Verification Strategy
> ZERO HUMAN INTERVENTION — all verification is agent-executed.
- Test decision: tests-after + `pytest`/`pytest-qt`
- QA policy: every task includes happy + failure/edge scenario
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks for max parallelism.

Wave 1: deletion-flow branching + reset routine + delete-action styling
Wave 2: test coverage + regression run

### Dependency Matrix (full, all tasks)
- Task 1 blocks Tasks 2-4
- Task 2 blocks Task 4
- Task 3 can run in parallel with Task 2 after Task 1
- Task 4 blocks Task 5
- Task 5 blocks final verification wave

### Agent Dispatch Summary (wave -> task count -> categories)
- Wave 1 -> 3 tasks -> `visual-engineering`, `unspecified-high`
- Wave 2 -> 2 tasks -> `unspecified-high`
- Final Verification Wave -> 4 tasks -> `oracle`, `unspecified-high`, `deep`

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: Agent Profile + Parallelization + QA Scenarios.

- [x] 1. Add stable input-node context lookup for delete flow

  **What to do**: In `MainWindow.handle_delete_node`, resolve the node data/type for `node_id` before removing it from controller state. Introduce an internal helper to classify whether deleted node is input (`input_single_image` or `input_image_folder`) and carry this boolean into post-delete branch logic.
  **Must NOT do**: Do not change controller contracts or node schema.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: logic-sensitive state transition in core UI flow
  - Skills: [`pyqt6-ui-development-rules`] — enforce signal/slot and single-page guardrails
  - Omitted: [`frontend-ui-ux`] — no layout redesign needed

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: [2,3,4] | Blocked By: []

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/ui/main_window.py:435` — signal wiring for delete flow
  - Pattern: `src/ui/main_window.py:695` — current delete handler entry point
  - API/Type: `src/ui/pipeline_stack_widget.py:221` — upstream signal emits deleted `node_id`

  **Acceptance Criteria** (agent-executable only):
  - [ ] Deletion branch can reliably distinguish input vs non-input node before controller mutation.
  - [ ] No lint/type/runtime error introduced by new helper/branch.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Happy path - input delete classification
    Tool: Bash
    Steps: Run `pytest tests/test_pipeline_execution.py -k "delete_input" -v`
    Expected: New/updated tests hit input classification branch and pass
    Evidence: .sisyphus/evidence/task-1-input-delete-classification.txt

  Scenario: Failure/edge case - unknown node id
    Tool: Bash
    Steps: Run `pytest tests/test_pipeline_execution.py -k "delete_unknown_node_id_no_crash" -v`
    Expected: No crash; handler exits gracefully with unchanged UI state
    Evidence: .sisyphus/evidence/task-1-input-delete-classification-error.txt
  ```

  **Commit**: YES | Message: `fix(ui): classify input node deletion before mutation` | Files: `src/ui/main_window.py`, `tests/test_pipeline_execution.py`

- [x] 2. Implement input-node reset routine for center view and right sidebar

  **What to do**: Add a dedicated reset routine in `MainWindow` for input-node deletion that clears image/context state used by center view (`current_image_path`, comparison artifacts), calls `comparison_controls.reset()`, triggers `_update_empty_state()`, hides folder explorer on the right panel, and calls `right_panel.clear()`.
  **Must NOT do**: Do not reset on non-input deletion; do not alter batch execution architecture.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: multi-widget state consistency and run-gating correctness
  - Skills: [`pyqt6-ui-development-rules`] — preserve PyQt lifecycle and parent/signal rules
  - Omitted: [`git-master`] — no git workflow operation in this task body

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: [4] | Blocked By: [1]

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/ui/main_window.py:695` — post-delete update sequence to extend
  - Pattern: `src/ui/main_window.py:505` — run-button gating logic tied to `current_image_path`
  - Pattern: `src/ui/main_window.py:_update_empty_state` — center empty-state + right clear behavior
  - API/Type: `src/ui/unified_right_panel.py:683` — full right-panel reset API (`clear()`)
  - API/Type: `src/ui/unified_right_panel.py:702` — folder explorer visibility API
  - API/Type: `src/ui/comparison_controls.py:104` — comparison reset API

  **Acceptance Criteria** (agent-executable only):
  - [ ] Deleting input node clears center display context and returns center to empty-state behavior.
  - [ ] Right sidebar properties are reset via `clear()` and folder explorer is hidden for deleted input context.
  - [ ] `Run Pipeline` becomes disabled when no valid input remains.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Happy path - delete open image node
    Tool: Bash
    Steps: Run `pytest tests/test_pipeline_execution.py -k "delete_input_node_resets_center_and_right_panel" -v`
    Expected: Assertions confirm cleared image state, hidden comparison controls, right panel reset defaults
    Evidence: .sisyphus/evidence/task-2-delete-open-image-reset.txt

  Scenario: Failure/edge case - delete input while processing nodes remain
    Tool: Bash
    Steps: Run `pytest tests/test_pipeline_execution.py -k "delete_input_folder_node_disables_run_gate_and_hides_folder_explorer" -v`
    Expected: Run stays disabled without input despite remaining processing nodes
    Evidence: .sisyphus/evidence/task-2-delete-input-run-gate-error.txt
  ```

  **Commit**: YES | Message: `fix(ui): reset center and sidebar on input node deletion` | Files: `src/ui/main_window.py`, `tests/test_pipeline_execution.py`

- [x] 3. Style `Delete Step` action as destructive in active context menu

  **What to do**: Update `PipelineNodeWidget.contextMenuEvent` styling path so the menu item used for `Delete Step` renders with opaque red background and bold black text. Prefer targeted local `QMenu` stylesheet in this context to avoid broad global impacts.
  **Must NOT do**: Do not restyle unrelated menus globally.

  **Recommended Agent Profile**:
  - Category: `visual-engineering` — Reason: targeted UI/QSS styling change
  - Skills: [`pyqt6-ui-development-rules`] — PyQt widget/QSS best practices
  - Omitted: [`frontend-ui-ux`] — unnecessary for one control-state update

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: [4] | Blocked By: [1]

  **References** (executor has NO interview context — be exhaustive):
  - Pattern: `src/ui/pipeline_stack_widget.py:207` — current menu/action creation for `Delete Step`
  - Pattern: `src/ui/pipeline_stack_widget.py` (`self.add_menu.setStyleSheet`) — local menu styling precedent
  - Guardrail: `src/ui/main_window.py:apply_styles` — avoid broad theme churn

  **Acceptance Criteria** (agent-executable only):
  - [ ] `Delete Step` action has opaque red item background and bold black text style declaration in active code path.
  - [ ] No unintended style regression for add-node menu entries.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Happy path - destructive style present
    Tool: Bash
    Steps: Run `pytest tests/test_pipeline_execution.py -k "delete_step_style_tokens" -v`
    Expected: Style tokens detected and scoped to delete menu path
    Evidence: .sisyphus/evidence/task-3-delete-style.txt

  Scenario: Failure/edge case - add menu unaffected
    Tool: Bash
    Steps: Run `pytest tests/test_pipeline_execution.py -k "add_menu_style_unchanged_after_delete_style_update" -v`
    Expected: Add-menu styles preserved; only delete affordance altered
    Evidence: .sisyphus/evidence/task-3-delete-style-error.txt
  ```

  **Commit**: YES | Message: `style(ui): emphasize delete step as destructive` | Files: `src/ui/pipeline_stack_widget.py`, `tests/test_pipeline_execution.py`

- [x] 4. Add integration tests for delete-reset semantics

  **What to do**: Extend `tests/test_pipeline_execution.py` with explicit pytest-qt tests for:
  1) input delete resets center + right,
  2) non-input delete preserves context,
  3) folder-input delete disables run gate + hides folder explorer.
  Assert widget and state values directly.
  **Must NOT do**: Do not rely on manual screenshots for acceptance.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: integration behavior locking and regression resistance
  - Skills: [`pyqt6-ui-development-rules`] — robust qtbot signal/widget assertions
  - Omitted: [`playwright`] — desktop PyQt app, not browser UI

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: [5] | Blocked By: [2,3]

  **References** (executor has NO interview context — be exhaustive):
  - Test: `tests/test_pipeline_execution.py` — existing MainWindow integration patterns
  - Pattern: `tests/test_folder_explorer.py` — qtbot interaction/assertion examples
  - Pattern: `src/ui/main_window.py:505` — run-gating expectations
  - API/Type: `src/ui/unified_right_panel.py:683` and `src/ui/unified_right_panel.py:702` — reset and folder explorer visibility behavior

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pytest tests/test_pipeline_execution.py -k "delete_input_node_resets_center_and_right_panel" -v` passes.
  - [ ] `pytest tests/test_pipeline_execution.py -k "delete_non_input_node_preserves_current_image_context" -v` passes.
  - [ ] `pytest tests/test_pipeline_execution.py -k "delete_input_folder_node_disables_run_gate_and_hides_folder_explorer" -v` passes.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Happy path - all three new tests pass
    Tool: Bash
    Steps: Run each targeted pytest command individually
    Expected: 3/3 pass with deterministic assertions
    Evidence: .sisyphus/evidence/task-4-delete-reset-tests.txt

  Scenario: Failure/edge case - non-input deletion regression guard
    Tool: Bash
    Steps: Run `pytest tests/test_pipeline_execution.py -k "delete_non_input_node_preserves_current_image_context" -v`
    Expected: Center/right context remains intact after deleting non-input node
    Evidence: .sisyphus/evidence/task-4-delete-reset-tests-error.txt
  ```

  **Commit**: YES | Message: `test(ui): cover input deletion reset and non-input preservation` | Files: `tests/test_pipeline_execution.py`

- [x] 5. Run focused regression verification for run-gating and batch mode safety

  **What to do**: Execute focused regression suite around run button enablement and folder/single-image mode behavior after introduced reset changes.
  **Must NOT do**: Do not expand into full test-suite overhaul.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` — Reason: validate adjacent behaviors against stale-state regressions
  - Skills: [] — existing pytest commands sufficient
  - Omitted: [`pyqt6-ui-development-rules`] — implementation is complete; this is pure verification

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: [Final Verification Wave] | Blocked By: [4]

  **References** (executor has NO interview context — be exhaustive):
  - Test: `tests/test_pipeline_execution.py` — run/batch behavior coverage
  - Pattern: `src/ui/main_window.py:505` — run enablement logic source

  **Acceptance Criteria** (agent-executable only):
  - [ ] `pytest tests/test_pipeline_execution.py -k "run" -v` passes.
  - [ ] No new failures in touched tests from Tasks 2-4.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Happy path - run gating remains correct
    Tool: Bash
    Steps: Run `pytest tests/test_pipeline_execution.py -k "run" -v`
    Expected: Run gating tests pass in single-image and folder contexts
    Evidence: .sisyphus/evidence/task-5-run-gate-regression.txt

  Scenario: Failure/edge case - stale image path prevented
    Tool: Bash
    Steps: Run `pytest tests/test_pipeline_execution.py -k "delete_input_node_disables_run_with_stale_image_guard" -v`
    Expected: Run is disabled when input node is absent
    Evidence: .sisyphus/evidence/task-5-run-gate-regression-error.txt
  ```

  **Commit**: NO | Message: `n/a` | Files: `n/a`

## Final Verification Wave (4 parallel agents, ALL must APPROVE)
- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high (+ playwright if UI)
- [ ] F4. Scope Fidelity Check — deep

## Commit Strategy
- Commit 1: delete-flow classification + reset routine changes in `src/ui/main_window.py` with paired tests.
- Commit 2: delete-action styling in `src/ui/pipeline_stack_widget.py` with style-scoped test assertion.
- Commit 3: test-only adjustments/regression locks in `tests/test_pipeline_execution.py` if needed.

## Success Criteria
- Requested destructive delete visual is implemented in active UI path.
- Deleting input nodes resets center and right panes deterministically.
- Non-input node deletion remains behaviorally stable.
- Focused pytest-qt verification passes with recorded evidence artifacts.
