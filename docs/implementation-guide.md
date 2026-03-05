# Implementation Guide

## Technology Stack

- **PyQt6** - Desktop GUI framework (Qt for Python)
- **OpenCV** - Computer vision and image processing
- **NumPy/SciPy** - Numerical computing
- **scikit-image** - Image processing algorithms

## Architecture Pattern

This application is built using **PyQt6** with a strict MVC/MVP architecture:

- **Shell:** Managing the main window and navigation, integrating a `QStackedWidget` for view rotation.
- **Sections:** Modular features loaded into the central widget located in `src/sections`.

### File Organization

```
src/
├── main.py              # Entry point
├── ui/                  # View layer - PyQt6 widgets ONLY
├── models/              # Model layer - Pure Python, no Qt imports
└── controllers/         # Controller layer - Binds models to UI via signals
```

**Critical Rule:** Code in `models/` must be runnable from CLI without importing PyQt.

---

## Design System

The app uses QSS (Qt Style Sheets) for styling to enforce the dark theme.

### Color Tokens

```python
BG_DARK = "#121415"      # Main background
BG_CARD = "#1a1d21"      # Card/panel background
BORDER = "#2a2e33"       # Borders
TEXT_PRIMARY = "#E8EAED"
TEXT_SECONDARY = "#9ca3af"
ACCENT = "#00B884"       # Primary accent (green)
ACCENT_HOVER = "#00d69a"
```

Colors and typography rules are locally defined within the `apply_stylesheet` methods of existing core widgets.

### Typography

- **Main:** Inter, 13px
- **Labels:** JetBrains Mono, 10px uppercase

---

## Development Guidelines

### PyQt6 Standards

```python
# Layouts: ALWAYS use layouts, NEVER absolute positioning
layout = QVBoxLayout(widget)
layout.setContentsMargins(16, 16, 16, 16)
layout.setSpacing(12)

# Signals: Use pyqtSlot decorator
from PyQt6.QtCore import pyqtSlot

@pyqtSlot(str)
def handle_selection(self, filename):
    pass

# Memory Safety: Always assign parent or store in self
self.button = QPushButton("Click", parent=self)
```

### Threading (Critical)

```python
# NEVER update GUI from worker threads
worker.signal.finished.connect(self.on_complete)

# NEVER subclass QThread
worker = Worker()
worker.moveToThread(thread)  # Correct pattern
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

## Testing

**Stack:** pytest, pytest-qt, pytest-mock. **Never unittest.**

```python
# GUI Testing with qtbot
def test_button_click(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)
    
    with qtbot.waitSignal(widget.clicked, timeout=1000):
        qtbot.mouseClick(widget.button, Qt.MouseButton.LeftButton)

# Mock blocking dialogs
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

**Always run tests:** `pytest tests/ -v`

---

## Build & Deployment

### Commands

```bash
# Development
python src/main.py

# Testing
pytest tests/ -v

# Build (PyInstaller)
pyinstaller SimplePhantast_Optimized.spec

# Format/Lint
ruff check src/
ruff format src/
```

### Dependencies

See `requirements_build.txt` for PyInstaller build dependencies:
- opencv-python-headless
- numpy
- scipy
- scikit-image
- PyQt6
- pyinstaller

---

## Next Steps

1. **Backend Integration** - Connect widgets to real backend logic (replacing mock data with real Phantast API or Python internal logic)
2. **Data Persistence** - Implement database or standard file-reading APIs to manage project persistence
3. **Core Processing** - Connect the OpenCV algorithm bindings to the "Run Pipeline" executions
4. **Expand Test Coverage** - Build a `tests/` directory with `pytest-qt` integration
