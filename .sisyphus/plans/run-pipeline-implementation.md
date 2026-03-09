# Run Pipeline Feature Implementation Plan

## TL;DR

Implement the complete "Run Pipeline" functionality for PhantastLab, enabling users to execute configured image processing pipelines (CLAHE + PHANTAST) on loaded images with automatic result saving and canvas selection. This plan addresses all identified gaps: unconnected run button, empty execution logic, simplified PHANTAST algorithm, and missing async processing.

**Key Deliverables:**
- Wired run button with enable/disable state management
- Full pipeline execution engine with sequential step processing
- Complete PHANTAST confluency detection algorithm integration
- Automatic output saving and canvas selection
- Progress feedback during execution
- Async processing to prevent UI freezing

**Estimated Effort:** Medium (6-8 tasks across 4 waves)
**Parallel Execution:** YES - 4 waves with final verification
**Critical Path:** Wire signals → Implement execution → Integrate PHANTAST → Async worker → QA

---

## Context

### Original Request
Enable the "Run Pipeline" button to execute configured processing steps (CLAHE with parameters, PHANTAST confluency detection) on the current image, save results, and auto-select on canvas.

### Current State Analysis
- **Run Button**: Exists in UI but NOT connected to any signal
- **Pipeline Execution**: Stub method exists (`_execute_pipeline`) but only reloads original image
- **PHANTAST Step**: Simplified adaptive thresholding - NOT the full algorithm from `phantast_confluency_corrected.py`
- **Output Handling**: No logic for generating output paths or saving processed images
- **Async Processing**: No QThread/Worker pattern implemented - processing would block UI

### Architecture Overview
```
PipelineStackWidget.run_pipeline (signal)
    ↓
MainWindow.handle_run_pipeline (slot)
    ↓
1. Load image from ImageSessionModel
2. Create output path (_processed suffix)
3. Execute enabled nodes sequentially:
   - Get step from STEP_REGISTRY
   - Apply: image = step.process(image, **params)
4. Save result to output path
5. Update ImageSessionModel
6. Load result to ImageCanvas
```

---

## Work Objectives

### Core Objective
Implement end-to-end pipeline execution that processes images through configured CLAHE and PHANTAST steps, saves results, and updates the UI with the processed image.

### Concrete Deliverables
- `src/ui/main_window.py`: Wired run button, execution handler, output path generation
- `src/core/steps/phantast_step.py`: Full PHANTAST algorithm with complete parameter schema
- `src/core/pipeline_worker.py`: Async worker for non-blocking execution (NEW FILE)
- `src/ui/pipeline_stack_widget.py`: Run button state management (optional enhancement)

### Definition of Done
- [ ] Run button enabled only when image loaded AND pipeline has nodes
- [ ] Clicking Run executes all enabled steps in sequence
- [ ] CLAHE applies contrast enhancement with user parameters
- [ ] PHANTAST detects confluency using full algorithm (not simplified)
- [ ] Output saved as `{original}_processed.{ext}` in same directory
- [ ] Saved image auto-selected on canvas
- [ ] Progress feedback shows current step name
- [ ] UI remains responsive during processing (async)

### Must Have
- Full PHANTAST algorithm from `phantast_confluency_corrected.py`
- Proper error handling for file I/O and processing errors
- Run button state tied to both image presence and pipeline configuration
- Output image visible in folder explorer (if folder mode)

### Must NOT Have (Guardrails)
- NO separate processing windows or dialogs
- NO blocking synchronous execution on main thread
- NO hardcoded paths or assumptions about directory structure
- NO modifications to CLAHE step (it already works)
- NO changes to existing signal patterns beyond adding run_pipeline connection

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest + pytest-qt available)
- **Automated tests**: Tests-after (implement feature first, then add tests)
- **Framework**: pytest with pytest-qt for GUI testing
- **Agent-Executed QA**: Every task includes specific QA scenarios

### QA Policy
Every task includes agent-executed QA scenarios with evidence capture:
- **Frontend/UI**: Playwright for browser (not applicable here), pytest-qt for Qt widgets
- **CLI/Processing**: Direct Python execution with assertion checks
- **Evidence**: Screenshots saved to `.sisyphus/evidence/task-{N}-{scenario}.{ext}`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - Start Immediately):
├── Task 1: Wire run button signal in MainWindow [quick]
├── Task 2: Add run button state management [quick]
└── Task 3: Create output path generation utility [quick]

Wave 2 (Core Execution - After Wave 1):
├── Task 4: Implement pipeline execution handler [unspecified-high]
└── Task 5: Integrate full PHANTAST algorithm [deep]

Wave 3 (Async & Polish - After Wave 2):
├── Task 6: Create PipelineWorker for async processing [unspecified-high]
└── Task 7: Add progress feedback and error handling [unspecified-high]

Wave 4 (Verification):
├── Task 8: Integration tests and end-to-end QA [deep]
└── Task 9: Final verification and edge case testing [unspecified-high]

Critical Path: Task 1 → Task 4 → Task 5 → Task 6 → Task 8
Parallel Speedup: ~40% faster than sequential
Max Concurrent: 3 (Wave 1)
```

### Dependency Matrix

- **Task 1**: None → Blocks Task 4, 2
- **Task 2**: None → Blocks Task 4 (co-dependent)
- **Task 3**: None → Blocks Task 4
- **Task 4**: 1, 2, 3 → Blocks Task 6, 7, 8
- **Task 5**: None → Blocks Task 8
- **Task 6**: 4 → Blocks Task 8
- **Task 7**: 4 → Blocks Task 8
- **Task 8**: 4, 5, 6, 7 → Blocks Task 9
- **Task 9**: 8 → Final

### Agent Dispatch Summary

- **Wave 1**: 3 tasks → `quick` agents (T1, T2, T3)
- **Wave 2**: 2 tasks → `unspecified-high` (T4), `deep` (T5)
- **Wave 3**: 2 tasks → `unspecified-high` (T6, T7)
- **Wave 4**: 2 tasks → `deep` (T8), `unspecified-high` (T9)

---

## TODOs

- [ ] 1. Wire Run Button Signal in MainWindow

  **What to do**:
  - In `src/ui/main_window.py`, locate the `wire_signals()` method
  - Add connection: `self.pipeline_stack.run_pipeline.connect(self.handle_run_pipeline)`
  - Create `handle_run_pipeline()` method that calls `_execute_pipeline()`
  - Ensure proper error handling with try/except block

  **Must NOT do**:
  - Do NOT modify pipeline_stack_widget.py signal definition (it already exists)
  - Do NOT change existing signal/slot patterns
  - Do NOT add blocking operations to the handler

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: Simple signal wiring with minimal logic
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 4 (execution handler depends on signal being wired)
  - **Blocked By**: None

  **References**:
  - `src/ui/main_window.py:300-316` - Existing wire_signals() method
  - `src/ui/main_window.py:483-500` - Existing _execute_pipeline() stub
  - `src/ui/pipeline_stack_widget.py:395-397` - Run button definition
  - `src/ui/pipeline_stack_widget.py:30-35` - run_pipeline signal definition

  **Acceptance Criteria**:
  - [ ] `wire_signals()` includes run_pipeline signal connection
  - [ ] `handle_run_pipeline()` method exists and is called on button click
  - [ ] No Qt warnings about unconnected signals

  **QA Scenarios**:

  ```
  Scenario: Run button emits signal
    Tool: Python pytest-qt
    Preconditions: MainWindow instantiated with PipelineStackWidget
    Steps:
      1. Create QApplication and MainWindow
      2. Mock handle_run_pipeline method
      3. Emit pipeline_stack.run_pipeline signal
      4. Assert mock was called exactly once
    Expected Result: Signal properly connected and handler invoked
    Evidence: .sisyphus/evidence/task-1-signal-connection.png (screenshot of test pass)
  ```

  **Commit**: YES
  - Message: `feat(pipeline): wire run button signal to main window handler`
  - Files: `src/ui/main_window.py`

- [ ] 2. Add Run Button State Management

  **What to do**:
  - Create `_update_run_button_state()` method in MainWindow
  - Enable button only when: `current_image_path is not None` AND `len(pipeline.nodes) > 0`
  - Call this method from:
    - `_update_empty_state()` (when image loads/unloads)
    - `handle_add_step()` (when node added)
    - `handle_delete_node()` (when node deleted)
  - Add tooltip "Load an image and add processing steps" when disabled

  **Must NOT do**:
  - Do NOT modify PipelineStackWidget directly (work through MainWindow)
  - Do NOT use hardcoded indices to access pipeline nodes
  - Do NOT forget to handle the case when all nodes are deleted

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: State management logic, straightforward conditions
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 4 (execution depends on proper state)
  - **Blocked By**: None

  **References**:
  - `src/ui/main_window.py:318-336` - _update_empty_state() pattern
  - `src/ui/main_window.py:381-399` - handle_add_step() method
  - `src/ui/main_window.py:441-448` - handle_delete_node() method
  - `src/controllers/pipeline_controller.py` - Pipeline model access

  **Acceptance Criteria**:
  - [ ] Run button disabled when no image loaded
  - [ ] Run button disabled when image loaded but no pipeline nodes
  - [ ] Run button enabled when both image and nodes present
  - [ ] Button state updates immediately on image load/unload
  - [ ] Button state updates immediately on node add/delete

  **QA Scenarios**:

  ```
  Scenario: Button disabled without image
    Tool: pytest-qt
    Preconditions: MainWindow with empty state
    Steps:
      1. Verify current_image_path is None
      2. Verify pipeline.nodes is empty
      3. Check run_button.isEnabled() is False
    Expected Result: Button disabled, tooltip shows "Load an image..."
    Evidence: .sisyphus/evidence/task-2-disabled-no-image.png

  Scenario: Button disabled with image but no nodes
    Tool: pytest-qt
    Preconditions: MainWindow with image loaded
    Steps:
      1. Load test image
      2. Verify pipeline.nodes is empty
      3. Check run_button.isEnabled() is False
    Expected Result: Button disabled, tooltip shows "Add processing steps..."
    Evidence: .sisyphus/evidence/task-2-disabled-no-nodes.png

  Scenario: Button enabled with image and nodes
    Tool: pytest-qt
    Preconditions: MainWindow with image and one CLAHE node
    Steps:
      1. Load test image
      2. Add CLAHE node via controller
      3. Check run_button.isEnabled() is True
    Expected Result: Button enabled, no tooltip
    Evidence: .sisyphus/evidence/task-2-enabled.png
  ```

  **Commit**: YES (group with Task 1)
  - Message: `feat(pipeline): add run button enable/disable state management`
  - Files: `src/ui/main_window.py`

- [ ] 3. Create Output Path Generation Utility

  **What to do**:
  - Create `_generate_output_path(input_path: str) -> str` method in MainWindow
  - Generate path: `{dirname}/{basename}_processed.{ext}`
  - Handle edge cases:
    - Filename already contains "_processed" → append "_processed_1", "_processed_2", etc.
    - Path with no extension → add ".png"
    - Invalid characters in path → sanitize
  - Return absolute path

  **Must NOT do**:
  - Do NOT overwrite existing files without checking
  - Do NOT use hardcoded "output" or "results" directories
  - Do NOT modify the original filename (preserve it, only add suffix)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Reason**: Pure function, path manipulation logic
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 4 (execution needs output path)
  - **Blocked By**: None

  **References**:
  - `src/models/image_model.py:60-61` - Path handling patterns
  - `src/ui/main_window.py` - Where method will be used
  - Python `os.path` module documentation

  **Acceptance Criteria**:
  - [ ] Method returns correct path format: `dir/file_processed.ext`
  - [ ] Handles files without extension
  - [ ] Handles duplicate "_processed" suffixes (increments counter)
  - [ ] Returns absolute paths
  - [ ] Unit tests pass for all edge cases

  **QA Scenarios**:

  ```
  Scenario: Standard filename
    Tool: Python direct execution
    Steps:
      1. Call _generate_output_path("/data/image.jpg")
      2. Assert result equals "/data/image_processed.jpg"
    Expected Result: Correct suffix insertion
    Evidence: .sisyphus/evidence/task-3-standard-path.txt

  Scenario: Already has _processed suffix
    Tool: Python direct execution
    Steps:
      1. Call _generate_output_path("/data/image_processed.jpg")
      2. Assert result equals "/data/image_processed_1.jpg"
      3. Call again with _1 suffix, assert _2
    Expected Result: Incremental numbering
    Evidence: .sisyphus/evidence/task-3-increment.txt

  Scenario: No extension
    Tool: Python direct execution
    Steps:
      1. Call _generate_output_path("/data/image")
      2. Assert result equals "/data/image_processed.png"
    Expected Result: Adds .png extension
    Evidence: .sisyphus/evidence/task-3-no-ext.txt
  ```

  **Commit**: YES (group with Tasks 1-2)
  - Message: `feat(pipeline): add output path generation utility`
  - Files: `src/ui/main_window.py`
  - Pre-commit: `pytest tests/test_output_path.py -v`

- [ ] 4. Implement Pipeline Execution Handler

  **What to do**:
  - Rewrite `_execute_pipeline()` in `src/ui/main_window.py` (lines 483-500)
  - Implement full execution logic:
    1. Get current image path from `self.current_image_path`
    2. Load image with `cv2.imread()`
    3. Generate output path using `_generate_output_path()`
    4. Iterate through `self.pipeline_controller.pipeline.nodes`:
       - Skip if `node.enabled` is False
       - Get step from `STEP_REGISTRY[node.type]`
       - Call `step.process(image, **node.parameters)`
       - Handle grayscale/mask outputs (convert to 3-channel if needed for display)
    5. Save result with `cv2.imwrite()`
    6. Update `ImageSessionModel` with new file (add to folder mode or replace single image)
    7. Call `self.image_canvas.load_image(output_path)`
    8. Update folder explorer if in folder mode
  - Add error handling with try/except and user feedback (QMessageBox or status bar)
  - Use proper OpenCV constants and numpy array handling

  **Must NOT do**:
  - Do NOT block the main thread (prepare for async in Task 6)
  - Do NOT ignore disabled nodes
  - Do NOT modify the original input file
  - Do NOT assume all steps return same array shape (CLAHE returns uint8, PHANTAST returns binary mask)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: Complex orchestration logic with multiple steps and error handling
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 1-3)
  - **Blocks**: Task 6 (async wrapper), Task 7 (progress feedback)
  - **Blocked By**: Task 1 (signal wiring), Task 2 (state management), Task 3 (output path)

  **References**:
  - `src/ui/main_window.py:483-500` - Current stub to replace
  - `src/core/steps/__init__.py:57` - STEP_REGISTRY access
  - `src/core/steps/clahe_step.py:47-78` - CLAHE process function signature
  - `src/core/steps/phantast_step.py:35-70` - PHANTAST process function
  - `src/models/image_model.py` - ImageSessionModel update methods
  - OpenCV cv2.imread/cv2.imwrite documentation
  - NumPy array shape handling (H, W) vs (H, W, 3)

  **Acceptance Criteria**:
  - [ ] Synchronous execution works end-to-end (before adding async)
  - [ ] CLAHE step applies contrast enhancement with stored parameters
  - [ ] PHANTAST step returns binary mask
  - [ ] Output image saved to correct location with _processed suffix
  - [ ] Canvas displays processed image after execution
  - [ ] Errors caught and displayed to user (not silently ignored)

  **QA Scenarios**:

  ```
  Scenario: Execute single CLAHE step
    Tool: pytest-qt + OpenCV
    Preconditions: MainWindow with loaded image and one CLAHE node
    Steps:
      1. Load test image "test.jpg"
      2. Add CLAHE node with clip_limit=4.0, block_size=16
      3. Call _execute_pipeline()
      4. Check output file "test_processed.jpg" exists
      5. Load output with cv2.imread()
      6. Compare histograms - output should have wider distribution
    Expected Result: Output differs from input, file saved correctly
    Evidence: .sisyphus/evidence/task-4-clahe-execution.png

  Scenario: Execute PHANTAST step (before full integration)
    Tool: pytest-qt
    Preconditions: MainWindow with loaded image and PHANTAST node
    Steps:
      1. Load test image
      2. Add PHANTAST node with sigma=2.0, epsilon=0.08
      3. Call _execute_pipeline()
      4. Check output exists and is binary mask (0 or 255 values)
    Expected Result: Binary mask output saved
    Evidence: .sisyphus/evidence/task-4-phantast-basic.png

  Scenario: Skip disabled nodes
    Tool: pytest-qt
    Preconditions: Pipeline with enabled CLAHE and disabled PHANTAST
    Steps:
      1. Add CLAHE (enabled)
      2. Add PHANTAST (disabled)
      3. Execute pipeline
      4. Verify only CLAHE applied (output should be color, not binary)
    Expected Result: Disabled nodes are skipped
    Evidence: .sisyphus/evidence/task-4-skip-disabled.png

  Scenario: Error handling - missing file
    Tool: pytest-qt with monkeypatch
    Steps:
      1. Set current_image_path to non-existent file
      2. Call _execute_pipeline()
      3. Verify error dialog or status message shown
    Expected Result: Graceful error, no crash
    Evidence: .sisyphus/evidence/task-4-error-handling.png
  ```

  **Commit**: YES (separate commit)
  - Message: `feat(pipeline): implement pipeline execution handler`
  - Files: `src/ui/main_window.py`
  - Pre-commit: `pytest tests/test_pipeline_execution.py::test_single_step -v`

- [ ] 5. Integrate Full PHANTAST Algorithm

  **What to do**:
  - Update `src/core/steps/phantast_step.py` to use full PHANTAST algorithm
  - Copy/adapt functions from `phantast_confluency_corrected.py`:
    - `gaussian_filter_separable()`
    - `contrast_stretching()`
    - `local_contrast_cv()` (already exists, enhance it)
    - `kirsch_edge_detection()`
    - `shrink_region()`
    - `halo_removal()`
    - `morphology_majority()`
    - `morphology_clean()`
    - `calculate_confluency()`
    - `process_phantast()` - main entry point
  - Extend parameter schema to include full PHANTAST parameters:
    - sigma (float, default=8.0, 1.0-20.0, step=0.5)
    - epsilon (float, default=0.05, 0.01-0.5, step=0.01)
    - contrast_stretch (bool, default=True)
    - contrast_saturation (float, default=0.5, 0.0-10.0, step=0.1)
    - halo_removal (bool, default=True)
    - min_fill_area (int, default=100, 0-1000, step=10)
    - remove_small_objects (bool, default=True)
    - min_object_area (int, default=100, 0-1000, step=10)
    - max_removal_ratio (float, default=0.3, 0.0-1.0, step=0.05)
  - Update `process()` function to call `process_phantast()` and return binary mask
  - Import numpy, cv2, scipy.ndimage, skimage.measure as needed
  - Maintain `@register_step` decorator

  **Must NOT do**:
  - Do NOT modify CLAHE step (it already works correctly)
  - Do NOT break existing parameter names (sigma, epsilon) - extend, don't replace
  - Do NOT remove simplified version until full version is verified working
  - Do NOT introduce new dependencies beyond what's already imported

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Reason**: Complex algorithm integration with many functions and careful parameter mapping
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 4)
  - **Blocks**: Task 8 (integration testing needs full PHANTAST)
  - **Blocked By**: None

  **References**:
  - `phantast_confluency_corrected.py:1-634` - Full algorithm source
  - `src/core/steps/phantast_step.py:1-75` - Current implementation to enhance
  - `src/core/steps/__init__.py:22-31` - StepParameter schema
  - `src/core/steps/clahe_step.py` - Example of complete step implementation

  **Acceptance Criteria**:
  - [ ] All PHANTAST functions from `phantast_confluency_corrected.py` integrated
  - [ ] Parameter schema includes all 9 PHANTAST parameters
  - [ ] `process()` calls `process_phantast()` and returns binary mask
  - [ ] Confluency calculation result accessible (return or store)
  - [ ] No import errors or missing dependencies
  - [ ] Step registers correctly in STEP_REGISTRY

  **QA Scenarios**:

  ```
  Scenario: Full PHANTAST produces different output than simplified
    Tool: Python with OpenCV
    Preconditions: Test stem cell image
    Steps:
      1. Load test image with cv2.imread()
      2. Call old simplified process() - save result
      3. Call new full process_phantast() - save result
      4. Compare masks - should differ significantly
      5. Verify new output has confluency percentage calculated
    Expected Result: Different (better) segmentation with confluency metric
    Evidence: .sisyphus/evidence/task-5-phantast-comparison.png

  Scenario: All parameters affect output
    Tool: pytest
    Steps:
      1. Test default parameters produce valid mask
      2. Test sigma changes affect smoothing
      3. Test epsilon changes affect threshold
      4. Test disable contrast_stretch changes output
      5. Test disable halo_removal changes output
    Expected Result: Each parameter modification changes output
    Evidence: .sisyphus/evidence/task-5-parameter-tests.txt

  Scenario: Integration with STEP_REGISTRY
    Tool: Python
    Steps:
      1. Import src.core.steps
      2. Get 'phantast' step from STEP_REGISTRY
      3. Verify all 9 parameters defined
      4. Call process() with test image
      5. Verify returns binary mask (0/255)
    Expected Result: Step fully functional via registry
    Evidence: .sisyphus/evidence/task-5-registry-test.txt
  ```

  **Commit**: YES (separate commit)
  - Message: `feat(steps): integrate full PHANTAST confluency detection algorithm`
  - Files: `src/core/steps/phantast_step.py`
  - Pre-commit: `python -c "from src.core.steps import STEP_REGISTRY; print(STEP_REGISTRY['phantast']._asdict())"`

- [ ] 6. Create PipelineWorker for Async Processing

  **What to do**:
  - Create NEW FILE: `src/core/pipeline_worker.py`
  - Implement `PipelineWorker` class inheriting from `QObject` (NOT QThread)
  - Define signals:
    - `started = pyqtSignal()`
    - `progress = pyqtSignal(str, int)`  # step_name, percent
    - `step_completed = pyqtSignal(str, object)`  # step_name, result_array
    - `finished = pyqtSignal(str)`  # output_path
    - `error = pyqtSignal(str)`  # error_message
  - Implement `process_pipeline(input_path, output_path, nodes, step_registry)` slot
  - Load image, iterate nodes, execute steps, save result
  - Emit progress signals between steps
  - Handle errors gracefully and emit error signal
  - Create `PipelineExecutor` helper class in MainWindow to manage worker thread
  - Update `handle_run_pipeline()` to:
    - Create QThread
    - Create PipelineWorker and moveToThread()
    - Connect signals
    - Start thread
    - Disable run button during execution

  **Must NOT do**:
  - Do NOT subclass QThread (use QObject + moveToThread pattern per AGENTS.md)
  - Do NOT update UI directly from worker (use signals only)
  - Do NOT forget to clean up thread when finished
  - Do NOT block main thread waiting for completion

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: Complex threading coordination with proper signal/slot patterns
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 4)
  - **Blocks**: Task 7 (progress feedback depends on worker signals)
  - **Blocked By**: Task 4 (execution logic must be implemented first)

  **References**:
  - AGENTS.md Qt Threading section - "NEVER subclass QThread"
  - `src/ui/main_window.py` - Where executor will be integrated
  - PyQt6 QThread, QObject, moveToThread documentation
  - Signal/slot patterns in existing code (`pipeline_controller.py`, `image_controller.py`)

  **Acceptance Criteria**:
  - [ ] PipelineWorker class created with all required signals
  - [ ] Worker properly moved to QThread using moveToThread()
  - [ ] Main thread remains responsive during processing
  - [ ] Progress signals emitted between processing steps
  - [ ] Error handling with error signal emission
  - [ ] Thread cleanup on completion (quit, wait, deleteLater)
  - [ ] Run button disabled during execution, re-enabled after

  **QA Scenarios**:

  ```
  Scenario: Async execution doesn't block UI
    Tool: pytest-qt
    Preconditions: MainWindow with pipeline
    Steps:
      1. Start pipeline execution
      2. During processing, try to click other buttons (zoom, pan)
      3. Verify UI responds immediately (no freeze)
      4. Wait for completion signal
    Expected Result: UI responsive throughout, buttons clickable
    Evidence: .sisyphus/evidence/task-6-async-responsive.gif (screen recording)

  Scenario: Progress signals emitted correctly
    Tool: pytest-qt
    Steps:
      1. Mock progress signal handler
      2. Run pipeline with 2 steps
      3. Verify progress emitted at least 2 times
      4. Verify step names match node names
    Expected Result: Progress updates for each step
    Evidence: .sisyphus/evidence/task-6-progress-signals.txt

  Scenario: Error handling in worker
    Tool: pytest-qt with monkeypatch
    Steps:
      1. Mock cv2.imread to raise exception
      2. Start pipeline
      3. Verify error signal emitted
      4. Verify thread cleans up properly
    Expected Result: Graceful error, no crash, thread terminated
    Evidence: .sisyphus/evidence/task-6-error-handling.txt

  Scenario: Thread cleanup on success
    Tool: pytest-qt
    Steps:
      1. Run successful pipeline
      2. Verify thread.quit() called
      3. Verify thread.wait() called
      4. Verify deleteLater() called on worker
    Expected Result: No thread leaks
    Evidence: .sisyphus/evidence/task-6-cleanup.txt
  ```

  **Commit**: YES (separate commit)
  - Message: `feat(pipeline): add PipelineWorker for async processing`
  - Files: `src/core/pipeline_worker.py`, `src/ui/main_window.py`
  - Pre-commit: `pytest tests/test_pipeline_worker.py -v`

- [ ] 7. Add Progress Feedback and Error Handling

  **What to do**:
  - Add progress indicator to MainWindow UI:
    - Status bar label showing "Processing: [Step Name]..."
    - Optional: Progress bar (QProgressBar) in status bar or overlay
  - Connect to PipelineWorker signals in `handle_run_pipeline()`:
    - `started` → Show "Processing started"
    - `progress` → Update status label with step name
    - `step_completed` → Log completion (optional)
    - `finished` → Show "Processing complete", enable run button
    - `error` → Show error dialog with message, enable run button
  - Add error dialog helper method `_show_error_dialog(message)`
  - Ensure run button state properly managed:
    - Disabled when execution starts
    - Re-enabled on completion or error
  - Add visual feedback for processing state (optional: change cursor to WaitCursor)

  **Must NOT do**:
  - Do NOT use blocking dialogs during processing
  - Do NOT update progress from worker thread (use signals)
  - Do NOT leave run button disabled on error (must re-enable)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: UI polish with proper state management and error UX
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 6)
  - **Blocks**: Task 8 (integration testing)
  - **Blocked By**: Task 6 (PipelineWorker signals must exist)

  **References**:
  - `src/ui/main_window.py` - Where progress UI will be added
  - QStatusBar, QLabel, QProgressBar documentation
  - QMessageBox.critical() for error dialogs
  - QApplication.setOverrideCursor() for wait cursor

  **Acceptance Criteria**:
  - [ ] Status bar shows current step name during processing
  - [ ] Progress updates visible to user
  - [ ] Error dialog appears on failure with clear message
  - [ ] Run button properly disabled/enabled around execution
  - [ ] No UI freeze or unresponsive behavior

  **QA Scenarios**:

  ```
  Scenario: Progress feedback visible
    Tool: Manual testing + screenshot
    Steps:
      1. Load image and add 2-step pipeline
      2. Click Run
      3. Observe status bar shows "Processing: CLAHE..."
      4. Observe status changes to "Processing: PHANTAST..."
      5. Observe "Processing complete" on finish
    Expected Result: Clear progress indication throughout
    Evidence: .sisyphus/evidence/task-7-progress-feedback.gif

  Scenario: Error dialog on failure
    Tool: pytest-qt with monkeypatch
    Steps:
      1. Mock processing to raise IOError("Disk full")
      2. Start pipeline
      3. Verify QMessageBox.critical() called with error message
      4. Verify run button re-enabled after error
    Expected Result: User-friendly error dialog, UI recoverable
    Evidence: .sisyphus/evidence/task-7-error-dialog.png

  Scenario: Button state during execution
    Tool: pytest-qt
    Steps:
      1. Verify run button enabled before start
      2. Start execution
      3. Verify run button disabled
      4. Wait for completion
      5. Verify run button re-enabled
    Expected Result: Proper state transitions
    Evidence: .sisyphus/evidence/task-7-button-state.txt
  ```

  **Commit**: YES (group with Task 6 or separate)
  - Message: `feat(pipeline): add progress feedback and error handling UI`
  - Files: `src/ui/main_window.py`

- [ ] 8. Integration Tests and End-to-End QA

  **What to do**:
  - Create `tests/test_pipeline_execution.py` with comprehensive tests:
    - Test full pipeline execution (CLAHE → PHANTAST)
    - Test single step pipelines
    - Test disabled node skipping
    - Test output file generation
    - Test canvas update after execution
    - Test error conditions (missing file, invalid path)
  - Create `tests/test_phantast_step.py` with unit tests for full algorithm:
    - Test each sub-function (gaussian_filter_separable, contrast_stretching, etc.)
    - Test parameter variations
    - Test output is valid binary mask
    - Test confluency calculation
  - Create test fixtures in `tests/fixtures/`:
    - Sample stem cell image
    - Expected output masks for regression testing
  - Run all tests and ensure 100% pass rate

  **Must NOT do**:
  - Do NOT skip tests for edge cases
  - Do NOT use production images in tests (create synthetic test images)
  - Do NOT hardcode paths that won't work in CI

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Reason**: Comprehensive test suite with proper fixtures and assertions
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on all previous tasks)
  - **Blocks**: Task 9 (final verification needs tests passing)
  - **Blocked By**: Tasks 4, 5, 6, 7

  **References**:
  - `tests/` directory structure
  - pytest documentation
  - pytest-qt for GUI testing
  - OpenCV image comparison techniques

  **Acceptance Criteria**:
  - [ ] test_pipeline_execution.py created with >10 test cases
  - [ ] test_phantast_step.py created with >8 test cases
  - [ ] All tests pass: `pytest tests/ -v`
  - [ ] Test coverage >80% for new code
  - [ ] CI-ready (no local path dependencies)

  **QA Scenarios**:

  ```
  Scenario: Full pipeline integration test
    Tool: pytest-qt
    Steps:
      1. Create MainWindow with test image
      2. Add CLAHE node (clip_limit=3.0)
      3. Add PHANTAST node (sigma=2.0)
      4. Execute pipeline
      5. Verify output file exists
      6. Verify canvas shows processed image
      7. Verify output different from input
    Expected Result: End-to-end success
    Evidence: .sisyphus/evidence/task-8-full-integration.png

  Scenario: Regression test - PHANTAST output
    Tool: pytest with image comparison
    Steps:
      1. Run PHANTAST on fixture image with known parameters
      2. Compare output to expected mask
      3. Assert similarity > 95%
    Expected Result: Consistent output across runs
    Evidence: .sisyphus/evidence/task-8-regression.txt
  ```

  **Commit**: YES (separate commit)
  - Message: `test(pipeline): add integration tests for pipeline execution`
  - Files: `tests/test_pipeline_execution.py`, `tests/test_phantast_step.py`, `tests/fixtures/*`
  - Pre-commit: `pytest tests/test_pipeline_execution.py tests/test_phantast_step.py -v`

- [ ] 9. Final Verification and Edge Case Testing

  **What to do**:
  - Manual end-to-end testing:
    - Load various image formats (jpg, png, tiff)
    - Test with large images (>10MB)
    - Test with folder mode (output should appear in explorer)
    - Test with single image mode
    - Test rapid start/stop (if cancel implemented)
  - Performance profiling:
    - Measure execution time for typical 2-step pipeline
    - Verify memory usage doesn't leak
  - Cross-platform check (if possible):
    - Windows path handling
    - Unix path handling
  - Documentation:
    - Update any relevant docs with new feature info
    - Add inline comments for complex logic
  - Final code review:
    - Check for TODO/FIXME comments
    - Verify all print statements removed or converted to logging
    - Check parent widget assignments

  **Must NOT do**:
  - Do NOT skip testing on real image data
  - Do NOT ignore performance issues
  - Do NOT leave debug code in production

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Reason**: Manual testing and final polish
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (final task)
  - **Blocked By**: Task 8

  **References**:
  - Test images in project
  - Performance profiling tools (cProfile, memory_profiler)
  - Cross-platform Python path handling (pathlib)

  **Acceptance Criteria**:
  - [ ] Manual testing completed on 3+ image types
  - [ ] Performance acceptable (<30s for 2-step pipeline on typical image)
  - [ ] No memory leaks detected
  - [ ] All edge cases handled gracefully
  - [ ] Code review passed

  **QA Scenarios**:

  ```
  Scenario: Large image performance
    Tool: Manual + timing
    Steps:
      1. Load 20MB TIFF image
      2. Run CLAHE+PHANTAST pipeline
      3. Measure total time
      4. Monitor memory with task manager
    Expected Result: Completes in <60s, no memory spike
    Evidence: .sisyphus/evidence/task-9-performance.txt

  Scenario: Folder mode integration
    Tool: Manual
    Steps:
      1. Open folder with multiple images
      2. Select first image
      3. Run pipeline
      4. Verify output appears in folder explorer
      5. Verify can click output in explorer to view
    Expected Result: Full folder workflow works
    Evidence: .sisyphus/evidence/task-9-folder-mode.png
  ```

  **Commit**: YES (final commit)
  - Message: `chore(pipeline): final verification and documentation updates`
  - Files: Any documentation updates

---

## Final Verification Wave

- [ ] F1. **Integration Test - Full Pipeline Execution**
  
  **What to verify**:
  - Load test image
  - Add CLAHE node (clip_limit=3.0, block_size=16)
  - Add PHANTAST node (sigma=2.0, epsilon=0.08)
  - Click Run Pipeline
  - Verify output file exists with correct name
  - Verify output is displayed on canvas
  - Verify folder explorer shows new file (if in folder mode)
  
  **Tool**: pytest-qt + OpenCV image comparison
  **Expected**: Output image differs from input (CLAHE enhancement applied)
  **Evidence**: `.sisyphus/evidence/integration-test-before.png`, `integration-test-after.png`

- [ ] F2. **Performance Test - Async Execution**
  
  **What to verify**:
  - Start pipeline on large image (10MB+)
  - Verify UI remains responsive (can click other buttons)
  - Measure processing time < 30 seconds for 2-step pipeline
  - Verify progress updates appear during execution
  
  **Tool**: Python time module + pytest-qt
  **Expected**: UI doesn't freeze, progress bar/text updates
  **Evidence**: `.sisyphus/evidence/performance-test-timing.txt`

- [ ] F3. **Edge Case Testing**
  
  **What to verify**:
  - Run with no nodes (should be disabled, but test error handling)
  - Run with disabled nodes only (should show error)
  - Run with invalid image path (should show error dialog)
  - Run with read-only output directory (should show error)
  - Cancel mid-execution (if cancel implemented)
  
  **Tool**: pytest-qt with monkeypatch for error conditions
  **Expected**: Graceful error handling with user-friendly messages
  **Evidence**: `.sisyphus/evidence/edge-case-errors.log`

- [ ] F4. **Code Quality Review**
  
  **What to verify**:
  - Run `ruff check src/`
  - Run type checking if available
  - Verify no `print()` statements (use logging or Qt signals)
  - Check for proper parent widget assignments
  - Verify all new methods have docstrings
  
  **Tool**: ruff + manual review
  **Expected**: Zero lint errors, consistent style
  **Evidence**: `.sisyphus/evidence/quality-check-ruff.txt`

---

## Commit Strategy

- **Wave 1 (Tasks 1-3)**: Single commit
  - `feat(pipeline): wire run button and add state management`
  
- **Wave 2 (Tasks 4-5)**: Two commits
  - `feat(pipeline): implement pipeline execution handler`
  - `feat(steps): integrate full PHANTAST algorithm`
  
- **Wave 3 (Tasks 6-7)**: Two commits
  - `feat(pipeline): add PipelineWorker for async processing`
  - `feat(pipeline): add progress feedback and error handling`
  
- **Wave 4 (Tasks 8-9)**: One commit
  - `test(pipeline): add integration and edge case tests`

---

## Success Criteria

### Verification Commands
```bash
# Run all tests
pytest tests/ -v

# Run specific pipeline tests
pytest tests/test_pipeline_execution.py -v

# Lint check
ruff check src/

# Manual verification
python src/main.py
# 1. Load test image
# 2. Add CLAHE step
# 3. Add PHANTAST step
# 4. Click Run Pipeline
# 5. Verify output appears
```

### Final Checklist
- [ ] Run button enabled/disables correctly based on state
- [ ] Pipeline executes all enabled steps in sequence
- [ ] CLAHE parameters are applied correctly
- [ ] Full PHANTAST algorithm runs (not simplified version)
- [ ] Output saved with _processed suffix in same directory
- [ ] Output auto-selected on canvas after processing
- [ ] UI remains responsive during processing
- [ ] Progress feedback visible during execution
- [ ] Error handling for file I/O and processing errors
- [ ] All tests pass
- [ ] No lint errors
