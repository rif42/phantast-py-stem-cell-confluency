# Image Folder Process Node + Automatic Folder-Wide Run

## TL;DR
> **Summary**: Add a new `image folder` pseudo input node when users open a folder, and execute pipeline runs across all eligible images in that folder automatically when run is triggered.
> **Deliverables**:
> - Auto-create/update single `input_image_folder` pseudo-node on folder open
> - Folder-wide run orchestration with continue-on-error behavior
> - Worker pseudo-node skip update for `input_image_folder`
> - Automated tests for node lifecycle, batch selection/filtering, and run/error flow
> **Effort**: Medium
> **Parallel**: YES - 2 waves
> **Critical Path**: 1 -> 3 -> 4 -> 8

## Context
### Original Request
- "when pressing the \"open folder\" button, add a process node called \"image folder\". when user create a process node and run it, run on all the images inside this folder automatically"

### Interview Summary
- User confirmed single-node lifecycle policy: when Open Folder is used again, update one existing `image folder` node (do not create duplicates).
- User confirmed failure policy: continue processing remaining files when a file fails and report aggregate failures.
- User confirmed test policy: tests-after implementation.

### Metis Review (gaps addressed)
- Added guardrail for input snapshot immutability at run start to prevent mid-run list mutation.
- Added deterministic ordering guardrail (sorted input list) to avoid platform-dependent run order.
- Added stale pseudo-node cleanup guardrail for mode switches (`input_single_image` <-> `input_image_folder`).
- Added explicit acceptance criteria for edge cases: empty folder, corrupt file, output collision, repeated folder opens.

## Work Objectives
### Core Objective
- Implement folder-mode input node and batch run orchestration without refactoring core worker architecture.

### Deliverables
- `MainWindow` auto-adds/updates a single `input_image_folder` node on folder open.
- `MainWindow` removes stale pseudo input node when switching between single-image and folder workflows.
- Pipeline run command executes on a deterministic, filtered snapshot of folder images when folder node is active.
- Batch runs continue across failures and provide one aggregate completion summary.
- `PipelineWorker` ignores `input_image_folder` during executable-step iteration.
- Tests validate behavior and edge cases.

### Definition of Done (verifiable conditions with commands)
- `rtk python -m pytest tests/test_pipeline_execution.py -v` passes with new/updated tests.
- `rtk python -m pytest tests/test_output_path.py -v` still passes (no regression in output naming helper usage).
- `rtk python -m pytest tests/test_folder_explorer.py -v` still passes (no folder UI regressions).
- `rtk python -m pytest tests/ -v` passes locally.

### Must Have
- Exactly one `input_image_folder` pseudo-node exists after each folder-open action.
- Batch input list is snapshotted once at run start, sorted deterministically, and excludes generated artifacts (`*_processed*`, `*_mask*`).
- Continue-on-error behavior records failures and processes remaining inputs.
- Single-image mode remains functional and unchanged when folder pseudo-node is absent.

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- No redesign of batch execution UI panels.
- No parallel processing/concurrency redesign.
- No conversion of `PipelineWorker` into multi-image orchestrator.
- No popup spam for per-item batch failures.
- No creation of additional app windows.

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.
- Test decision: tests-after + `pytest`/`pytest-qt`
- QA policy: Every task includes executable happy + failure scenarios
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks for max parallelism.

Wave 1: core behavior + orchestration foundation (Tasks 1-5)
Wave 2: automated verification + regression validation (Tasks 6-8)

### Dependency Matrix (full, all tasks)
- 1: Blocks 3, 6
- 2: Blocks 6
- 3: Blocks 4, 7
- 4: Blocks 8
- 5: Blocks 8
- 6: Depends on 1, 2
- 7: Depends on 3
- 8: Depends on 4, 5

### Agent Dispatch Summary (wave -> task count -> categories)
- Wave 1 -> 5 tasks -> `unspecified-high`, `quick`
- Wave 2 -> 3 tasks -> `quick`, `unspecified-high`

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: Agent Profile + Parallelization + QA Scenarios.

- [x] 1. Add `input_image_folder` pseudo-node lifecycle on folder open

  **What to do**: In `MainWindow`, implement `_create_image_folder_node(folder_path)` that (a) removes any existing `input_image_folder`, (b) removes stale `input_single_image`, (c) creates exactly one new pseudo-node with `step_type="input_image_folder"`, name `Image Folder`, and parameters containing absolute `folder_path`, then (d) refreshes pipeline view and run-button state. Call this helper from `action_open_folder()` after successful folder selection.
  **Must NOT do**: Do not register `input_image_folder` in `STEP_REGISTRY`; do not create duplicate folder pseudo-nodes; do not add new windows/dialogs.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: touches central UI orchestration state and pseudo-node lifecycle.
  - Skills: `[]` - no special external skill needed.
  - Omitted: `playwright` - unnecessary for this code-first task.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 3, 6 | Blocked By: none

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `src/ui/main_window.py` - existing `_create_single_image_node()` single-instance pseudo-node lifecycle.
  - Entry point: `src/ui/main_window.py` - `action_open_folder()` folder-open flow.
  - Node model: `src/models/pipeline_model.py` - `PipelineNode` dataclass contract.
  - Controller add path: `src/controllers/pipeline_controller.py` - node add/remove and refresh behavior.
  - Test pattern: `tests/test_pipeline_execution.py` - existing MainWindow callback and pseudo-node tests.

  **Acceptance Criteria** (agent-executable only):
  - [ ] New test proving one `input_image_folder` node is created on folder open passes: `rtk python -m pytest tests/test_pipeline_execution.py -k image_folder_node_created -v`
  - [ ] New test proving repeated folder open updates/replaces to one node passes: `rtk python -m pytest tests/test_pipeline_execution.py -k image_folder_node_replaced -v`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```
  Scenario: Happy path - folder open creates one folder pseudo-node
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k image_folder_node_created -v`
    Expected: Test passes and asserts exactly one `input_image_folder` node exists with selected folder path.
    Evidence: .sisyphus/evidence/task-1-image-folder-node.txt

  Scenario: Failure/edge case - repeated folder open does not duplicate nodes
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k image_folder_node_replaced -v`
    Expected: Test passes and asserts old node removed/replaced and final count remains 1.
    Evidence: .sisyphus/evidence/task-1-image-folder-node-error.txt
  ```

  **Commit**: NO | Message: `feat(ui): add image folder pseudo-node on folder open` | Files: `src/ui/main_window.py`, `tests/test_pipeline_execution.py`

- [x] 2. Enforce single active input source when switching modes

  **What to do**: Ensure `action_open_image()` removes any existing `input_image_folder` node before creating `input_single_image`; ensure `action_open_folder()` removes `input_single_image` through the new folder helper. Maintain exactly one active pseudo input source at any time.
  **Must NOT do**: Do not alter non-input processing nodes; do not clear full pipeline; do not change drag/drop constraints.

  **Recommended Agent Profile**:
  - Category: `quick` - Reason: focused lifecycle guard around existing actions.
  - Skills: `[]` - straightforward codebase-local update.
  - Omitted: `frontend-ui-ux` - no visual redesign required.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 6 | Blocked By: none

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `src/ui/main_window.py` - `action_open_image()` + `_create_single_image_node()`.
  - Folder action: `src/ui/main_window.py` - `action_open_folder()`.
  - Node list ownership: `src/controllers/pipeline_controller.py` and `src/models/pipeline_model.py`.
  - Existing pseudo-node skip semantics: `src/core/pipeline_worker.py` filter for `input_single_image`.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Test for image-open path removing folder pseudo-node passes: `rtk python -m pytest tests/test_pipeline_execution.py -k open_image_clears_folder_input -v`
  - [ ] Test for folder-open path removing single-image pseudo-node passes: `rtk python -m pytest tests/test_pipeline_execution.py -k open_folder_clears_single_input -v`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```
  Scenario: Happy path - open image after folder mode keeps only single-image input
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k open_image_clears_folder_input -v`
    Expected: Test passes and pipeline has one `input_single_image` and zero `input_image_folder` nodes.
    Evidence: .sisyphus/evidence/task-2-input-mode-switch.txt

  Scenario: Failure/edge case - open folder after image mode keeps only folder input
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k open_folder_clears_single_input -v`
    Expected: Test passes and pipeline has one `input_image_folder` and zero `input_single_image` nodes.
    Evidence: .sisyphus/evidence/task-2-input-mode-switch-error.txt
  ```

  **Commit**: NO | Message: `fix(ui): enforce single active input pseudo-node` | Files: `src/ui/main_window.py`, `tests/test_pipeline_execution.py`

- [x] 3. Build deterministic folder batch input snapshot + run eligibility checks

  **What to do**: Add `MainWindow` helper to collect batch inputs from folder mode as an immutable run-start snapshot: absolute paths, sorted deterministically, filtered to valid image extensions, excluding generated artifacts (`*_processed*`, `*_mask*`). Update run eligibility logic so folder mode can run when snapshot has inputs, and keep single-image gating unchanged when folder pseudo-node is absent.
  **Must NOT do**: Do not rescan filesystem during active batch; do not mutate `image_model.files` while collecting; do not include files generated mid-run.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: run preconditions and file-selection rules are correctness-critical.
  - Skills: `[]` - no external tooling required.
  - Omitted: `playwright` - behavior is testable via pytest.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4, 7 | Blocked By: 1

  **References** (executor has NO interview context - be exhaustive):
  - Folder state source: `src/models/image_model.py` - `set_folder()` / `files` / mode behavior.
  - Current run gate: `src/ui/main_window.py` - `_update_run_button_state()` and `handle_run_pipeline()`.
  - Existing extension handling: `src/models/image_model.py` valid extension filtering pattern.
  - Output artifact naming pattern: `src/ui/main_window.py` `_generate_output_path()` and mask save path logic in `src/core/pipeline_worker.py`.
  - Test support: `tests/test_output_path.py`, `tests/test_pipeline_execution.py`.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Test proving snapshot sorting/filtering/exclusion rules passes: `rtk python -m pytest tests/test_pipeline_execution.py -k batch_input_snapshot_filtering -v`
  - [ ] Test proving run-button eligibility in folder mode is correct passes: `rtk python -m pytest tests/test_pipeline_execution.py -k folder_mode_run_gate -v`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```
  Scenario: Happy path - mixed folder contents produce deterministic eligible snapshot
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k batch_input_snapshot_filtering -v`
    Expected: Test passes; snapshot order is deterministic and excludes `_processed`/`_mask` artifacts.
    Evidence: .sisyphus/evidence/task-3-batch-snapshot.txt

  Scenario: Failure/edge case - empty or artifact-only folder disables run
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k folder_mode_run_gate -v`
    Expected: Test passes; run is not enabled when no eligible inputs exist.
    Evidence: .sisyphus/evidence/task-3-batch-snapshot-error.txt
  ```

  **Commit**: NO | Message: `feat(run): add deterministic folder batch input snapshot rules` | Files: `src/ui/main_window.py`, `tests/test_pipeline_execution.py`

- [x] 4. Implement sequential folder batch orchestration with continue-on-error summary

  **What to do**: Extend `MainWindow` run orchestration to process folder snapshot sequentially using existing `PipelineExecutor` one image at a time. Add batch state fields (queue/current index/successes/failures). In batch mode: on item success, queue next; on item error, record failure and continue; on completion, emit one aggregate summary in status metadata. Keep single-image run flow and UX unchanged when not in batch mode.
  **Must NOT do**: Do not redesign worker threading model; do not stop entire batch on first failure; do not show per-item modal error dialogs in batch mode.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: non-trivial async state-machine behavior with error routing.
  - Skills: `[]` - project-local orchestration work.
  - Omitted: `git-master` - no git workflow needed at implementation step.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 8 | Blocked By: 3

  **References** (executor has NO interview context - be exhaustive):
  - Async runner: `src/ui/main_window.py` `PipelineExecutor.start()` wiring and run callbacks.
  - Existing callbacks: `src/ui/main_window.py` `_handle_pipeline_finished()`, `_handle_pipeline_error()`.
  - Existing worker contract: `src/core/pipeline_worker.py` signals `finished`, `error`, `progress`, `step_completed`.
  - Status/UI update path: `src/ui/main_window.py` status panel updates and metadata setters.
  - Error handling tests: `tests/test_pipeline_execution.py` error path assertions.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Batch success-flow test passes: `rtk python -m pytest tests/test_pipeline_execution.py -k folder_batch_run_success -v`
  - [ ] Continue-on-error behavior test passes: `rtk python -m pytest tests/test_pipeline_execution.py -k folder_batch_continue_on_error -v`
  - [ ] No per-item modal error in batch-mode test passes: `rtk python -m pytest tests/test_pipeline_execution.py -k batch_error_no_dialog_spam -v`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```
  Scenario: Happy path - all folder images run sequentially
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k folder_batch_run_success -v`
    Expected: Test passes; all eligible images are processed once and summary reports full success count.
    Evidence: .sisyphus/evidence/task-4-batch-orchestration.txt

  Scenario: Failure/edge case - one image fails and batch continues
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k folder_batch_continue_on_error -v`
    Expected: Test passes; failure is recorded, subsequent images still run, and end summary includes fail count.
    Evidence: .sisyphus/evidence/task-4-batch-orchestration-error.txt
  ```

  **Commit**: YES | Message: `feat(run): process folder images sequentially with continue-on-error` | Files: `src/ui/main_window.py`, `tests/test_pipeline_execution.py`

- [x] 5. Extend worker pseudo-node skip logic for folder input node

  **What to do**: Update `PipelineWorker.process_pipeline()` executable-node filtering to skip `input_image_folder` in addition to `input_single_image`. Preserve all existing execution semantics for enabled algorithmic steps.
  **Must NOT do**: Do not skip real processing nodes; do not alter image load/save logic or `phantast` mask-save behavior.

  **Recommended Agent Profile**:
  - Category: `quick` - Reason: focused one-file logic extension with direct tests.
  - Skills: `[]` - no external dependencies.
  - Omitted: `frontend-ui-ux` - backend processing path only.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 8 | Blocked By: none

  **References** (executor has NO interview context - be exhaustive):
  - Filter location: `src/core/pipeline_worker.py` executable-node construction in `process_pipeline()`.
  - Existing pseudo-node pattern: `input_single_image` skip logic in same function.
  - Regression tests: `tests/test_pipeline_execution.py` existing `input_single_image` skip test.

  **Acceptance Criteria** (agent-executable only):
  - [ ] New test proving `input_image_folder` is skipped passes: `rtk python -m pytest tests/test_pipeline_execution.py -k input_image_folder_skipped -v`
  - [ ] Existing skip and worker tests remain green: `rtk python -m pytest tests/test_pipeline_execution.py -k skipped -v`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```
  Scenario: Happy path - worker ignores folder pseudo-node and runs real steps
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k input_image_folder_skipped -v`
    Expected: Test passes and confirms executable steps exclude `input_image_folder`.
    Evidence: .sisyphus/evidence/task-5-worker-skip.txt

  Scenario: Failure/edge case - unknown real step still errors correctly
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k unknown_step -v`
    Expected: Test passes and confirms skip logic changes do not mask unknown-step errors.
    Evidence: .sisyphus/evidence/task-5-worker-skip-error.txt
  ```

  **Commit**: NO | Message: `fix(worker): skip image folder pseudo-node during execution` | Files: `src/core/pipeline_worker.py`, `tests/test_pipeline_execution.py`

- [x] 6. Lock folder-node metadata updates and folder-open integration correctness

  **What to do**: Ensure folder pseudo-node metadata remains accurate when reopening same/different folders (e.g., description shows current folder basename). Guarantee the node parameter payload is always absolute path and that repeated opens update existing node cleanly.
  **Must NOT do**: Do not alter model scanning rules in `ImageSessionModel`; do not add recursive scanning.

  **Recommended Agent Profile**:
  - Category: `quick` - Reason: constrained correctness pass on folder-node integration.
  - Skills: `[]` - local behavior refinement.
  - Omitted: `playwright` - can be validated via pytest-level behavior tests.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: none | Blocked By: 1, 2

  **References** (executor has NO interview context - be exhaustive):
  - Folder-open flow: `src/ui/main_window.py` `action_open_folder()`.
  - Model folder state: `src/models/image_model.py` `set_folder()` and `files`.
  - Existing folder UI behavior: `tests/test_folder_explorer.py` list update patterns.
  - Node data model: `src/models/pipeline_model.py`.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Test for folder-node parameter/description refresh passes: `rtk python -m pytest tests/test_pipeline_execution.py -k image_folder_node_metadata_refresh -v`
  - [ ] Folder explorer regression test subset remains green: `rtk python -m pytest tests/test_folder_explorer.py -k file_list -v`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```
  Scenario: Happy path - reopening different folders updates node metadata
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k image_folder_node_metadata_refresh -v`
    Expected: Test passes; node params/description reflect latest opened folder only.
    Evidence: .sisyphus/evidence/task-6-folder-node-metadata.txt

  Scenario: Failure/edge case - non-image files do not break folder integration
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_folder_explorer.py -k empty -v`
    Expected: Test passes; UI handles empty/non-image list states without crashes.
    Evidence: .sisyphus/evidence/task-6-folder-node-metadata-error.txt
  ```

  **Commit**: NO | Message: `fix(ui): keep image folder pseudo-node metadata current` | Files: `src/ui/main_window.py`, `tests/test_pipeline_execution.py`, `tests/test_folder_explorer.py`

- [x] 7. Guarantee per-image output-path generation and deterministic batch order

  **What to do**: In batch orchestration, call `_generate_output_path()` per queued input file (not once globally), preserving collision-safe naming and extension handling for each source image. Assert sorted execution order is the same order used for output generation.
  **Must NOT do**: Do not hardcode output suffixes outside `_generate_output_path`; do not overwrite existing files silently.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: subtle correctness around output naming/order invariants.
  - Skills: `[]` - internal helper-based implementation.
  - Omitted: `git-master` - not needed for coding path.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 8 | Blocked By: 3, 4

  **References** (executor has NO interview context - be exhaustive):
  - Naming helper: `src/ui/main_window.py` `_generate_output_path()`.
  - Existing naming tests: `tests/test_output_path.py`.
  - Batch queue origin: `src/ui/main_window.py` new snapshot helper and run orchestration methods.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Batch output-path-per-input test passes: `rtk python -m pytest tests/test_pipeline_execution.py -k batch_output_path_per_input -v`
  - [ ] Existing output path test suite still passes: `rtk python -m pytest tests/test_output_path.py -v`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```
  Scenario: Happy path - sorted input order maps to one generated output each
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k batch_output_path_per_input -v`
    Expected: Test passes; output-path generation invoked once per input in deterministic order.
    Evidence: .sisyphus/evidence/task-7-output-order.txt

  Scenario: Failure/edge case - pre-existing processed output triggers suffix increment
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_output_path.py -k existing -v`
    Expected: Test passes; collision-safe increment behavior unchanged.
    Evidence: .sisyphus/evidence/task-7-output-order-error.txt
  ```

  **Commit**: NO | Message: `fix(run): apply output-path helper per folder batch item` | Files: `src/ui/main_window.py`, `tests/test_pipeline_execution.py`, `tests/test_output_path.py`

- [x] 8. Final folder-mode vs single-image integration regression closure

  **What to do**: Complete integration coverage proving: folder mode auto-processes all eligible images; continue-on-error summary reports correct counts; single-image mode remains unchanged. Update/extend existing pipeline execution tests and run targeted + full suite.
  **Must NOT do**: Do not add manual-only verification; do not leave flaky timing-dependent assertions.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: broad integration closure across UI orchestration and worker boundaries.
  - Skills: `[]` - standard pytest/pytest-qt patterns in repo are sufficient.
  - Omitted: `playwright` - GUI browser automation not applicable to PyQt unit/integration scope here.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: none | Blocked By: 4, 5, 7

  **References** (executor has NO interview context - be exhaustive):
  - Main orchestration: `src/ui/main_window.py` run flow + callbacks.
  - Worker execution path: `src/core/pipeline_worker.py`.
  - Existing integration baseline: `tests/test_pipeline_execution.py`.
  - Folder UI baseline: `tests/test_folder_explorer.py`.
  - Output naming baseline: `tests/test_output_path.py`.

  **Acceptance Criteria** (agent-executable only):
  - [ ] Folder integration test block passes: `rtk python -m pytest tests/test_pipeline_execution.py -k "folder_batch or image_folder_node" -v`
  - [ ] Single-image regression block passes: `rtk python -m pytest tests/test_pipeline_execution.py -k single_image -v`
  - [ ] Full test suite passes: `rtk python -m pytest tests/ -v`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```
  Scenario: Happy path - folder run processes all eligible images end-to-end
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k folder_batch_run_success -v`
    Expected: Test passes with expected success count and generated outputs.
    Evidence: .sisyphus/evidence/task-8-integration-closure.txt

  Scenario: Failure/edge case - one corrupt input reported while others succeed
    Tool: Bash
    Steps: Run `rtk python -m pytest tests/test_pipeline_execution.py -k folder_batch_continue_on_error -v`
    Expected: Test passes and summary contains both success and failure counts.
    Evidence: .sisyphus/evidence/task-8-integration-closure-error.txt
  ```

  **Commit**: YES | Message: `test(pipeline): validate folder auto-batch run and single-image regressions` | Files: `tests/test_pipeline_execution.py`, `tests/test_output_path.py`, `tests/test_folder_explorer.py`

## Final Verification Wave (4 parallel agents, ALL must APPROVE)
- [x] F1. Plan Compliance Audit - oracle
- [x] F2. Code Quality Review - unspecified-high
- [x] F3. Real Manual QA - unspecified-high (+ playwright if UI)
- [x] F4. Scope Fidelity Check - deep

## Commit Strategy
- Commit 1: `feat(ui): add image folder pseudo-node lifecycle in main window`
- Commit 2: `feat(pipeline): run folder pipelines across image snapshot with continue-on-error`
- Commit 3: `test(pipeline): cover folder node lifecycle and batch orchestration edge cases`

## Success Criteria
- Opening a folder always results in one updated `image folder` pseudo-node in pipeline state.
- Running pipeline in folder mode executes against every eligible folder image automatically.
- A corrupted image does not abort the whole run; summary clearly reports pass/fail counts.
- Existing single-image processing path remains intact.
- All targeted and full test suites pass.
