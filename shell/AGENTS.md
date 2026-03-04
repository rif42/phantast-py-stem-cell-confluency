# shell/ AGENTS.md

**Scope:** Prototype/reference PyQt6 app with pipeline framework.

## STRUCTURE
```
shell/
├── shell/
│   ├── main_window.py     # QStackedWidget navigation
│   └── navigation.py      # Nav button handling
├── sections/
│   ├── image_navigation_inspection/  # Image browser + tools
│   ├── pipeline_construction/        # Pipeline builder UI
│   └── batch_execution_output/       # Batch processing
├── core/
│   ├── pipeline.py        # ImagePipeline executor
│   └── steps.py           # Built-in PipelineStep classes
└── gui/
    ├── simple_app.py      # Standalone demo app
    ├── pipeline_editor.py # Visual step editor
    └── image_viewer.py    # Basic image display
```

## CONCEPTS

### Pipeline Framework
```python
from shell.core.pipeline import ImagePipeline, PipelineStep

class CLAHEStep(PipelineStep):
    def __init__(self, clip_limit=2.0):
        self.clip_limit = clip_limit
    
    def process(self, image: np.ndarray, metadata: dict) -> np.ndarray:
        # Process image, return result
        return enhanced_image
    
    def get_parameters(self) -> dict:
        return {"clip_limit": self.clip_limit}

# Usage
pipeline = ImagePipeline()
pipeline.add_step(CLAHEStep(clip_limit=3.0))
result = pipeline.execute(image_array)
```

### Navigation Pattern
Uses QStackedWidget for section switching:
```python
self.stack = QStackedWidget()
self.stack.addWidget(image_nav_view)    # Index 0
self.stack.addWidget(pipeline_view)     # Index 1
self.stack.add_widget(batch_view)       # Index 2
```

### Import Style
```python
# shell imports its own sections from src.sections
from shell.sections.image_navigation_inspection.views.image_navigation import ImageNavigationWidget
```

## CONVENTIONS
- Same dark theme as src/ (#121415, #00B884)
- QStackedWidget for section navigation
- Steps must inherit PipelineStep, implement process()

## ANTI-PATTERNS
- **NEVER** mix shell/ and src/ imports - they're separate apps
- **NEVER** put pipeline logic in gui/ - belongs in core/
