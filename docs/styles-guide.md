# Global Stylesheet System

## Overview

The global stylesheet system provides a **React-like component-based styling approach** for PyQt6 widgets. All design tokens and component styles are centralized in `src/ui/styles.py`, ensuring visual consistency across the entire application.

## Architecture

```
src/ui/styles.py
├── Theme              # Design tokens (colors, fonts, spacing)
├── ComponentStyles    # Reusable component style generators
├── Styles             # Global stylesheet combiner
└── StyleManager       # Runtime theme management (optional)
```

## Usage

### Applying Global Stylesheet

In `src/main.py`:

```python
from src.ui.styles import Styles

def main():
    app = QApplication(sys.argv)
    
    # Apply global stylesheet - applies to all widgets
    app.setStyleSheet(Styles.get_global_stylesheet())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

### Using Design Tokens

Access theme values directly in Python code:

```python
from src.ui.styles import Theme

# Use color tokens
widget.setStyleSheet(f"background-color: {Theme.BG_DARK};")

# Use spacing
layout.setSpacing(int(Theme.SPACE_4.replace('px', '')))
```

### Component Styling with Object Names

Widgets are styled via CSS selectors using `setObjectName()`:

```python
# In your widget class
button = QPushButton("Save")
button.setObjectName("primaryButton")  # Matches #primaryButton in stylesheet

label = QLabel("Title")
label.setObjectName("sectionHeader")   # Matches #sectionHeader in stylesheet
```

## Available Object Names

### Buttons

| Object Name | Purpose |
|-------------|---------|
| `primaryButton` | Main action buttons (green) |
| `secondaryButton` | Secondary actions, toggleable |
| `toolBtn` | Icon toolbar buttons |
| `toolBtnActive` | Active toolbar state |

### Typography

| Object Name | Purpose |
|-------------|---------|
| `appTitle` | Main application title |
| `panelHeader` | Sidebar section headers |
| `sectionHeader` | Content section titles |
| `sectionHeaderLarge` | Large titles (empty states) |
| `filenameLabel` | File name display |
| `fileDesc` | File metadata/description |
| `propertyLabel` | Property key labels |
| `propertyValue` | Property values (mono font) |

### Panels & Layout

| Object Name | Purpose |
|-------------|---------|
| `AppHeader` | Top header bar |
| `leftPanel` | Left sidebar |
| `rightPanel` | Right sidebar |
| `canvasArea` | Image canvas background |
| `canvasImage` | Canvas placeholder text |
| `floatingToolbar` | Floating toolbars |
| `fileBox` | File card containers |

### Pipeline Nodes

| Object Name | Purpose |
|-------------|---------|
| `nodeWidget` | Input nodes (blue border) |
| `nodeWidgetOutput` | Output nodes (orange border) |
| `nodeWidgetProcessing` | Processing nodes (green border) |
| `badgeInput` | Input badges |
| `badgeOutput` | Output badges |
| `badgeProcessing` | Processing badges |
| `nodeArrow` | Arrow between nodes |

### Lists

| Object Name | Purpose |
|-------------|---------|
| `fileList` | File browser list |

### Icons

| Object Name | Purpose |
|-------------|---------|
| `icon` | Standard icons (20px) |
| `largeIcon` | Large icons (48px) |

## Theme Tokens

### Colors

```python
Theme.PRIMARY          # #00B884 - Emerald green
Theme.PRIMARY_HOVER    # #00C890 - Lighter green
Theme.SECONDARY        # #E8A317 - Amber/yellow
Theme.BG_DARK          # #121415 - Main background
Theme.BG_CARD          # #1E2224 - Card backgrounds
Theme.BORDER           # #2D3336 - Borders
Theme.TEXT_PRIMARY     # #E8EAED - Primary text
Theme.TEXT_SECONDARY   # #9AA0A6 - Secondary text
Theme.TEXT_ON_PRIMARY  # #FFFFFF - Text on green
```

### Typography

```python
Theme.FONT_FAMILY      # 'Inter', 'Segoe UI', sans-serif
Theme.FONT_FAMILY_MONO # 'JetBrains Mono', monospace
Theme.FONT_SIZE_SM     # 11px
Theme.FONT_SIZE_BASE   # 13px
Theme.FONT_SIZE_LG     # 15px
Theme.FONT_SIZE_2XL    # 20px
```

### Spacing

```python
Theme.SPACE_2  # 8px
Theme.SPACE_4  # 16px
Theme.SPACE_6  # 24px
```

### Border Radius

```python
Theme.RADIUS_SM  # 4px
Theme.RADIUS_MD  # 6px
Theme.RADIUS_LG  # 8px
```

## Adding New Styles

### 1. Add Component Style

In `ComponentStyles` class, add a new static method:

```python
@staticmethod
def my_new_component() -> str:
    return f"""
        #myComponent {{
            background-color: {Theme.BG_CARD};
            color: {Theme.TEXT_PRIMARY};
            border-radius: {Theme.RADIUS_MD};
        }}
        #myComponent:hover {{
            background-color: {Theme.BORDER};
        }}
    """
```

### 2. Register in Global Stylesheet

Add to `Styles.get_global_stylesheet()`:

```python
components = [
    # ... existing components
    ComponentStyles.my_new_component(),
]
```

### 3. Use in Widget

```python
widget = MyWidget()
widget.setObjectName("myComponent")
```

## Migration Guide

### Before (Inline Styles)

```python
button = QPushButton("Save")
button.setStyleSheet("""
    background-color: #00B884;
    color: #FFFFFF;
    border-radius: 4px;
""")
```

### After (Global Stylesheet)

```python
button = QPushButton("Save")
button.setObjectName("primaryButton")
# Styles come from src/ui/styles.py
```

## Benefits

1. **Single Source of Truth** - Change a color once, applies everywhere
2. **Consistency** - No color value drift across files
3. **Maintainability** - Central location for all styling
4. **Runtime Theming** - Foundation for dark/light mode switching
5. **Component Reusability** - Same button style via object names

## Optional: Runtime Theme Switching

```python
from src.ui.styles import StyleManager

# Initialize manager
manager = StyleManager(app)

# Switch themes
manager.apply_theme("dark")
# manager.apply_theme("light")  # Future: light theme

# Hot reload during development
manager.reload_styles()
```

## Troubleshooting

### Styles Not Applying

1. Check `app.setStyleSheet(Styles.get_global_stylesheet())` is called before creating widgets
2. Verify object name matches selector exactly (`#primaryButton` vs `primaryButton`)
3. Check for typos in object names

### Conflicting Styles

- More specific selectors win: `#primaryButton` beats `QPushButton`
- Last declaration wins in QSS
- Use `!important` sparingly

### Debugging

```python
# Print generated stylesheet for inspection
print(Styles.get_global_stylesheet())

# Check applied stylesheet on widget
print(widget.styleSheet())
```
