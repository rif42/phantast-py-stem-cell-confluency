# Report Header Band on Output Images

## TL;DR

> **Quick Summary**: Add a black header band (80px) to the top of processed binary mask images showing confluency %, parameters (sigma/epsilon), title "Stem Cell Confluency Detector", and a per-image UUID.
> 
> **Deliverables**:
> - Modified `phantast_step.py` that communicates metadata via mutable dict
> - New `create_report_header()` function in `pipeline_worker.py`
> - Integrated header rendering in the pipeline save flow
> - Working output images with header band
> 
> **Estimated Effort**: Short
> **Parallel Execution**: NO — sequential (3 tasks, each depends on previous)
> **Critical Path**: Task 1 → Task 2 → Task 3

---

## Context

### Original Request
User wants an extra black space at the top of the output image (binary mask) with:
- **Top left**: "Stem Cell Confluency Detector" (big bold)
- **Below left**: Randomized UUID (small font, per image)
- **Top right**: "Confluency: xx%" (big bold)
- **Below right**: sigma and epsilon parameters (small font)

### Interview Summary
**Key Decisions**:
- UUID: Per image (unique per execution)
- Background: Black
- Target: On the binary mask output (not a separate file)
- Header is NOT added to the `_mask.png` green overlay

### Metis Review
**Critical Finding**: Function attribute storage (`process._last_report = ...`) is NOT thread-safe. PipelineWorker runs in QThread, concurrent batch items could clobber metadata.

**Resolution**: Use mutable dict parameter `_metadata={}` passed to `step.process()`. Steps that don't support it ignore it via `**kwargs` or default `None`.

**Other Gaps Addressed**:
- Header height: 80px (hardcoded)
- Minimum image width: 400px (skip header if narrower)
- Confluency format: 1 decimal place ("42.5%")
- Params format: "σ=8.00, ε=0.05"
- UUID format: First 8 chars of uuid4 ("a1b2c3d4")
- Text color: White for big text, gray (180) for small text

---

## Work Objectives

### Core Objective
Add a 80px black header band to processed output images containing confluency %, parameters, title, and UUID.

### Concrete Deliverables
- `src/core/steps/phantast_step.py` — modified `process()` to populate metadata dict
- `src/core/pipeline_worker.py` — new `create_report_header()` + integration in save flow

### Definition of Done
- [ ] Running pipeline with phantast step produces output image with 80px header
- [ ] Header contains correct confluency %, sigma, epsilon, title, UUID
- [ ] Images < 400px wide skip header gracefully (no crash)
- [ ] Non-phantast pipelines produce normal output (no header)

### Must Have
- Header band on all phantast-processed output images
- Thread-safe metadata passing (mutable dict, not function attributes)
- UUID unique per image execution
- Confluency with 1 decimal place

### Must NOT Have (Guardrails)
- ❌ Header on the `_mask.png` green overlay file
- ❌ Configuration UI for header (no toggle, no customization)
- ❌ Function attribute storage for metadata (thread-unsafe)
- ❌ TTF/custom font loading (OpenCV built-in only)
- ❌ Multi-line text wrapping
- ❌ Header on non-phantast pipelines
- ❌ Any changes to the green mask overlay image

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest, pytest-qt, pytest-mock)
- **Automated tests**: YES (Tests-after)
- **Framework**: pytest

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Library/Module**: Use Bash (python REPL) — Import, call functions, compare output

---

## Execution Strategy

### Sequential Execution (3 tasks)

```
Task 1: Modify phantast_step.py — capture metadata via mutable dict [quick]
  ↓
Task 2: Add create_report_header() + integrate in pipeline_worker.py [unspecified-high]
  ↓
Task 3: Verify with test image run [quick]
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 2, 3 | 1 |
| 2 | 1 | 3 | 2 |
| 3 | 2 | FINAL | 3 |

### Agent Dispatch Summary

- **Wave 1**: T1 → `quick`
- **Wave 2**: T2 → `unspecified-high` (computer-vision-opencv skill for OpenCV text rendering)
- **Wave 3**: T3 → `quick`

---

## TODOs

- [x] 1. Modify phantast_step.py to capture confluency metadata

  **What to do**:
  - Add `import uuid` at top of `phantast_step.py`
  - Modify `process()` signature to accept `_metadata=None` as first positional arg after `image`
  - Inside `process()`: capture `confluency` from `process_phantast()` return (currently discarded as `_`)
  - If `_metadata is not None`: populate it with `{confluency, sigma, epsilon, uuid: str(uuid.uuid4())[:8]}`
  - The `_metadata` dict is passed by reference from pipeline_worker, so no function attributes needed
  - **Important**: `_metadata` must be a kwarg with default None so existing callers aren't broken

  **Must NOT do**:
  - Do NOT use function attributes (`process._last_report`) — thread-unsafe
  - Do NOT change the return type of `process()` — must still return `np.ndarray`
  - Do NOT modify `process_phantast()` — it already returns `(confluency, mask)` correctly
  - Do NOT change any other step files

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single function modification, well-defined scope
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `computer-vision-opencv`: Not needed — no OpenCV API changes, just Python logic

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 (alone)
  - **Blocks**: Tasks 2, 3
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - `src/core/steps/phantast_step.py:402-428` — Current `process()` function that discards confluency. The `_` in `_, mask = process_phantast(...)` on line 415 is the discarded confluency value. Change `_` to `confluency`.
  - `src/core/steps/phantast_step.py:351-399` — `process_phantast()` already returns `tuple[float, np.ndarray]` — `(confluency, mask)`. No changes needed here.

  **API/Type References**:
  - `src/core/steps/__init__.py:73-148` — `register_step` decorator. Note that the decorated function is stored in `StepMetadata.process`. The `_metadata` parameter must have default None to not break the step registry's type contract.

  **WHY Each Reference Matters**:
  - `phantast_step.py:415` — This is THE line that discards confluency. The `_` variable must become `confluency` and be stored in `_metadata` dict.
  - `__init__.py:53` — `StepMetadata.process` is typed as `Callable[..., np.ndarray]`. Adding an optional `_metadata=None` kwarg is compatible with `...` in the Callable type.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Metadata is populated when _metadata dict provided
    Tool: Bash (python)
    Preconditions: In project root with src/ on PYTHONPATH
    Steps:
      1. Run: python -c "import sys; sys.path.insert(0,'src'); from core.steps.phantast_step import process; import numpy as np; img = np.random.randint(0,255,(100,100),dtype=np.uint8); meta = {}; result = process(img, _metadata=meta, sigma=8.0, epsilon=0.05); print('confluency' in meta, 'sigma' in meta, 'epsilon' in meta, 'uuid' in meta, result.shape)"
      2. Assert output contains "True True True True (100, 100)"
    Expected Result: All metadata keys present, result shape unchanged
    Failure Indicators: Missing keys, shape changed, or ImportError
    Evidence: .sisyphus/evidence/task-1-metadata-populated.txt

  Scenario: Metadata is None-safe (no _metadata passed)
    Tool: Bash (python)
    Preconditions: In project root
    Steps:
      1. Run: python -c "import sys; sys.path.insert(0,'src'); from core.steps.phantast_step import process; import numpy as np; img = np.random.randint(0,255,(100,100),dtype=np.uint8); result = process(img); print(result.shape, result.dtype)"
      2. Assert output contains "(100, 100) uint8"
    Expected Result: Works identically to before — no crash, same return type
    Failure Indicators: TypeError about _metadata, or different shape/dtype
    Evidence: .sisyphus/evidence/task-1-metadata-none-safe.txt

  Scenario: UUID is unique across consecutive calls
    Tool: Bash (python)
    Preconditions: In project root
    Steps:
      1. Run: python -c "import sys; sys.path.insert(0,'src'); from core.steps.phantast_step import process; import numpy as np; img = np.random.randint(0,255,(100,100),dtype=np.uint8); uuids = set(); [uuids.add(process(img, _metadata:={}) or _metadata.get('uuid','')) for _ in range(10)]; print(f'Unique UUIDs: {len(uuids)}/10')"
      2. Assert output shows "Unique UUIDs: 10/10"
    Expected Result: All 10 UUIDs are different
    Failure Indicators: Any duplicate UUIDs
    Evidence: .sisyphus/evidence/task-1-uuid-unique.txt
  ```

  **Commit**: YES
  - Message: `feat(phantast): capture confluency metadata for report header`
  - Files: `src/core/steps/phantast_step.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0,'src'); from core.steps.phantast_step import process; import numpy as np; process(np.zeros((50,50),dtype=np.uint8))"`

- [x] 2. Add report header rendering and integrate into pipeline_worker

  **What to do**:
  - In `src/core/pipeline_worker.py`:
    1. Add `import uuid` at top
    2. Add `create_report_header(image, metadata)` function:
       - Create 80px tall black band: `np.zeros((80, width, 3), dtype=np.uint8)`
       - Draw text using `cv2.putText()`:
         - Left side (x=20):
           - y=30: "Stem Cell Confluency Detector" — font: `FONT_HERSHEY_SIMPLEX`, scale=0.7, thickness=2, color=(255,255,255)
           - y=58: f"ID: {metadata['uuid']}" — scale=0.45, thickness=1, color=(180,180,180)
         - Right side (right-aligned using `cv2.getTextSize()`):
           - y=30: f"Confluency: {metadata['confluency']:.1f}%" — scale=0.7, thickness=2, color=(255,255,255)
           - y=58: f"\u03c3={metadata['sigma']:.2f}, \u03b5={metadata['epsilon']:.2f}" — scale=0.45, thickness=1, color=(180,180,180)
       - Vertically stack header on top of image: `np.vstack([header, image])`
       - Return the combined image
    3. Modify `process_pipeline()`:
       - Before the step loop: create `report_metadata = {}`
       - In the step loop at line 83: pass `_metadata=report_metadata` to step.process() — but only for steps that accept it. Use try/except TypeError or check if `_metadata` is in the step's signature.
       - **Better approach**: Always pass `_metadata=report_metadata` as kwarg. Since `_metadata` defaults to `None` in phantast_step, non-phantast steps will receive it as an unexpected kwarg. To handle this, catch `TypeError` or use `inspect.signature` to check. Simplest: wrap in try/except TypeError and retry without `_metadata`.
       - After `_prepare_for_save()`, before `cv2.imwrite()`: if `report_metadata` is non-empty, call `create_report_header(output_image, report_metadata)` and use result for saving.

  **Must NOT do**:
  - Do NOT modify the `_mask.png` overlay — only the main output image gets the header
  - Do NOT add header to images < 400px wide (skip gracefully)
  - Do NOT change `_prepare_for_save()` function
  - Do NOT change signal emissions or thread management

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: OpenCV text rendering requires careful positioning, threading awareness, and integration into existing pipeline flow
  - **Skills**: [`computer-vision-opencv`]
    - `computer-vision-opencv`: OpenCV text rendering (cv2.putText, cv2.getTextSize), numpy array manipulation (np.vstack, np.zeros)
  - **Skills Evaluated but Omitted**:
    - `numpy-best-practices`: The numpy operations are trivial (zeros, vstack) — no performance concerns
    - `scikit-image`: Not needed — no scikit-image operations

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (alone)
  - **Blocks**: Task 3
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - `src/core/pipeline_worker.py:43-117` — Full `process_pipeline()` method. The step loop is lines 72-109. The save happens at lines 111-115. Report header must be inserted between `_prepare_for_save()` (line 111) and `cv2.imwrite()` (line 112).
  - `src/core/pipeline_worker.py:145-168` — `_prepare_for_save()` converts image to 3-channel BGR uint8. After this function, the image is always `ndim==3, shape[2]==3, dtype==uint8`. This is the format `create_report_header()` will receive.

  **API/Type References**:
  - `src/core/pipeline_worker.py:39-41` — Signal definitions: `mask_saved = pyqtSignal(str, str)` and `finished = pyqtSignal(str)`. Do NOT change these.
  - `src/core/pipeline_worker.py:25-30` — `create_green_mask_overlay()` — example of numpy array manipulation in this file. Follow similar patterns.

  **External References**:
  - OpenCV docs: `cv2.putText()` — https://docs.opencv.org/4.x/d6/d6e/group__imgproc__draw.html#ga5126c47988102cf465cc5e0dd5c734e1
  - OpenCV docs: `cv2.getTextSize()` — https://docs.opencv.org/4.x/d6/d6e/group__imgproc__draw.html#ga3d2abf8e2b4daaab25a41b5f6f0b7b3e
  - OpenCV fonts: `cv2.FONT_HERSHEY_SIMPLEX` — clean sans-serif, `FONT_HERSHEY_BOLD` does NOT exist (use thickness for bold)

  **WHY Each Reference Matters**:
  - `pipeline_worker.py:111-115` — This is the insertion point. `_prepare_for_save()` normalizes the image to BGR uint8, then `cv2.imwrite()` saves. Header must go between these.
  - `pipeline_worker.py:25-30` — Shows the numpy pattern used in this file. Follow it for `create_report_header()`.
  - OpenCV has no `FONT_HERSHEY_BOLD` — "bold" is achieved via `thickness=2` or `thickness=3`.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: Header band added to output image
    Tool: Bash (python)
    Preconditions: Task 1 complete, in project root
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0,'src')
from core.pipeline_worker import PipelineWorker
from core.steps import STEP_REGISTRY
import numpy as np
import tempfile, os

# Create test image (800x600)
img = np.random.randint(0,255,(600,800), dtype=np.uint8)
input_path = os.path.join(tempfile.gettempdir(), 'test_input.png')
cv2 imwrite test image
import cv2; cv2.imwrite(input_path, img)

# Run through pipeline_worker's create_report_header directly
from core.pipeline_worker import create_report_header if exists
# Actually test via full pipeline:
worker = PipelineWorker()
metadata = {'confluency': 42.5, 'sigma': 8.0, 'epsilon': 0.05, 'uuid': 'a1b2c3d4'}
# Test the function if it's importable, or test via end-to-end
print('Test approach: verify function exists and produces correct dimensions')
"
      2. Verify the function exists and is importable
    Expected Result: create_report_header function importable from pipeline_worker module
    Failure Indicators: ImportError or function not found
    Evidence: .sisyphus/evidence/task-2-header-function.txt

  Scenario: Header dimensions correct (80px added)
    Tool: Bash (python)
    Preconditions: Task 1+2 complete
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0,'src')
import numpy as np
from core.pipeline_worker import create_report_header

# Create a 3-channel test image (600x800 BGR)
test_img = np.zeros((600, 800, 3), dtype=np.uint8)
metadata = {'confluency': 42.5, 'sigma': 8.0, 'epsilon': 0.05, 'uuid': 'a1b2c3d4'}
result = create_report_header(test_img, metadata)
print(f'Input: {test_img.shape}, Output: {result.shape}')
assert result.shape == (680, 800, 3), f'Expected (680, 800, 3), got {result.shape}'
assert result.dtype == np.uint8
print('PASS: Header band correctly added')
"
      2. Assert output shows "PASS: Header band correctly added"
    Expected Result: Output shape is (680, 800, 3) — original + 80px header
    Failure Indicators: Shape mismatch, wrong dtype, or crash
    Evidence: .sisyphus/evidence/task-2-header-dimensions.txt

  Scenario: Small image (< 400px) skips header gracefully
    Tool: Bash (python)
    Preconditions: Task 1+2 complete
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0,'src')
import numpy as np
from core.pipeline_worker import create_report_header

# Create a small 3-channel image (300x200)
small_img = np.zeros((200, 300, 3), dtype=np.uint8)
metadata = {'confluency': 42.5, 'sigma': 8.0, 'epsilon': 0.05, 'uuid': 'a1b2c3d4'}
result = create_report_header(small_img, metadata)
print(f'Small input: {small_img.shape}, Output: {result.shape}')
# Should either skip header (same size) or handle gracefully
assert result.shape[2] == 3  # Still 3-channel
print('PASS: Small image handled gracefully')
"
      2. Assert no crash, output is valid
    Expected Result: No crash. Image either unchanged or with header — either way, valid 3-channel BGR.
    Failure Indicators: Crash, wrong number of channels, assertion error
    Evidence: .sisyphus/evidence/task-2-small-image.txt

  Scenario: Header text is white on black background
    Tool: Bash (python)
    Preconditions: Task 1+2 complete
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0,'src')
import numpy as np
from core.pipeline_worker import create_report_header

test_img = np.zeros((600, 800, 3), dtype=np.uint8)
metadata = {'confluency': 42.5, 'sigma': 8.0, 'epsilon': 0.05, 'uuid': 'a1b2c3d4'}
result = create_report_header(test_img, metadata)

# Header region (top 80px) should not be all black — text pixels exist
header_region = result[:80, :, :]
has_white_pixels = np.any(header_region > 200)
print(f'Header has text pixels: {has_white_pixels}')
assert has_white_pixels, 'Header appears empty — no text rendered'
print('PASS: Text rendered in header')
"
      2. Assert header region contains non-black pixels (text was rendered)
    Expected Result: Header has white/gray pixels where text is drawn
    Failure Indicators: Header is all black (text not rendered)
    Evidence: .sisyphus/evidence/task-2-header-text.txt
  ```

  **Commit**: YES
  - Message: `feat(pipeline): add report header band to processed output images`
  - Files: `src/core/pipeline_worker.py`
  - Pre-commit: `python -c "import sys; sys.path.insert(0,'src'); from core.pipeline_worker import create_report_header"`

- [x] 3. End-to-end verification with real pipeline run

  **What to do**:
  - Run the actual application with a test image to verify header appears in output
  - Verify the confluency value in the header matches the printed "IMAGE CONFLUENCY" output
  - Verify UUID is present and unique
  - Verify sigma/epsilon match the pipeline parameters
  - Check that the `_mask.png` overlay file does NOT have a header
  - Remove debug print statements added during batch debugging (lines with `print(..., flush=True)`)

  **Must NOT do**:
  - Do NOT modify any source code (verification only)
  - Do NOT change test files

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Verification-only task, no code changes
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (alone)
  - **Blocks**: FINAL
  - **Blocked By**: Tasks 1, 2

  **References**:

  **Pattern References**:
  - `tests/test_phantast_step.py` — Shows how to create synthetic test images and verify phantast output patterns

  **WHY Each Reference Matters**:
  - Test patterns show how to verify phantast output without needing real microscopy images.

  **Acceptance Criteria**:

  **QA Scenarios (MANDATORY):**

  ```
  Scenario: End-to-end pipeline produces image with header
    Tool: Bash (python)
    Preconditions: Tasks 1+2 complete, in project root
    Steps:
      1. Run: python -c "
import sys; sys.path.insert(0,'src')
import numpy as np
import cv2
import tempfile, os

# Create synthetic test image
img = np.random.randint(50, 200, (400, 600), dtype=np.uint8)
input_path = os.path.join(tempfile.gettempdir(), 'test_header_input.png')
cv2.imwrite(input_path, img)

# Simulate the pipeline worker flow
from core.steps.phantast_step import process
from core.pipeline_worker import create_report_header, PipelineWorker

metadata = {}
mask = process(img, _metadata=metadata, sigma=8.0, epsilon=0.05)
print(f'Metadata: {metadata}')
print(f'Mask shape: {mask.shape}, dtype: {mask.dtype}')

# Simulate _prepare_for_save
worker = PipelineWorker()
output_image = worker._prepare_for_save(mask)
print(f'Prepared shape: {output_image.shape}')

# Add header
if metadata:
    final = create_report_header(output_image, metadata)
    print(f'Final shape: {final.shape}')
    assert final.shape[0] == output_image.shape[0] + 80, 'Header not 80px'
    assert final.shape[1] == output_image.shape[1], 'Width changed'
    
    # Save and verify
    out_path = os.path.join(tempfile.gettempdir(), 'test_header_output.png')
    cv2.imwrite(out_path, final)
    loaded = cv2.imread(out_path)
    print(f'Saved and loaded: {loaded.shape}')
    assert loaded.shape == final.shape, 'Saved image shape mismatch'
    print('PASS: End-to-end header rendering works')
"
      2. Assert output shows "PASS: End-to-end header rendering works"
    Expected Result: Full pipeline produces image with correct dimensions and metadata
    Failure Indicators: Shape mismatch, metadata empty, or crash
    Evidence: .sisyphus/evidence/task-3-e2e-header.txt

  Scenario: Verify mask overlay file unchanged
    Tool: Bash (python)
    Preconditions: Tasks 1+2 complete
    Steps:
      1. Run:python -c "
import sys; sys.path.insert(0,'src')
import numpy as np
from core.pipeline_worker import create_green_mask_overlay

# Verify create_green_mask_overlay still produces RGBA overlay without header
mask = np.zeros((100, 100), dtype=np.uint8)
mask[20:80, 20:80] = 255
overlay = create_green_mask_overlay(mask > 0)
assert overlay.shape == (100, 100, 4), f'Overlay shape wrong: {overlay.shape}'
assert overlay.dtype == np.uint8
print('PASS: Mask overlay unchanged — no header added')
"
      2. Assert overlay is still RGBA, same dimensions as input
    Expected Result: create_green_mask_overlay produces (100,100,4) RGBA — no header
    Failure Indicators: Shape mismatch, 3-channel instead of 4
    Evidence: .sisyphus/evidence/task-3-overlay-unchanged.txt
  ```

  **Commit**: YES
  - Message: `chore: remove debug prints from batch processing`
  - Files: `src/ui/main_window.py` (remove `print(..., flush=True)` lines)
  - Pre-commit: `python -c "import sys; sys.path.insert(0,'src'); from core.pipeline_worker import create_report_header; from core.steps.phantast_step import process"`

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `ruff check src/` + `ruff format src/ --check`. Review all changed files for: `as any` patterns, empty catches, console.log/print in prod (except phantast_step.py line 398 which is intentional), commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction.
  Output: `Lint [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test integration: run full pipeline on test image, verify output has header, verify mask overlay does not. Test edge cases: small image, missing metadata.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec. Check "Must NOT do" compliance. Detect cross-task contamination.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Task 1**: `feat(phantast): capture confluency metadata for report header` — `src/core/steps/phantast_step.py`
- **Task 2**: `feat(pipeline): add report header band to processed output images` — `src/core/pipeline_worker.py`
- **Task 3**: `chore: remove debug prints from batch processing` — `src/ui/main_window.py`

---

## Success Criteria

### Verification Commands
```bash
# 1. Metadata capture works
python -c "import sys; sys.path.insert(0,'src'); from core.steps.phantast_step import process; import numpy as np; m={}; process(np.zeros((50,50),dtype=np.uint8), _metadata=m); print(m)" 
# Expected: dict with confluency, sigma, epsilon, uuid keys

# 2. Header function produces correct dimensions
python -c "import sys; sys.path.insert(0,'src'); from core.pipeline_worker import create_report_header; import numpy as np; r=create_report_header(np.zeros((600,800,3),dtype=np.uint8),{'confluency':42.5,'sigma':8.0,'epsilon':0.05,'uuid':'abc12345'}); print(r.shape)"
# Expected: (680, 800, 3)

# 3. Lint passes
ruff check src/core/steps/phantast_step.py src/core/pipeline_worker.py
# Expected: No errors
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Output image has 80px header with correct text
- [ ] Mask overlay (_mask.png) is unchanged (no header)
- [ ] Thread-safe metadata passing (mutable dict, no function attributes)
