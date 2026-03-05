# Global Stylesheet System Implementation Plan

## Overview

Transform the scattered, inline PyQt6 stylesheets into a centralized, component-based system similar to React's styled-components. This will ensure consistency across all windows and states while making the UI more maintainable.

## Current State Analysis

### Problems Identified

1. **Styles scattered across files:**
   - `main_window.py` - Global app stylesheet (basic colors)
   - `image_navigation.py` - Widget-specific stylesheet (~150 lines in `apply_styles()`)
   - `pipeline_view.py` - Inline styles in constructors
   - Individual `setStyleSheet()` calls throughout UI files

2. **Inconsistent color usage:**
   - Hardcoded hex values repeated everywhere
   - No single source of truth for design tokens
   - Risk of color drift between components

3. **No component reusability:**
   - Styles tightly coupled to specific widgets
   - Cannot easily share button/panel styles
   - Duplicated style code across files

4. **Dynamic state handling issues:**
   - Changing button states requires manual `unpolish()`/`polish()` calls
   - No systematic approach to hover/active states

## Proposed Solution

### Architecture

```
src/
└── ui/
    ├── styles.py              # NEW: Central stylesheet system
    ├── style_manager.py       # NEW: Runtime style management
    └── components/
        ├── base_widget.py     # NEW: Base widget with style support
        └── styled_button.py   # NEW: Pre-styled components (optional)
```

### Design System Structure

#### 1. Theme Tokens (`Theme` class)
Single source of truth for all design values:

```python
class Theme:
    # Colors
    PRIMARY = "#00B884"
    BG_DARK = "#121415"
    # ... all other tokens
    
    # Typography
    FONT_FAMILY = '"Inter", "Segoe UI", sans-serif'
    
    # Spacing
    SPACE_4 = "16px"
```

#### 2. Component Styles (`ComponentStyles` class)
Reusable style generators - like React components:

```python
class ComponentStyles:
    @staticmethod
    def button_primary() -> str:
        return """
            QPushButton#primaryButton {
                background-color: {Theme.PRIMARY};
                /* ... */
            }
            QPushButton#primaryButton:hover {
                background-color: {Theme.PRIMARY_HOVER};
            }
        """
```

#### 3. Global Stylesheet (`Styles` class)
Combines all components into application-wide stylesheet:

```python
class Styles:
    @staticmethod
    def get_global_stylesheet() -> str:
        # Combines all component styles
        # Applied once to QApplication
```

## Implementation Tasks

### Task 1: Create Core Stylesheet Module
**File:** `src/ui/styles.py`
**Estimated Time:** 1-2 hours
**Priority:** HIGH

**What to do:**
1. Create `Theme` class with all design tokens
2. Create `ComponentStyles` class with methods for each component type:
   - `button_primary()` - Main action buttons (emerald)
   - `button_secondary()` - Secondary buttons (dark with border)
   - `button_tool()` - Toolbar icon buttons
   - `panel()` - Side panels (left/right)
   - `canvas()` - Central image canvas
   - `toolbar()` - Floating toolbar
   - `node_input()` - Input nodes (blue)
   - `node_output()` - Output nodes (yellow)
   - `node_processing()` - Processing nodes
   - `typography()` - All text styles
   - `lists()` - File lists
   - `scrollbars()` - Custom scrollbars
   - `inputs()` - Form inputs
   - `file_items()` - File list items
3. Create `Styles` class with `get_global_stylesheet()` method
4. Export convenience constants

**Acceptance Criteria:**
- [ ] File created at `src/ui/styles.py`
- [ ] All colors from existing code extracted as Theme constants
- [ ] All component styles defined as static methods
- [ ] Global stylesheet generator working
- [ ] No hardcoded values - all use Theme tokens

### Task 2: Update Main Application Entry
**File:** `src/main.py`
**Estimated Time:** 15 minutes
**Priority:** HIGH

**What to do:**
1. Import `Styles` from `src.ui.styles`
2. Apply global stylesheet to QApplication before creating MainWindow
3. Remove existing stylesheet calls from MainWindow

**Current code:**
```python
app = QApplication(sys.argv)
window = MainWindow()
```

**New code:**
```python
app = QApplication(sys.argv)
app.setStyleSheet(Styles.get_global_stylesheet())  # ADD THIS
window = MainWindow()
```

**Acceptance Criteria:**
- [ ] Global stylesheet applied at app level
- [ ] MainWindow no longer calls `apply_stylesheet()`
- [ ] Application starts without errors
- [ ] Basic styling (colors) visible

### Task 3: Refactor MainWindow
**File:** `src/ui/main_window.py`
**Estimated Time:** 30 minutes
**Priority:** HIGH

**What to do:**
1. Remove `apply_stylesheet()` method entirely
2. Remove inline `setStyleSheet()` calls on widgets
3. Use `setObjectName()` for component identification
4. Keep only layout and widget creation code

**Changes needed:**
- Remove lines 35-50 (apply_stylesheet method)
- Remove inline styles on logo, title, avatar (lines 63, 66, 75)
- Add object names: `logo.setObjectName("appLogo")`, etc.

**Acceptance Criteria:**
- [ ] No setStyleSheet calls in MainWindow
- [ ] Widgets use setObjectName for styling
- [ ] Styling still works (from global stylesheet)

### Task 4: Refactor ImageNavigationWidget
**File:** `src/ui/image_navigation.py`
**Estimated Time:** 1 hour
**Priority:** HIGH

**What to do:**
1. Remove `apply_styles()` method (lines 436-597)
2. Keep only layout/widget creation code
3. Ensure all widgets have proper object names
4. Remove inline setStyleSheet calls

**Key changes:**
- Remove the entire ~160-line apply_styles() method
- Widgets already use object names like "primaryButton", "leftPanel" - good!
- Remove inline style on arrow (line 109): `arrow.setStyleSheet("color: #2D3336...")`
- Remove inline style on icons (lines 88, 118)

**Acceptance Criteria:**
- [ ] apply_styles() method removed
- [ ] No inline setStyleSheet calls remain
- [ ] All styled widgets have objectName set
- [ ] UI looks identical after changes

### Task 5: Refactor PipelineView
**File:** `src/ui/pipeline_view.py`
**Estimated Time:** 45 minutes
**Priority:** MEDIUM

**What to do:**
1. Move HelpTooltip styles to global stylesheet
2. Move icon_frame styles to component system
3. Remove inline setStyleSheet calls

**Changes:**
- Lines 50-60: HelpTooltip frame style
- Line 100: icon_frame style
- Any other inline styles

**Acceptance Criteria:**
- [ ] Inline styles removed
- [ ] Tooltips use global styling
- [ ] Pipeline nodes styled correctly

### Task 6: Create Style Manager (Optional Enhancement)
**File:** `src/ui/style_manager.py`
**Estimated Time:** 2 hours
**Priority:** LOW

**What to do:**
Create a runtime style manager for dynamic theme switching:

```python
class StyleManager:
    def __init__(self, app: QApplication):
        self.app = app
        self.current_theme = "dark"
    
    def apply_theme(self, theme_name: str):
        if theme_name == "dark":
            self.app.setStyleSheet(Styles.get_global_stylesheet())
        elif theme_name == "light":
            self.app.setStyleSheet(LightStyles.get_global_stylesheet())
    
    def reload_styles(self):
        """Hot-reload styles during development"""
        self.apply_theme(self.current_theme)
```

**Acceptance Criteria:**
- [ ] StyleManager class created
- [ ] Can switch themes at runtime
- [ ] Hot-reload working for development

### Task 7: Update BatchExecutionView
**File:** `src/ui/batch_execution_view.py`
**Estimated Time:** 30 minutes
**Priority:** MEDIUM

**What to do:**
1. Audit and remove inline styles
2. Add object names where needed
3. Ensure all styles come from global stylesheet

**Acceptance Criteria:**
- [ ] No inline setStyleSheet calls
- [ ] Object names properly set
- [ ] Consistent styling with rest of app

### Task 8: Create Pre-styled Components (Optional)
**Files:** `src/ui/components/*.py`
**Estimated Time:** 3 hours
**Priority:** LOW

**What to do:**
Create reusable widget classes with built-in styling:

```python
class PrimaryButton(QPushButton):
    """Button with primary styling built-in."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("primaryButton")

class StyledPanel(QFrame):
    """Panel with proper styling and layout."""
    def __init__(self, parent=None, position: str = "left"):
        super().__init__(parent)
        self.setObjectName("leftPanel" if position == "left" else "rightPanel")
```

**Components to create:**
- PrimaryButton
- SecondaryButton
- ToolButton
- StyledPanel
- CanvasArea

**Acceptance Criteria:**
- [ ] Components module created
- [ ] At least 3 pre-styled components working
- [ ] Components used in existing code

### Task 9: Documentation
**File:** `docs/styling-guide.md`
**Estimated Time:** 30 minutes
**Priority:** MEDIUM

**What to do:**
Create documentation for the new system:

1. How to use existing styles
2. How to add new component styles
3. How to override styles for specific cases
4. Best practices

**Acceptance Criteria:**
- [ ] Styling guide created
- [ ] Examples provided
- [ ] Added to main docs README

### Task 10: Testing
**Estimated Time:** 1 hour
**Priority:** HIGH

**What to do:**
1. Visual regression testing
2. Check all windows and states
3. Verify dynamic states (hover, active, disabled)
4. Test on different OS (Windows, macOS, Linux)

**Test Checklist:**
- [ ] Main window styling correct
- [ ] Left panel styling correct
- [ ] Right panel styling correct
- [ ] Canvas area correct
- [ ] Buttons (primary, secondary, tool) correct
- [ ] Node widgets (input, output, processing) correct
- [ ] File list styling correct
- [ ] Scrollbar styling correct
- [ ] Hover states work
- [ ] Active/selected states work
- [ ] Disabled states work

## Migration Strategy

### Phase 1: Foundation (Tasks 1-3)
1. Create styles.py with all design tokens
2. Update main.py to apply global stylesheet
3. Refactor main_window.py

### Phase 2: Core UI (Tasks 4-5)
1. Refactor image_navigation.py
2. Refactor pipeline_view.py

### Phase 3: Remaining UI (Tasks 7)
1. Refactor batch_execution_view.py
2. Any other UI files

### Phase 4: Enhancements (Tasks 6, 8-9)
1. Style manager (optional)
2. Pre-styled components (optional)
3. Documentation

## Benefits After Implementation

1. **Single Source of Truth:** All colors, fonts in one place
2. **Consistency:** Same button looks same everywhere
3. **Maintainability:** Change color once, applies everywhere
4. **Reusability:** Component styles can be mixed and matched
5. **Developer Experience:** Clear pattern for adding new styles
6. **Runtime Theming:** Foundation for light/dark mode switching

## Rollback Plan

If issues arise:
1. Keep old `apply_styles()` methods commented out initially
2. Can revert by uncommenting old code
3. Global stylesheet can be removed by commenting out `app.setStyleSheet()`

## Success Metrics

- [ ] Zero hardcoded hex values in UI files
- [ ] All styles defined in styles.py
- [ ] Application looks identical (or better) than before
- [ ] New widget can be styled by just setting object name
- [ ] Developer can add new component style in <5 minutes
