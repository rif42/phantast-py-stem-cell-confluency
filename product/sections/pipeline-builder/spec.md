# Pipeline Builder Specification

## Overview
The engine to create, reorder, and tune image processing steps. It uses a node-based list interface where users build a linear processing pipeline from top to bottom.

## User Flows
- **Add Processing Step**: Click the "+" button at the bottom of the list to open an accordion menu of available algorithms (e.g., CLAHE, Gaussian Blur) and append a step.
- **Edit Parameters**: Select a node in the left sidebar to reveal its specific parameters in the right sidebar properties panel.
- **Toggle/Reorder**: Drag nodes to reorder the pipeline or toggle them On/Off to temporarily disable steps.
- **Execute**: Click "Apply" (or use keyboard shortcut) to run the updated pipeline and view results.
- **Manage Presets**: Save the current configuration as a named preset or load an existing one.

## UI Requirements
- **Pipeline List (Left Sidebar)**: Vertical list growing downwards. Supports drag-and-drop and On/Off toggles.
- **Add Button**: Located at the bottom of the pipeline list.
- **Process Menu**: Accordion-style menu categorizing available steps.
- **Properties Panel (Right Sidebar)**: Context-sensitive form for the selected node's parameters.
- **Actions**: Explicit "Apply" button for processing.

## Configuration
- shell: true
