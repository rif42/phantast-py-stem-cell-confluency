# Report Header - Learnings

## 2026-04-01 Session Start

### Batch Fix Context (from previous work)
- `_start_batch_item()` at line 824: per-image state reset added (clears `_mask_image_path`, `_processed_image_path`, canvas overlay, comparison controls)
- `_queue_next_batch_item_or_complete()`: fixed batch skipping bug — moved `self._batch_current_index = next_index` AFTER `is_running()` check
- `_on_mask_saved()`: deferred overlay during batch via `if not self._is_batch_run_active()`
- Debug `print(..., flush=True)` statements still in main_window.py — to be removed in Task 3
- `build_optimized.bat` updated: entry point `src/main.py`, name `PhantastLab`

### Architecture Notes
- PipelineExecutor is a nested class inside `src/ui/main_window.py` (line 53)
- PipelineWorker is in `src/core/pipeline_worker.py`
- Steps are registered via `register_step` decorator in `src/core/steps/__init__.py`
- `phantast_step.py:process()` currently discards confluency (`_, mask = process_phantast(...)`)
- Thread safety: PipelineWorker runs in QThread — metadata MUST use mutable dict, not function attributes
