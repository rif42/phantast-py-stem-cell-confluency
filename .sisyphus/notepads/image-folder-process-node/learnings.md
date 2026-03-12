- Added `_create_image_folder_node(folder_path)` in `MainWindow` following the pseudo-node lifecycle pattern: remove stale input pseudo-nodes first, then add one fresh input node, then refresh pipeline UI state.
- Folder pseudo-node parameters must store an absolute path (`os.path.abspath`) so downstream execution logic receives canonical folder locations.
- `action_open_folder()` is the correct integration point for folder pseudo-node creation because it already gates on successful folder selection.

-  now mirrors folder-node cleanup by removing both  and  before adding the selected single-image pseudo-node.
- Enforcing symmetric cleanup in both input helpers keeps mode switches deterministic and guarantees one active pseudo input source.

- _create_single_image_node(file_path) now mirrors folder-node cleanup by removing both input_single_image and input_image_folder before adding the selected single-image pseudo-node.
- Enforcing symmetric cleanup in both input helpers keeps mode switches deterministic and guarantees one active pseudo input source.

- `PipelineWorker.process_pipeline()` must treat pseudo input nodes as non-executable (`input_single_image`, `input_image_folder`) so only algorithmic steps enter the execution loop.
- Mirroring the existing `input_single_image` skip-test pattern made it easy to add coverage for `input_image_folder` while still asserting a real step (`clahe`) executes.

- Folder batch snapshot now copies and case-insensitively sorts , then emits absolute paths to keep run-start inputs deterministic and immutable.
- Snapshot filtering now reuses  and excludes filenames containing  or  so generated artifacts are never treated as fresh inputs.
- Folder batch snapshot uses a copied and case-insensitively sorted image_model.files list, then emits absolute paths so run-start inputs are deterministic and immutable.
- Snapshot filtering reuses ImageSessionModel.valid_extensions and excludes names containing _processed or _mask so generated artifacts are not re-queued.
- Folder batch orchestration in MainWindow is stable when modeled as explicit queue state (`_batch_queue`, `_batch_current_index`, `_batch_success_count`, `_batch_failure_count`) plus a queue-advance helper reused by success/error handlers.
- Calling `_queue_next_batch_item_or_complete()` from both `_handle_pipeline_finished` and `_handle_pipeline_error` keeps continue-on-error behavior centralized while preserving the non-batch single-image path unchanged.
- Batch completion metadata is easiest to verify and consume when emitted once at end with aggregate counts in `right_panel.show_metadata` and matching status label text.
- Folder-open integration is more reliable when `action_open_folder()` normalizes selection to `os.path.abspath(...)` once and passes the same canonical value to both `image_controller.handle_open_folder(...)` and `_create_image_folder_node(...)`.
- Reopening folders is safest by reusing the existing `input_image_folder` node (same id) and replacing its `parameters` dict/description atomically, which prevents stale keys from surviving across opens.
- Batch output paths are safest when generated inside `_start_batch_item()` from the queued input at that index, ensuring one `_generate_output_path(...)` call per batch item instead of any shared/global precomputation.
- A focused regression (`test_batch_output_path_per_input_follows_sorted_queue_order`) can lock both invariants at once: sorted input execution order and matching output-generation order.
- Final integration closure is strongest when folder-batch success coverage uses mixed folder contents (eligible images plus `_processed`, `_mask`, and non-image files) and drives `_handle_pipeline_finished(...)` until aggregate completion.
- A dedicated single-image regression should assert `handle_run_pipeline()` starts exactly one run and leaves `_batch_queue`/aggregate counters untouched so folder orchestration changes cannot leak into single-image behavior.
