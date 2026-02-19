---
description: You are helping the user export their complete product design as a handoff package for implementation. This generates all files needed to build the product in a real Python/PyQt codebase.
---

# Export Product

You are helping the user export their complete product design as a handoff package for implementation. This generates all files needed to build the product in a real Python/PyQt codebase.

## Step 1: Check Prerequisites

Verify the minimum requirements exist:

**Required:**
- `/product/product-overview.md` — Product overview
- `/product/product-roadmap.md` — Sections defined
- At least one section with screen designs in `src/sections/[section-id]/`

**Recommended (show warning if missing):**
- `/product/data-model/data-model.md` — Global data model
- `/product/design-system/colors.json` — Color tokens
- `/product/design-system/typography.json` — Typography tokens
- `src/shell/main_window.py` — Application shell

If required files are missing, stop and advise the user.

## Step 2: Gather Export Information

Read all relevant files:
1. `/product/product-overview.md`
2. `/product/product-roadmap.md`
3. Data models and Design tokens.
4. Shell spec and implementation.
5. Section specs and implementations (`src/sections/`).

## Step 3: Create Export Directory Structure

Create the `product-plan/` directory with this structure:

```
product-plan/
├── README.md                    # Quick start guide
├── requirements.txt             # Python dependencies
├── src/                         # Source code
│   ├── main.py                  # Entry point
│   ├── shell/                   # Shell components
│   ├── sections/                # Feature sections
│   ├── utils/                   # Utilities
│   └── assets/                  # Images/Icons
├── docs/                        # Documentation
│   ├── product-overview.md
│   ├── architecture.md
│   └── instructions/            # Implementation instructions
└── tests/                       # Test placeholders
```

## Step 4: Generate Configuration Files

### requirements.txt
```text
PySide6>=6.0.0
requests
# Add other dependencies
```

### README.md
Instructions on how to install dependencies (`pip install -r requirements.txt`) and run the application (`python src/main.py`).

## Step 5: Export Code

### Shell
Copy `src/shell/` to `product-plan/src/shell/`. Ensure imports are relative or absolute based on the new structure.

### Sections
Copy `src/sections/` to `product-plan/src/sections/`.
- Remove `properties` preview scripts if they are not needed in the final build, or move them to `tests/`.
- Ensure `__init__.py` files exist for package recognition.

### Main Entry Point
Create `product-plan/src/main.py` that initializes the `QApplication`, loads the `MainWindow`, and starts the event loop.

```python
import sys
from PySide6.QtWidgets import QApplication
from shell.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

## Step 6: Generate Documentation

Create `product-plan/docs/product-overview.md` with the content from the original product overview.

Create `product-plan/docs/instructions/implementation_guide.md`:

```markdown
# Implementation Guide

## Architecture
This application is built using PySide6 (Qt for Python). 
- **Shell:** Managing the main window and navigation.
- **Sections:** Modular features loaded into the central widget.

## Design System
The app uses QSS (Qt Style Sheets) for styling.
- Colors and Fonts are defined in `src/utils/styles.py` (or similar).

## Next Steps
1. Connect widgets to real backend logic (replacing mock data).
2. Implement data persistence (database/API).
3. Expand test coverage in `tests/`.
```

## Step 7: Confirm Completion

Let the user know:

"I've exported your product design to `product-plan/`.

**Structure:**
- `src/` contains the runnable PyQt application.
- `docs/` contains the overview and implementation guide.
- `requirements.txt` lists the dependencies.

**To Run:**
1. `pip install -r product-plan/requirements.txt`
2. `python product-plan/src/main.py`

You now have a working skeleton of your desktop application!"
