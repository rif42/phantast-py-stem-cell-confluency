# PhantastLab AI Agent Guidelines

**Context:** PyQt6 desktop application for stem cell image processing and confluency detection.

## Project Overview

PhantastLab is a scientific image analysis tool for biologists working with stem cell microscopy. It provides:
- **Image Navigation & Inspection**: Browse directories, view images, adjust contrast (CLAHE)
- **Pipeline Construction**: Build and configure image processing pipelines
- **Batch Execution**: Process multiple images with automated analysis
- **Confluency Detection**: Automated stem cell confluency measurement using computer vision

**Core Stack:** PyQt6, OpenCV, NumPy, SciPy, scikit-image

---

## Architecture

### MVC/MVP Pattern (Strict Separation)

```
src/
├── main.py                    # Application entry point
├── models/                    # Pure Python data/logic (NO PyQt imports)
│   ├── image_model.py        # ImageSessionModel - manages image sessions
│   └── pipeline_model.py     # Pipeline configuration persistence
├── ui/                       # PyQt6 Widgets (View layer only)
│   ├── main_window.py        # QMainWindow with header + navigation
│   ├── image_navigation.py   # Left panel: file browser, thumbnails
│   ├── image_canvas.py       # Central image display with overlay
│   ├── pipeline_view.py      # Right panel: pipeline configuration
│   ├── batch_execution_view.py  # Batch processing UI
│   └── navigation.py         # Navigation widget components
└── controllers/              # Glue layer (models ↔ UI via signals)
    ├── image_controller.py   # Binds ImageNavigation to model
    └── pipeline_controller.py
```

**CLI Litmus Test:** All logic in `models/` must run in a CLI script without importing PyQt.

---

## Entry Points

| Entry Point | Purpose |
|-------------|---------|
| `src/main.py` | **Primary entry point** - launches the main application |
| `shell/shell/main_window.py` | Alternative shell-based launcher (legacy) |
| `CLAHE.py` | Standalone CLAHE processing script |
| `phantast_confluency_corrected.py` | Standalone confluency detection script |

---

## Where to Look

| Task | Location | Notes |
|------|----------|-------|
| Add new UI widget | `src/ui/` | Subclass QWidget, follow existing patterns |
| Add image processing logic | `src/models/` | Pure Python, testable without Qt |
| Connect UI to data | `src/controllers/` | One controller per major feature |
| Add processing step | `src/core/steps/` | Pipeline step implementations |
| UI styling/theme | `src/ui/main_window.py` | Global stylesheet in `apply_stylesheet()` |
| Build/package | `requirements_build.txt` | PyInstaller dependencies |

---

## Conventions

### PyQt6 Implementation

```python
# Layouts: ALWAYS use layouts, NEVER absolute positioning
layout = QVBoxLayout(widget)
layout.setContentsMargins(16, 16, 16, 16)
layout.setSpacing(12)

# Signals: Use pyqtSlot decorator for handlers
from PyQt6.QtCore import pyqtSlot

@pyqtSlot(str)
def handle_selection(self, filename):
    pass

# Memory Safety: Always assign parent or store in self.
self.button = QPushButton("Click", parent=self)  # or
self.button = QPushButton("Click")
self.layout.addWidget(self.button)  # layout takes ownership
```

### Threading (Critical)

```python
# NEVER update GUI from worker threads
worker.signal.finished.connect(self.on_complete)  # Use signals

# NEVER subclass QThread
worker = Worker()
worker.moveToThread(thread)  # Correct pattern

# Offload >100ms operations to prevent UI freeze
```

### Styling (Dark Theme)

```python
# Theme Colors (DON'T deviate)
BG_DARK = "#121415"      # Main background
BG_CARD = "#1a1d21"      # Card/panel background
BORDER = "#2a2e33"       # Borders
TEXT_PRIMARY = "#E8EAED"
TEXT_SECONDARY = "#9ca3af"
ACCENT = "#00B884"       # Primary accent (green)
ACCENT_HOVER = "#00d69a"

# Fonts
# Main: Inter, 13px
# Labels: JetBrains Mono, 10px uppercase
```

### Path Handling (PyInstaller Compatible)

```python
import os
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
```

---

## PyQt6 CRITICAL RULES (READ BEFORE ANY UI CHANGE)

### The #1 Rule: ALWAYS SET PARENT

**WINDOW SPAWNING BUG:** If you create a widget without a parent, it becomes a separate window. This is the most common and frustrating bug.

```python
# ❌ WRONG - Spawns separate window
node = PipelineNodeWidget(node_data)

# ✅ CORRECT - Stays embedded in parent
node = PipelineNodeWidget(node_data, parent=self.nodes_container)
```

### Parent Assignment Checklist

**BEFORE creating ANY QWidget subclass, ask:**
1. Who is my parent widget?
2. Am I passing `parent=xxx` to `__init__`?
3. Am I calling `super().__init__(parent=parent)` in the child's `__init__`?

**Every widget constructor MUST have `parent=None` parameter:**
```python
class MyWidget(QWidget):
    def __init__(self, some_data, parent=None):  # parent parameter required
        super().__init__(parent=parent)  # Pass to super
        self.some_data = some_data
        # ... rest of init
```

**When creating child widgets inside a parent:**
```python
class PipelineNodeWidget(QWidget):
    def __init__(self, node_data, is_selected=False, parent=None):
        super().__init__(parent=parent)  # CRITICAL: Pass parent to super
        
        # All child widgets MUST have parent=self
        self.toggle = ToggleSwitch(checked=True, parent=self)  # ✅
        self.label = QLabel("Text", parent=self)  # ✅
        
        # Or add to layout (layout takes ownership)
        layout = QHBoxLayout(self)
        layout.addWidget(self.toggle)  # ✅ Layout takes ownership
```

### Widget Creation Rules

| Widget Type | Parent Required? | How to Set |
|-------------|------------------|------------|
| `QWidget` subclass | **YES** | `parent=self` in constructor |
| `QPushButton` | **YES** | `QPushButton("Text", parent=self)` |
| `QLabel` | **YES** | `QLabel("Text", parent=self)` |
| `QFrame` | **YES** | `QFrame(parent=self)` |
| Layout containers | **YES** | `QVBoxLayout(self)` - parent is the widget |

### Common Window-Spawning Mistakes

```python
# ❌ WRONG: Creating widget without parent
widget = MyCustomWidget(data)
layout.addWidget(widget)  # Too late! Window already spawned

# ✅ CORRECT: Pass parent at creation
widget = MyCustomWidget(data, parent=self)
layout.addWidget(widget)

# ❌ WRONG: Custom widget init without parent
class MyWidget(QWidget):
    def __init__(self, data):  # Missing parent parameter!
        super().__init__()  # No parent passed!
        
# ✅ CORRECT: Custom widget with parent
class MyWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
```

### The Layout Parent Trap

When you create a layout with `QVBoxLayout(self)`, the `self` becomes the parent. But child widgets added to the layout STILL need explicit parents if they're not immediately added:

```python
# ❌ WRONG: Creating widget before adding to layout
label = QLabel("Text")  # No parent - becomes window!
layout.addWidget(label)

# ✅ CORRECT: Pass parent when creating
label = QLabel("Text", parent=self)
layout.addWidget(label)

# ✅ ALSO CORRECT: Create and add immediately (layout takes ownership)
layout.addWidget(QLabel("Text", parent=self))
```

### Debugging Window Spawn Issues

**If a widget spawns as a separate window:**

1. **Check the widget's `__init__`** - Does it accept `parent=None`?
2. **Check `super().__init__()`** - Is `parent` being passed?
3. **Check instantiation** - Is `parent=xxx` being passed when creating?
4. **Check ALL child widgets** - Every child must have parent set

**Quick diagnostic:**
```python
# Add this to check if widget has proper parent
if widget.parent() is None:
    print(f"WARNING: {widget} has no parent - will spawn as window!")
```

---

## Anti-Patterns (Forbidden)

| Pattern | Why Forbidden | Correct Approach |
|---------|---------------|------------------|
| `resize()`, `move()` | Breaks layouts, non-responsive | Use QVBoxLayout/QHBoxLayout/QGridLayout |
| Subclassing `QThread` | Error-prone, harder to manage | Use `worker.moveToThread(thread)` |
| GUI updates from worker | Crashes, race conditions | Use Signals/Slots for thread communication |
| `time.sleep()` in UI | Freezes interface | Use `QTimer.singleShot()` or `QThread` |
| Import PyQt in `models/` | Breaks CLI testability | Keep models pure Python |
| `uic.loadUi()` edits | Generated code changes | Subclass .ui files or load dynamically |
| No parent assignment | Python GC destroys widgets | Assign parent= or store in self. |
| Image processing in `paintEvent` | Performance killer | Process once, cache result |
| Direct model access from UI | Violates MVC | Emit signals, let controller handle |

---

## Testing (`pytest` + `pytest-qt`)

**Stack:** pytest, pytest-qt, pytest-mock. **Never unittest.**

```python
# GUI Testing with qtbot
def test_button_click(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)  # Cleanup handled automatically
    
    with qtbot.waitSignal(widget.clicked, timeout=1000):
        qtbot.mouseClick(widget.button, Qt.MouseButton.LeftButton)

# Mock blocking dialogs to prevent test hangs
def test_save_dialog(monkeypatch):
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName",
        lambda *args, **kwargs: ("/tmp/test.png", "")
    )
```

**Test Pyramid:**
- 70% Logic tests (no GUI import)
- 20% Integration tests
- 10% GUI tests (minimal)

**Always run tests before presenting results:** `pytest tests/ -v`

---

## Commands

```bash
# Development
python src/main.py

# Testing
pytest tests/ -v
pytest tests/test_image_model.py -v  # Single module

# Build (PyInstaller)
pyinstaller SimplePhantast_Optimized.spec

# Format/Lint
ruff check src/
ruff format src/
```

---

## Key Implementation Notes

### Image Navigation Flow
1. User clicks "Open Folder" → View emits `open_folder_requested`
2. Controller handles → Updates `ImageSessionModel`
3. Model scans directory → Filters valid extensions (.png, .jpg, .tiff)
4. Controller calls `_update_view_from_model()` → View updates file list
5. User clicks file → Controller loads image to canvas

### Pipeline System
- Pipelines are serializable JSON configurations
- Each step is a reusable component in `src/core/steps/`
- Steps can be chained: preprocessing → segmentation → analysis

### Memory Management
- Large images are loaded as `QImage` with careful memory management
- Canvas uses lazy loading with thumbnail previews
- Always call `deleteLater()` on dynamic widgets

---

## Gotchas

1. **sys.path manipulation:** Both `src/main.py` and `shell/` use `sys.path.append` for imports. Always use absolute imports from `src.`

2. **Dual MainWindow:** There's `src/ui/main_window.py` (current) and `shell/shell/main_window.py` (legacy). Work on the `src/` version unless explicitly told otherwise.

3. **Image extensions:** Valid extensions are hardcoded in `ImageSessionModel`: `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`

4. **Signal/slot types:** PyQt6 is stricter than PyQt5. Signal parameter types must match slot decorator exactly.

5. **Stylesheet inheritance:** Child widgets inherit parent stylesheets. Use object names (`#WidgetName`) for specific targeting.

---

## External Documentation

- **Phantast Algorithm:** See `PHANTAST Cell Confluency Detection Explained.md`
- **Product Plan:** See `product-plan/` directory
- **Build Scripts:** `build_optimized.bat`, `SimplePhantast_Optimized.spec`
