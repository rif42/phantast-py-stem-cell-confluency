- Initial tests hung/faulted because `MainWindow` requires a `QApplication`; resolved by keeping the `qtbot` fixture for app bootstrap while avoiding `qtbot.addWidget(window)` (MainWindow is not a QWidget).

- No new blockers encountered for Task 2; targeted mode-switch tests passed on first run.

- No blockers in Task 5; both targeted skip selectors passed after naming the new test to match `-k input_image_folder_skipped`.

- No new blockers encountered for Task 2; targeted mode-switch tests passed on first run.

- No blockers in Task 3; both targeted selectors (, ) passed after first implementation pass.
- Follow-up note: prior shell escaping stripped inline marker text in one append entry; this was corrected with plain-text append lines.
- New batch tests initially triggered Windows fatal exceptions in isolated `-k` runs because `_handle_pipeline_finished()` called `_get_current_metadata()` -> `_get_image_dimensions()`; patched tests by monkeypatching `_get_current_metadata` to a lightweight stub for orchestration-focused assertions.
- No remaining blockers after the metadata stub fix; all three required Task 4 targeted selectors passed.
- `tests/test_folder_explorer.py -k file_list` still fails in this repo baseline with pytest-qt type mismatch (`qtbot.addWidget` rejecting `UnifiedRightPanel` as non-QWidget under mixed Qt bindings); left unchanged per task scope.
- Task 7 had no new blockers; targeted per-input output-path and collision tests passed after adding orchestration coverage.
- Task 8 had no new blockers in `tests/test_pipeline_execution.py`; targeted selectors passed after extending folder success and single-image non-batch regressions.
- Broad suite baseline remains unchanged: `tests/test_folder_explorer.py` still errors in fixture setup at `qtbot.addWidget(UnifiedRightPanel())` with `TypeError: Need to pass a QWidget to addWidget`.
