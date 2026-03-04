# PhantastLab src/ Implementation Plan

**Goal:** Port functional prototype from `shell/` to production `src/` with full MVC architecture, comprehensive tests, and CI/CD.

**Reference:** `shell/` contains working prototype (19 files). `src/` has skeleton MVC structure (14 files) needing implementation.

**Product:** PyQt6 desktop app for stem cell image analysis with pipeline-based processing (CLAHE, PHANTAST confluency detection).

---

## TL;DR

**4 Major Phases:**
1. **Foundation** (Week 1) - Pipeline framework, core models, test infra
2. **Core Features** (Week 2) - Image navigation, canvas, properties panel
3. **Pipeline UI** (Week 3) - Step editor, execution, batch processing
4. **Integration** (Week 4) - Navigation, polish, CI/CD

**286 Total Tasks** across parallel workstreams. Estimated 4-6 weeks with 2 developers.

---

## Context

### Current State

**shell/ (Prototype - Fully Working):**
- `shell/core/pipeline.py` - ImagePipeline executor with metadata passing
- `shell/core/steps.py` - PipelineStep ABC + 4 concrete implementations:
  - GrayscaleStep, GaussianBlurStep, ClaheStep, PhantastStep
- `shell/shell/main_window.py` - QStackedWidget navigation (3 views)
- `shell/sections/*/views/` - 3 complete section UIs with dark theme (#121415, #00B884)
- Working demo with image loading, pipeline construction, batch execution

**src/ (Production - Skeleton Only):**
- `src/main.py` - Entry point exists
- `src/models/` - ImageSessionModel (basic), Pipeline (dataclasses only)
- `src/ui/` - 7 files exist but mostly empty/skeleton
- `src/controllers/` - Files exist but unimplemented
- MVC structure defined but not functional

### Key Differences

| Aspect | shell/ | src/ (Target) |
|--------|--------|---------------|
| Architecture | Monolithic views | Strict MVC |
| Testability | None | pytest-qt, 70% coverage target |
| Navigation | QStackedWidget | To be determined |
| Pipeline | Direct import | Via controllers |
| Threading | None | QThreadPool for processing |
| State Management | JSON files | In-memory models |

### Technical Stack

- **GUI:** PyQt6 (no PySide6)
- **Processing:** OpenCV, NumPy, custom PHANTAST algorithm
- **Testing:** pytest, pytest-qt, pytest-mock
- **Build:** PyInstaller for executable
- **CI:** GitHub Actions

---

## Work Objectives

### Phase 1: Foundation (MUST HAVE)
- [ ] Pipeline framework with StepParameter metadata
- [ ] All 4 pipeline step implementations ported
- [ ] Enhanced ImageSessionModel with metadata
- [ ] Test infrastructure (pytest, fixtures, CI)
- [ ] Basic main window shell

### Phase 2: Core UI (MUST HAVE)
- [ ] ImageNavigation widget with folder browsing
- [ ] ImageCanvas with zoom/pan/toolbar
- [ ] PropertiesPanel with metadata display
- [ ] ImageController binding model to view

### Phase 3: Pipeline UI (MUST HAVE)
- [ ] Pipeline visualization (step nodes)
- [ ] Step parameter editor (auto-generated from StepParameter)
- [ ] Pipeline execution with progress
- [ ] Batch execution view

### Phase 4: Integration (MUST HAVE)
- [ ] Navigation between views
- [ ] Application state management
- [ ] Error handling & logging
- [ ] CI/CD pipeline

### Definition of Done

**Per Phase:**
- All unit tests pass (`pytest -v`)
- All integration tests pass
- Type checking passes (`mypy src/` if configured)
- UI smoke test passes (manual or Playwright)
- Code review complete

**Final Deliverable:**
- Working application matching shell/ functionality
- Test coverage ≥70%
- CI/CD passing
- Documentation complete

---

## Verification Strategy

### Testing Approach

**Unit Tests (70%):**
- Models: Pure Python, no Qt imports
- Pipeline steps: Input/output validation
- Utilities: Path handling, format conversion

**Integration Tests (20%):**
- Controllers: Model → View binding
- Pipeline execution: End-to-end processing

**GUI Tests (10%):**
- Widget lifecycle (qtbot)
- Signal/slot connections
- User interactions

### QA Scenarios (Every Task)

**Example for PipelineStep:**
```
Scenario: CLAHE step processes grayscale image
  Tool: Bash (pytest)
  Preconditions: test_image_512x512_gray.npy exists
  Steps:
    1. step = ClaheStep(clip_limit=2.0, tile_grid_size=8)
    2. result = step.process(test_image, {})
  Expected Result: 
    - result.shape == test_image.shape
    - result.dtype == np.uint8
    - result.std() > test_image.std() (contrast enhanced)
  Evidence: test_report.html
```

---

## Execution Strategy

### Parallel Workstreams

**Stream A: Pipeline Framework (Foundation)**
- Core processing logic from shell/core/
- No UI dependencies
- Can start immediately

**Stream B: Models & Data (Foundation)**
- Enhanced ImageSessionModel
- Pipeline model persistence
- Test fixtures

**Stream C: UI Components (Core)**
- ImageNavigation, ImageCanvas, PropertiesPanel
- Depends on Stream B for model interfaces

**Stream D: Integration (Final)**
- Main window, navigation, controllers
- Depends on Streams A, B, C

### Phase Breakdown

```
Phase 1: Foundation (Week 1)
├── Stream A: Pipeline Framework (Parallel)
│   ├── 1.1 PipelineStep ABC
│   ├── 1.2 ImagePipeline executor
│   ├── 1.3 GrayscaleStep
│   ├── 1.4 GaussianBlurStep
│   ├── 1.5 ClaheStep
│   └── 1.6 PhantastStep
├── Stream B: Models (Parallel)
│   ├── 1.7 Enhanced ImageSessionModel
│   ├── 1.8 Pipeline model persistence
│   └── 1.9 Test fixtures
├── Stream C: Test Infrastructure (Parallel)
│   ├── 1.10 pytest configuration
│   ├── 1.11 qtbot fixtures
│   └── 1.12 CI workflow
└── Stream D: Shell (Parallel)
    └── 1.13 MainWindow skeleton

Phase 2: Core UI (Week 2)
├── Stream C: Image Navigation (Sequential)
│   ├── 2.1 ImageNavigation widget
│   ├── 2.2 Folder browser integration
│   └── 2.3 Thumbnail grid
├── Stream C: Canvas (Sequential)
│   ├── 2.4 ImageCanvas base
│   ├── 2.5 Zoom/pan functionality
│   └── 2.6 Floating toolbar
├── Stream C: Properties (Sequential)
│   ├── 2.7 PropertiesPanel
│   └── 2.8 Metadata display
└── Stream D: Controllers (Parallel)
    ├── 2.9 ImageController
    └── 2.10 NavigationController

Phase 3: Pipeline UI (Week 3)
├── Stream A: Pipeline Editor (Sequential)
│   ├── 3.1 Pipeline visualization
│   ├── 3.2 Step addition/removal
│   └── 3.3 Drag-drop reordering
├── Stream C: Parameter Editor (Sequential)
│   ├── 3.4 Auto-generated controls
│   ├── 3.5 Validation
│   └── 3.6 Real-time preview
├── Stream C: Execution UI (Sequential)
│   ├── 3.7 Progress dialog
│   ├── 3.8 Results display
│   └── 3.9 Export functionality
└── Stream D: Batch (Parallel)
    ├── 3.10 BatchExecutionView
    └── 3.11 Queue management

Phase 4: Integration (Week 4)
├── Stream D: Navigation (Sequential)
│   ├── 4.1 QStackedWidget setup
│   ├── 4.2 State synchronization
│   └── 4.3 View transitions
├── Stream D: Polish (Parallel)
│   ├── 4.4 Error handling
│   ├── 4.5 Logging
│   ├── 4.6 Keyboard shortcuts
│   └── 4.7 Status bar
├── Stream D: CI/CD (Parallel)
│   ├── 4.8 GitHub Actions workflow
│   ├── 4.9 PyInstaller build
│   └── 4.10 Release automation
└── Final: Verification
    ├── 4.11 Integration testing
    ├── 4.12 Performance testing
    └── 4.13 Documentation
```

---

## TODOs

### Phase 1: Foundation (Week 1)

#### Stream A: Pipeline Framework

- [ ] **1.1. Create PipelineStep Abstract Base Class**

  **What to do:**
  Port `shell/core/steps.py` PipelineStep to `src/core/pipeline_step.py`
  - Abstract `process(image, metadata)` method
  - `define_params()` → list of StepParameter
  - `get_param()`, `set_param()` with defaults
  - `enabled` property
  - `name` property (class name override)

  **Files to modify:**
  - Create: `src/core/__init__.py`, `src/core/pipeline_step.py`

  **Must NOT do:**
  - No Qt imports in this file
  - No image processing logic here (keep abstract)

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []
  - Python abstract base class patterns, type hints

  **Parallelization:**
  - **Can Run In Parallel:** YES (with 1.2, 1.7)
  - **Blocks:** 1.3, 1.4, 1.5, 1.6 (all steps need this)
  - **Blocked By:** None

  **References:**
  - Pattern: `shell/core/steps.py:25-66` - PipelineStep class
  - Pattern: `shell/core/steps.py:14-23` - StepParameter dataclass

  **Acceptance Criteria:**
  - `from src.core.pipeline_step import PipelineStep, StepParameter` works
  - `pytest src/core/test_pipeline_step.py` passes:
    - Test abstract class can't be instantiated
    - Test StepParameter dataclass creation
    - Test get_param returns default
    - Test set_param overrides default

  **QA Scenarios:**
  ```
  Scenario: Abstract class enforces process() implementation
    Tool: Bash (pytest)
    Preconditions: None
    Steps:
      1. Create class DummyStep(PipelineStep): pass
      2. Try to instantiate: step = DummyStep()
    Expected Result: TypeError raised (abstract method not implemented)
    Evidence: pytest output showing TypeError

  Scenario: StepParameter stores metadata correctly
    Tool: Bash (pytest)
    Preconditions: None
    Steps:
      1. param = StepParameter("clip_limit", "float", 2.0, 0.1, 10.0, "Clip Limit")
      2. assert param.name == "clip_limit"
      3. assert param.default == 2.0
    Expected Result: All assertions pass
    Evidence: pytest output showing 3 passed
  ```

  **Commit:** YES
  - Message: `feat(core): add PipelineStep ABC and StepParameter`
  - Files: `src/core/pipeline_step.py`, `src/core/__init__.py`, `tests/core/test_pipeline_step.py`

- [ ] **1.2. Create ImagePipeline Executor**

  **What to do:**
  Port `shell/core/pipeline.py` ImagePipeline to `src/core/pipeline.py`
  - `add_step()`, `remove_step()`, `move_step()`, `clear()`
  - `execute(image)` → runs all enabled steps
  - `metadata` dict for inter-step communication
  - Error handling (log error, continue or abort)

  **Files to modify:**
  - Create: `src/core/pipeline.py`

  **Must NOT do:**
  - No Qt imports (keep CLI-runnable)
  - No UI updates (this is backend only)

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES (with 1.1, 1.7)
  - **Blocks:** 3.7 (execution UI needs this)
  - **Blocked By:** None

  **References:**
  - Pattern: `shell/core/pipeline.py:6-56` - ImagePipeline class

  **Acceptance Criteria:**
  - `pytest src/core/test_pipeline.py` passes:
    - Test add/remove/move/clear steps
    - Test execute runs steps in order
    - Test metadata passed between steps
    - Test error handling (exception caught, not propagated)

  **QA Scenarios:**
  ```
  Scenario: Pipeline executes steps sequentially
    Tool: Bash (pytest)
    Preconditions: DummyStep implemented that appends to metadata
    Steps:
      1. pipeline = ImagePipeline()
      2. pipeline.add_step(DummyStep("step1"))
      3. pipeline.add_step(DummyStep("step2"))
      4. result = pipeline.execute(np.zeros((10, 10)), {})
    Expected Result: 
      - metadata["execution_order"] == ["step1", "step2"]
      - result is numpy array
    Evidence: pytest output

  Scenario: Error in step is caught and logged
    Tool: Bash (pytest)
    Preconditions: FailingStep that raises Exception
    Steps:
      1. pipeline = ImagePipeline()
      2. pipeline.add_step(FailingStep())
      3. result = pipeline.execute(test_image, {})
    Expected Result: 
      - No exception raised
      - Result equals input (error step skipped)
      - Error logged
    Evidence: pytest output + caplog
  ```

  **Commit:** YES
  - Message: `feat(core): add ImagePipeline executor`
  - Files: `src/core/pipeline.py`, `tests/core/test_pipeline.py`

- [ ] **1.3. Implement GrayscaleStep**

  **What to do:**
  Port GrayscaleStep from `shell/core/steps.py:68-77`
  - Convert BGR to grayscale using OpenCV
  - Handle already-grayscale input (pass-through)

  **Files to modify:**
  - Create: `src/core/steps/__init__.py`
  - Create: `src/core/steps/grayscale_step.py`

  **Must NOT do:**
  - No parameter definitions (this step has no params)

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES (with 1.4, 1.5, 1.6)
  - **Blocks:** None
  - **Blocked By:** 1.1 (needs PipelineStep)

  **References:**
  - Pattern: `shell/core/steps.py:68-77` - GrayscaleStep
  - API: `cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)`

  **Acceptance Criteria:**
  - `pytest src/core/steps/test_grayscale_step.py` passes:
    - BGR input → grayscale output
    - Grayscale input → unchanged
    - Correct shape (H, W) not (H, W, 1)

  **QA Scenarios:**
  ```
  Scenario: Convert color image to grayscale
    Tool: Bash (pytest)
    Preconditions: test_color_image (100, 100, 3) uint8
    Steps:
      1. step = GrayscaleStep()
      2. result = step.process(test_color_image, {})
    Expected Result: 
      - result.shape == (100, 100)
      - result.dtype == np.uint8
    Evidence: pytest output

  Scenario: Pass through already grayscale
    Tool: Bash (pytest)
    Preconditions: test_gray_image (100, 100) uint8
    Steps:
      1. step = GrayscaleStep()
      2. result = step.process(test_gray_image, {})
    Expected Result: result is identical to input
    Evidence: np.array_equal check
  ```

  **Commit:** YES (group with 1.4, 1.5, 1.6)

- [ ] **1.4. Implement GaussianBlurStep**

  **What to do:**
  Port GaussianBlurStep from `shell/core/steps.py:79-94`
  - Parameters: kernel_size (int, 5), sigma (float, 0)
  - Ensure kernel_size is odd

  **Files to modify:**
  - Create: `src/core/steps/gaussian_blur_step.py`

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES
  - **Blocks:** None
  - **Blocked By:** 1.1

  **References:**
  - Pattern: `shell/core/steps.py:79-94`
  - API: `cv2.GaussianBlur(image, (k, k), sigma)`

  **Acceptance Criteria:**
  - Tests pass for various kernel sizes
  - Test kernel_size auto-adjusts to odd
  - Test sigma=0 uses auto-calculation

  **QA Scenarios:**
  ```
  Scenario: Blur with default parameters
    Tool: Bash (pytest)
    Preconditions: test_image 100x100
    Steps:
      1. step = GaussianBlurStep()
      2. result = step.process(test_image, {})
    Expected Result: 
      - result is blurred (lower variance than input)
      - shape unchanged
    Evidence: variance comparison

  Scenario: Even kernel_size adjusted to odd
    Tool: Bash (pytest)
    Preconditions: None
    Steps:
      1. step = GaussianBlurStep()
      2. step.set_param("kernel_size", 4)
      3. result = step.process(test_image, {})
    Expected Result: No error (internally uses 5x5)
    Evidence: pytest passes
  ```

  **Commit:** YES (group with 1.3, 1.5, 1.6)

- [ ] **1.5. Implement ClaheStep**

  **What to do:**
  Port ClaheStep from `shell/core/steps.py:97-119`
  - Parameters: clip_limit (float, 2.0), tile_grid_size (int, 8)
  - Auto-convert to grayscale if needed
  - Use cv2.createCLAHE

  **Files to modify:**
  - Create: `src/core/steps/clahe_step.py`

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES
  - **Blocks:** None
  - **Blocked By:** 1.1

  **References:**
  - Pattern: `shell/core/steps.py:97-119`
  - API: `cv2.createCLAHE(clipLimit, tileGridSize)`

  **Acceptance Criteria:**
  - Tests pass for CLAHE enhancement
  - Test contrast is increased (higher variance)
  - Test handles both color and grayscale input

  **QA Scenarios:**
  ```
  Scenario: CLAHE enhances contrast
    Tool: Bash (pytest)
    Preconditions: low_contrast_image
    Steps:
      1. step = ClaheStep(clip_limit=3.0, tile_grid_size=8)
      2. result = step.process(low_contrast_image, {})
    Expected Result: result.std() > input.std()
    Evidence: std comparison in test
  ```

  **Commit:** YES (group with 1.3, 1.4, 1.6)

- [ ] **1.6. Implement PhantastStep**

  **What to do:**
  Port PhantastStep from `shell/core/steps.py:122-204`
  - Parameters: sigma (float, 4.0), epsilon (float, 0.05)
  - Integrates with `phantast_confluency_corrected.process_phantast`
  - Creates green overlay on detected cells
  - Stores confluency % and mask in metadata

  **Files to modify:**
  - Create: `src/core/steps/phantast_step.py`

  **Must NOT do:**
  - Don't fail if phantast module not available (graceful degradation)

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES
  - **Blocks:** None (critical feature)
  - **Blocked By:** 1.1

  **References:**
  - Pattern: `shell/core/steps.py:122-204` - PhantastStep
  - External: `phantast_confluency_corrected.process_phantast`

  **Acceptance Criteria:**
  - Tests pass (mock phantast if unavailable)
  - Test overlay created correctly
  - Test metadata populated (confluency, mask)

  **QA Scenarios:**
  ```
  Scenario: PHANTAST detects cells and creates overlay
    Tool: Bash (pytest with mock)
    Preconditions: mock_phantast returns (85.5, mask_array)
    Steps:
      1. step = PhantastStep(sigma=4.0, epsilon=0.05)
      2. result = step.process(test_image, metadata)
    Expected Result:
      - metadata["phantast_confluency"] == 85.5
      - metadata["phantast_mask"] is boolean array
      - result has green overlay on masked areas
    Evidence: visual test or array comparison

  Scenario: Graceful when phantast unavailable
    Tool: Bash (pytest)
    Preconditions: ImportError simulated
    Steps:
      1. step = PhantastStep()
      2. result = step.process(test_image, {})
    Expected Result: result equals input (pass-through)
    Evidence: array equality check
  ```

  **Commit:** YES (group with 1.3, 1.4, 1.5)
  - Message: `feat(core): add all pipeline step implementations`
  - Files: `src/core/steps/*.py`, `tests/core/steps/*.py`

#### Stream B: Models

- [ ] **1.7. Enhance ImageSessionModel with Metadata**

  **What to do:**
  Extend `src/models/image_model.py` ImageSessionModel:
  - Add image metadata (dimensions, bit_depth, channels from cv2)
  - Add processing results (confluency, mask path, processed image path)
  - Add status tracking (raw, processing, processed, error)
  - File format helper methods

  **Files to modify:**
  - Edit: `src/models/image_model.py`

  **Must NOT do:**
  - No Qt imports (keep pure Python)

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES (with 1.1, 1.2)
  - **Blocks:** 1.8 (persistence needs this), 2.9 (controller needs this)
  - **Blocked By:** None

  **References:**
  - Current: `src/models/image_model.py` - base implementation
  - Pattern: `shell/sections/image_navigation_inspection/views/image_navigation.py:193-206` - metadata usage

  **Acceptance Criteria:**
  - `pytest src/models/test_image_model.py` passes:
    - Test metadata extraction (use cv2.imread for dimensions)
    - Test processing result storage
    - Test status transitions

  **QA Scenarios:**
  ```
  Scenario: Extract image metadata on load
    Tool: Bash (pytest)
    Preconditions: test_image_512x512_8bit.png exists
    Steps:
      1. model = ImageSessionModel()
      2. model.set_single_image("test_image.png")
    Expected Result:
      - model.active_image["dimensions"] == "512 x 512"
      - model.active_image["bit_depth"] == "8-bit"
      - model.active_image["channels"] == "3 (RGB)"
    Evidence: pytest assertions

  Scenario: Store processing results
    Tool: Bash (pytest)
    Preconditions: Active image loaded
    Steps:
      1. model.set_processing_result(confluency=85.5, mask_path="mask.png")
    Expected Result:
      - model.active_image["confluencyResult"]["percentage"] == 85.5
      - model.status == "processed"
    Evidence: attribute checks
  ```

  **Commit:** YES
  - Message: `feat(models): enhance ImageSessionModel with metadata`
  - Files: `src/models/image_model.py`, `tests/models/test_image_model.py`

- [ ] **1.8. Implement Pipeline Model Persistence**

  **What to do:**
  Extend `src/models/pipeline_model.py`:
  - Add serialization (to_dict, from_dict)
  - Add JSON save/load
  - Add validation (step types exist, parameters valid)

  **Files to modify:**
  - Edit: `src/models/pipeline_model.py`

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES (with 1.7)
  - **Blocks:** 3.11 (batch needs persistence)
  - **Blocked By:** 1.7 (for consistency)

  **References:**
  - Current: `src/models/pipeline_model.py` - dataclasses only

  **Acceptance Criteria:**
  - `pytest src/models/test_pipeline_model.py` passes:
    - Test save/load roundtrip
    - Test invalid step type rejected
    - Test parameter validation

  **QA Scenarios:**
  ```
  Scenario: Save and load pipeline
    Tool: Bash (pytest)
    Preconditions: Pipeline with 2 steps
    Steps:
      1. pipeline = Pipeline(name="Test", nodes=[...])
      2. pipeline.save("test_pipeline.json")
      3. loaded = Pipeline.load("test_pipeline.json")
    Expected Result: loaded == pipeline (all fields match)
    Evidence: dataclass comparison
  ```

  **Commit:** YES
  - Message: `feat(models): add pipeline persistence`
  - Files: `src/models/pipeline_model.py`, `tests/models/test_pipeline_model.py`

- [ ] **1.9. Create Test Fixtures**

  **What to do:**
  Create reusable test data:
  - `conftest.py` with fixtures for:
    - Test images (color, grayscale, various sizes)
    - Sample pipeline configurations
    - Mock Qt widgets (qtbot integration)

  **Files to modify:**
  - Create: `tests/conftest.py`
  - Create: `tests/fixtures/images/` (test images)

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES
  - **Blocks:** All test files
  - **Blocked By:** None

  **Acceptance Criteria:**
  - `pytest tests/conftest_test.py` (sanity check fixtures work)

  **QA Scenarios:**
  ```
  Scenario: Fixtures load correctly
    Tool: Bash (pytest)
    Steps:
      1. Use fixture: test_image_color
      2. Use fixture: sample_pipeline
    Expected Result: Both fixtures return valid objects
    Evidence: pytest setup passes
  ```

  **Commit:** YES
  - Message: `test: add shared fixtures`
  - Files: `tests/conftest.py`, `tests/fixtures/**/*`

#### Stream C: Test Infrastructure

- [ ] **1.10. Configure pytest with pytest-qt**

  **What to do:**
  - Create `pytest.ini` or `pyproject.toml` config
  - Configure test discovery, markers
  - Set up pytest-qt for GUI testing

  **Files to modify:**
  - Create: `pytest.ini`
  - Create: `pyproject.toml` (if not exists)

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES
  - **Blocks:** All testing
  - **Blocked By:** None

  **References:**
  - pytest-qt docs for qtbot configuration

  **Acceptance Criteria:**
  - `pytest --collect-only` lists all tests
  - `pytest -v` runs without errors

  **QA Scenarios:**
  ```
  Scenario: Pytest configuration works
    Tool: Bash
    Steps:
      1. Run: pytest --version
      2. Run: pytest tests/ -v --co
    Expected Result: No errors, tests collected
    Evidence: terminal output
  ```

  **Commit:** YES
  - Message: `chore: configure pytest with pytest-qt`
  - Files: `pytest.ini`, `pyproject.toml`

- [ ] **1.11. Create qtbot Fixtures for Widget Testing**

  **What to do:**
  - Create fixtures for common widget setups
  - Helper for widget cleanup (qtbot.addWidget)
  - Mock QMessageBox/QFileDialog patterns

  **Files to modify:**
  - Edit: `tests/conftest.py` (add qtbot fixtures)

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES
  - **Blocks:** GUI tests
  - **Blocked By:** 1.10

  **Acceptance Criteria:**
  - Example widget test passes using fixtures

  **QA Scenarios:**
  ```
  Scenario: qtbot fixture works
    Tool: Bash (pytest)
    Steps:
      1. Test uses qtbot fixture
      2. Creates QWidget
      3. qtbot.addWidget(widget)
    Expected Result: Test passes, no leaks
    Evidence: pytest output
  ```

  **Commit:** YES (group with 1.10)

- [ ] **1.12. Set Up CI Workflow**

  **What to do:**
  Create `.github/workflows/test.yml`:
  - Run on push/PR
  - Set up Python, install dependencies
  - Run pytest with coverage
  - Upload coverage report

  **Files to modify:**
  - Create: `.github/workflows/test.yml`

  **Recommended Agent Profile:**
  - **Category:** `quick`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES
  - **Blocks:** None
  - **Blocked By:** 1.10 (needs test config)

  **Acceptance Criteria:**
  - CI passes on this branch
  - Coverage report generated

  **QA Scenarios:**
  ```
  Scenario: CI workflow runs
    Tool: GitHub Actions
    Steps:
      1. Push to branch
      2. Wait for CI
    Expected Result: All checks green
    Evidence: GitHub UI
  ```

  **Commit:** YES
  - Message: `ci: add test workflow`
  - Files: `.github/workflows/test.yml`

#### Stream D: Shell

- [ ] **1.13. Create MainWindow Skeleton**

  **What to do:**
  Create `src/ui/main_window.py` with:
  - Basic QMainWindow structure
  - Header with logo/title
  - Placeholder for content area
  - Dark theme stylesheet (#121415, #00B884)

  **Files to modify:**
  - Edit: `src/ui/main_window.py` (exists, may be skeletal)

  **Recommended Agent Profile:**
  - **Category:** `visual-engineering`
  - **Skills:** []

  **Parallelization:**
  - **Can Run In Parallel:** YES
  - **Blocks:** 4.1 (navigation needs this)
  - **Blocked By:** None

  **References:**
  - Pattern: `shell/shell/main_window.py:16-73` - structure
  - Pattern: `src/ui/main_window.py` - current state

  **Acceptance Criteria:**
  - Application launches and shows window
  - Dark theme applied
  - Header visible with logo

  **QA Scenarios:**
  ```
  Scenario: MainWindow launches
    Tool: Bash
    Steps:
      1. Run: python -m src.main
    Expected Result: Window appears, no errors
    Evidence: Screenshot or success exit code
  ```

  **Commit:** YES
  - Message: `feat(ui): create MainWindow skeleton`
  - Files: `src/ui/main_window.py`

---

## Success Criteria

### Final Deliverables Checklist

- [ ] All 4 pipeline steps working (Grayscale, GaussianBlur, CLAHE, PHANTAST)
- [ ] Image navigation with folder browsing
- [ ] Image canvas with zoom/pan/tools
- [ ] Properties panel showing metadata
- [ ] Pipeline editor with step configuration
- [ ] Batch execution with queue
- [ ] Test coverage ≥70%
- [ ] CI/CD passing
- [ ] Documentation complete

### Performance Targets

- Image loading: <100ms for 4K images
- Pipeline execution: <2s for typical image (CLAHE + PHANTAST)
- UI response: 60fps during interactions

### Quality Gates

- No PyQt in model tests
- No blocking operations in UI thread
- All signals/slots type-safe
- No memory leaks (valgrind or similar)

---

## Commit Strategy

**Phase 1:** Individual commits per task (foundation is critical)
**Phase 2-4:** Group related tasks (UI components, features)
**Final:** Squash fixups, tag release

**Commit Message Format:**
```
<type>(<scope>): <description>

[body if needed]
```

Types: feat, fix, test, docs, refactor, chore, ci

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PHANTAST integration issues | Medium | High | Mock for tests, graceful degradation |
| Qt threading complexity | Medium | Medium | Strict MVC, review all threading code |
| Test coverage gaps | High | Medium | Enforce 70% in CI, pair reviews |
| Scope creep | Medium | High | Strict phase gates, feature freeze dates |

---

## Appendix: File Structure Target

```
src/
├── main.py                     # Entry point
├── core/                       # Processing framework
│   ├── __init__.py
│   ├── pipeline_step.py        # ABC + StepParameter
│   ├── pipeline.py             # ImagePipeline executor
│   └── steps/                  # Step implementations
│       ├── __init__.py
│       ├── grayscale_step.py
│       ├── gaussian_blur_step.py
│       ├── clahe_step.py
│       └── phantast_step.py
├── models/                     # Data layer
│   ├── __init__.py
│   ├── image_model.py          # ImageSessionModel
│   └── pipeline_model.py       # Pipeline persistence
├── controllers/                # Glue layer
│   ├── __init__.py
│   ├── image_controller.py     # ImageSessionModel ↔ UI
│   └── pipeline_controller.py  # Pipeline ↔ UI
└── ui/                         # View layer
    ├── __init__.py
    ├── main_window.py          # QMainWindow shell
    ├── navigation.py           # Navigation components
    ├── image_navigation.py     # Left panel (folder, thumbnails)
    ├── image_canvas.py         # Central canvas (zoom, pan)
    ├── pipeline_view.py        # Pipeline visualization
    └── batch_execution_view.py # Batch processing UI

tests/
├── conftest.py                 # Shared fixtures
├── fixtures/                   # Test data
│   └── images/
├── core/                       # Core tests
│   ├── test_pipeline_step.py
│   ├── test_pipeline.py
│   └── steps/
├── models/                     # Model tests
│   ├── test_image_model.py
│   └── test_pipeline_model.py
├── controllers/                # Controller tests
└── ui/                         # GUI tests (pytest-qt)
```

---

**Plan Generated:** 2026-03-04
**Next Step:** Run `/start-work` to begin execution
