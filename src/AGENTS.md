# src/ AGENTS.md

**Scope:** Main PhantastLab application - MVC architecture.

## STRUCTURE
```
src/
├── main.py                 # Entry point (QApplication setup)
├── ui/
│   ├── main_window.py      # Dark-themed main window
│   ├── image_navigation.py # Left panel navigation
│   ├── image_canvas.py     # Image display with overlay
│   └── pipeline_view.py    # Pipeline configuration UI
├── models/
│   ├── image_model.py      # ImageSession, metadata
│   └── pipeline_model.py   # Pipeline persistence
└── controllers/
    ├── image_controller.py # Binds ImageNavigation to model
    └── pipeline_controller.py
```

## CONVENTIONS

### MVC Separation
- **models/**: Pure Python, no PyQt imports except signals
- **ui/**: QWidget subclasses, display/input only, no logic
- **controllers/**: Glues models ↔ UI via signals

### Imports
```python
from PyQt6.QtWidgets import *
from src.models.image_model import ImageSession  # Never import ui from models
```

### Widget Patterns
- Theme: #121415 bg, #00B884 accent, Inter font
- Layouts: Always use (HBox, VBox, Grid) - no absolute positioning
- Memory: Assign `parent=` or store in `self.`

## ANTI-PATTERNS
- **NEVER** put image processing logic in ui/ files
- **NEVER** access UI directly from models
- **NEVER** block main thread (>100ms ops → thread pool)
