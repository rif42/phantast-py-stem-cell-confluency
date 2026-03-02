# Implementation Guide

## Architecture
This application is built using PyQt6 (Qt for Python). 
- **Shell:** Managing the main window and navigation, integrating a `QStackedWidget` for view rotation.
- **Sections:** Modular features loaded into the central widget located in `src/sections`.

## Design System
The app uses QSS (Qt Style Sheets) for styling to enforce the dark theme.
- Colors and typography rules are locally defined within the `apply_stylesheet` methods of existing core widgets, mimicking the defined tokens.

## Mock Data
Presently, the UI depends on sample `data.json` schemas mapped inside the prototype files to automatically render inputs, properties, and image metadata.

## Next Steps
1. **Backend Integration:** Connect widgets to real backend logic (replacing the mock data in `data.json` files mapping with real Phantast API or Python internal logic).
2. **Data Persistence:** Implement database or standard file-reading APIs to manage project persistence.
3. **Core Processing:** Connect the OpenCV algorithm bindings to the "Run Pipeline" executions.
4. **Expand Test Coverage:** Build a `tests/` directory with `pytest-qt` integration.
