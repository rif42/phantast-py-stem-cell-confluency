# src/ui/ AGENTS.md

**Scope:** View layer - PyQt6 widgets for PhantastLab.

## STRUCTURE
```
ui/
├── main_window.py         # QMainWindow with header + nav
├── image_navigation.py    # Left panel (dir tree, thumbnails)
├── image_canvas.py        # Central image display + overlay
├── pipeline_view.py       # Right panel pipeline config
├── batch_execution_view.py
└── navigation.py          # Navigation widget components
```

## STYLING CONVENTIONS

### Theme Colors
```python
"""Dark theme palette"""
BG_DARK = "#121415"      # Main background
BG_CARD = "#1a1d21"      # Card/panel background
BORDER = "#2a2e33"       # Borders
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#9ca3af"
ACCENT = "#00B884"       # Primary accent (green)
ACCENT_HOVER = "#00d69a"
```

### StyleSheet Pattern
```python
self.setStyleSheet("""
    QWidget#mainContainer {
        background-color: #121415;
    }
    QPushButton#primaryButton {
        background-color: #00B884;
        border-radius: 6px;
        padding: 8px 16px;
    }
    QPushButton#primaryButton:hover {
        background-color: #00d69a;
    }
""")
```

### Typography
- Main: Inter, 12-14px
- Labels: JetBrains Mono, 10px uppercase
- Use font-weight: 500/600 for emphasis

## WIDGET PATTERNS

### Signal/Slot
```python
class ImageCanvas(QWidget):
    image_clicked = pyqtSignal(int, int)  # x, y coordinates
    
    def mousePressEvent(self, event):
        self.image_clicked.emit(event.pos().x(), event.pos().y())
```

### Layout Structure
```python
def _setup_ui(self):
    layout = QVBoxLayout(self)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(12)
    # ... add widgets
```

## ANTI-PATTERNS
- **NO** inline `resize()` or `move()` - use layouts
- **NO** image processing in paintEvent
- **NO** direct model access - emit signals instead
