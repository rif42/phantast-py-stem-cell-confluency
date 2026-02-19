---
description: You are helping the user capture a screenshot of a screen design they've created. The screenshot will be saved to the product folder for documentation purposes.
---

# Screenshot Screen Design

You are helping the user capture a screenshot of a screen design they've created. The screenshot will be saved to the product folder for documentation purposes.

## Step 1: Identify the Screen Design

First, determine which screen design to screenshot.

Read `/product/product-roadmap.md` to get the list of available sections, then check `src/sections/` to see what screen designs exist.

If multiple screen designs exist, ask the user which one to screenshot.

"Which screen design would you like to screenshot?"

## Step 2: Capture the Screenshot

Since this is a desktop application (PyQt), we cannot use a browser tool. We will run the preview script and use `QWidget.grab().save()` to capture the widget's state programmatically.

The preview script should be at `src/sections/[section-id]/[ViewName]_preview.py`.

Modify the preview script temporarily or creating a temporary runner script to:
1. Initialize the app/widget.
2. Wait for it to render (process events).
3. Grab the widget as a pixmap.
4. Save the pixmap to disk.

Example runner code:

```python
import sys
import json
from PySide6.QtWidgets import QApplication
from sections.[section-id].views.[ViewName] import [ComponentClass]

# Load sample data
data_path = '../../product/sections/[section-id]/data.json'
with open(data_path) as f:
    data = json.load(f)

app = QApplication(sys.argv)
window = [ComponentClass](data)
window.show()

# Allow processing of events to ensure rendering
app.processEvents()

# Capture screenshot
pixmap = window.grab()
pixmap.save("product/sections/[section-id]/[ViewName].png")

print(f"Screenshot saved to product/sections/[section-id]/[ViewName].png")
sys.exit()
```

Run this temporary script using `python`.

## Step 3: Save the Screenshot

Verify the screenshot was saved to `product/sections/[section-id]/[filename].png`.

**Naming convention:** `[screen-design-name]-[variant].png`

## Step 4: Confirm Completion

Let the user know:

"I've saved the screenshot to `product/sections/[section-id]/[filename].png`.

The screenshot captures the **[ScreenDesignName]** screen design for the **[Section Title]** section."

## Important Notes

- Ensure `PySide6` is installed.
- Ensure the preview script can run headless or in the current environment.
