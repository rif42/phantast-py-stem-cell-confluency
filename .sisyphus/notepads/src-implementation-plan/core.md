# Core Framework Learnings

## Successful Patterns

### PipelineStep ABC
- Abstract base class with `process()` method works well
- StepParameter dataclass for UI metadata is clean
- `get_param()`/`set_param()` with defaults allows flexibility
- `enabled` property allows steps to be skipped without removal

### ImagePipeline
- Error handling with logging (not exceptions) keeps pipeline resilient
- Metadata dict passed between steps enables cross-step communication
- `move_step()` allows reordering without recreating steps

### Step Implementations
- All steps follow same pattern: `__init__` → `define_params()` → `process()`
- OpenCV integration is straightforward
- PHANTAST module available and working (green overlay applied correctly)

## Testing Insights

### Pure Python Testing
- Models tested without Qt imports - fast and reliable
- Test fixtures using `tempfile` work well for image operations
- OpenCV test images created programmatically

### Test Coverage
- 29 tests passing across core and models
- All pipeline operations tested
- All step implementations tested with real image processing

## Gotchas

### Type Hints
- `os.path.join()` requires non-None path - use local variable pattern:
  ```python
  folder = self.current_folder
  if folder is None:
      raise ValueError(...)
  os.path.join(folder, filename)
  ```

### PHANTAST Availability
- Module IS available in this environment
- Tests initially assumed unavailable (need to test actual behavior)
- Green overlay is applied to detected cells

## Architecture Validation

### MVC Separation
- Core framework has NO Qt dependencies ✓
- Models have NO Qt dependencies ✓
- Can run pipeline from CLI without GUI ✓

### Error Resilience
- Pipeline continues on step error ✓
- Errors logged properly ✓
- Graceful degradation when modules unavailable ✓
