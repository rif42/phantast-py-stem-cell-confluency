- Implemented folder input pseudo-node as `type="input_image_folder"`, `name="Image Folder"`, with `parameters={"folder_path": abs_path}` to match requested contract.
- `_create_image_folder_node` removes both `input_image_folder` and `input_single_image` nodes before creation to guarantee exactly one active folder input pseudo-node after each folder-open action.
- Added focused regression tests (`image_folder_node_created`, `image_folder_node_replaced`) in `tests/test_pipeline_execution.py` to lock node count/type behavior.

- Kept mode-switch enforcement inside existing helper lifecycle methods instead of adding new orchestration paths, preserving Task 1 behavior and minimizing scope.
- Added explicit regression tests  and  to lock cross-mode cleanup contracts.

- Kept mode-switch enforcement inside existing helper lifecycle methods instead of adding new orchestration paths, preserving Task 1 behavior and minimizing scope.
- Added explicit regression tests test_open_image_clears_folder_input and test_open_folder_clears_single_input to lock cross-mode cleanup contracts.

- Extended executable-node filtering in `PipelineWorker` with a minimal set-membership check so both pseudo input node types are excluded without changing unknown-step handling.
- Added `test_input_image_folder_skipped` in `tests/test_pipeline_execution.py` to lock folder pseudo-node skip behavior and verify algorithmic node execution remains intact.

- Added folder-mode run gating branch in  that requires a non-empty eligible snapshot and at least one enabled executable (non-pseudo) node.
- Kept non-folder run gating unchanged when no  node exists (still gated by current image + any node), matching task scope.
- Implemented folder-mode gate in MainWindow._update_run_button_state requiring eligible snapshot inputs plus at least one enabled executable non-pseudo node.
- Explicitly preserved non-folder gate behavior: when no input_image_folder node exists, run eligibility still follows current image plus existing node count.
- Kept `PipelineExecutor`/`PipelineWorker` as single-image execution engines and implemented all sequential folder orchestration exclusively in `MainWindow` to satisfy scope and minimize threading risk.
- Suppressed per-item modal dialogs only for active batch runs by early-returning in `_handle_pipeline_error` after recording failure and advancing queue; retained existing single-image dialog behavior unchanged.
- Added focused regression tests (`test_folder_batch_run_success`, `test_folder_batch_continue_on_error`, `test_batch_error_no_dialog_spam`) to lock queue order, continue-on-error execution, and no-dialog-spam guarantees.
- Chose in-place refresh for existing `input_image_folder` node on reopen (instead of delete+recreate) to keep node identity stable while still enforcing a single active folder node.
- When refreshing folder node metadata, replaced `parameters` wholesale with `{"folder_path": abs_path}` to guarantee absolute-path contract and eliminate stale parameter carryover.
- Kept `_generate_output_path` as the sole naming/collision mechanism and invoked it per queued batch input in `_start_batch_item`, preserving extension/default and collision-safe behavior.
- Added a dedicated batch orchestration test that monkeypatches `_generate_output_path` to assert input-order parity between sorted queue execution and output-path generation calls.
- Expanded folder success integration coverage by asserting end-to-end auto-processing over all eligible images from a mixed file list while preserving artifact exclusion and sorted queue semantics.
- Added `test_single_image_run_remains_non_batch` to explicitly guard the unchanged single-image path: one executor start, no batch queue activation, and no aggregate batch summary state changes.
