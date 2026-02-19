---
description: You are helping the user design the application shell — the persistent navigation and layout that wraps all sections. This is a screen design for a PyQt Main Window.
---

# Design Shell

You are helping the user design the application shell — the persistent navigation and layout that wraps all sections. This will be a PyQt `QMainWindow` design.

## Step 1: Check Prerequisites

First, verify prerequisites exist:

1. Read `/product/product-overview.md` — Product name and description
2. Read `/product/product-roadmap.md` — Sections for navigation
3. Check if `/product/design-system/colors.json` and `/product/design-system/typography.json` exist

If overview or roadmap are missing:

"Before designing the shell, you need to define your product and sections. Please run:
1. `/product-vision` — Define your product
2. `/product-roadmap` — Define your sections"

Stop here if overview or roadmap are missing.

If design tokens are missing, show a warning but continue.

## Step 2: Analyze Product Structure

Review the roadmap sections and present navigation options suitable for a desktop application:

"I'm designing the shell for **[Product Name]**. Based on your roadmap, you have [N] sections:

1. **[Section 1]** — [Description]
2. **[Section 2]** — [Description]
...

Let's decide on the shell layout. Common desktop patterns:

**A. Sidebar Navigation (QListWidget/Custom Side Bar)** — Vertical nav on the left, QStackedWidget on the right
   Best for: Complex apps with many distinct modules.

**B. Tabbed Interface (QTabWidget)** — Tabs at the top
   Best for: Document-based apps or workspaces where context switching is frequent.

**C. Menu Bar + Toolbar (QMainWindow standard)** — Traditional desktop feel
   Best for: Productivity tools, editors.

Which pattern fits **[Product Name]** best?"

Wait for their response.

## Step 3: Gather Design Details

Use AskUserQuestion to clarify:

- "Should we include a status bar at the bottom?"
- "Do you need a persistent toolbar for common actions?"
- "Where should user profile/settings access be located?"
- "What should the 'home' or default view be when the app loads?"

## Step 4: Present Shell Specification

Once you understand their preferences:

"Here's the shell design for **[Product Name]**:

**Layout Pattern:** [Sidebar/Tabs/Menu]

**Navigation Structure:**
- [Nav Item 1] → [Section]
...

**User Interface:**
- [Menus/Toolbars details]
- [Status bar details]

**Responsive Behavior:**
- [Resize policies]

Does this match what you had in mind?"

Iterate until approved.

## Step 5: Create the Shell Specification

Create `/product/shell/spec.md`:

```markdown
# Application Shell Specification

## Overview
[Description of the shell design and its purpose]

## Navigation Structure
- [Nav Item 1] → [Section 1]
...

## Layout Pattern
[Description of the layout — sidebar, tabs, etc.]

## Components
- Main Window (QMainWindow)
- Central Widget (QStackedWidget or QTabWidget)
- Navigation Widget (QListWidget, QTabBar, etc.)

## Design Notes
[Any additional design decisions or notes]
```

## Step 6: Create Shell Components

Create the shell components at `src/shell/`:

### main_window.py
The main entry point inheriting from `QMainWindow`.

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget
# Import navigation components

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("[Product Name]")
        self.resize(1280, 800)
        
        # Setup central widget and layout
        # Setup navigation
```

### navigation.py
The navigation component (sidebar or custom widgets).

### index.py
Export key components if needed, or just rely on main_window.

**Component Requirements:**
- Use `PySide6`
- Apply stylesheet (QSS) based on design tokens
- Be structured for modularity (signals/slots for navigation)

## Step 7: Apply Design Tokens

If design tokens exist, apply them to the shell components via `setStyleSheet` or a central style manager:

**Colors:**
- Map `colors.json` to QSS variables (e.g., `background-color: [neutral]; color: [text-color];`)

**Typography:**
- Map `typography.json` to `font-family` and `font-size`.

## Step 8: Confirm Completion

Let the user know:

"I've designed the application shell for **[Product Name]**:

**Created files:**
- `/product/shell/spec.md` — Shell specification
- `src/shell/main_window.py` — Main window implementation
- `src/shell/navigation.py` — Navigation component

**Shell features:**
- [Layout pattern] layout
- Navigation for all [N] sections
- QSS styling support

**Important:** You can run this file directly with python to test the shell.

Next: Run `/shape-section` to start designing your first section."
