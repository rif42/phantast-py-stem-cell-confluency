# Application Shell Specification

## Overview
A modern, 3-column "Studio" layout designed for image processing workflows. It features a central workspace for the image, flanked by a pipeline manager on the left and a parameter editor on the right.

## Navigation Structure
- **Image Analysis Workspace** (Default View)
    - Left: Pipeline Steps List
    - Center: interactive Image Viewer (Zoom, Pan, Split View)
    - Right: Step Parameters / Tool Settings
- **Batch Workflow**
    - Switches central view to Batch List & Progress
    - Left/Right panels may adapt or hide

## Layout Pattern
**Docking Window Layout (QMainWindow)**
- **Central Widget:** The Image Viewer (or Batch View).
- **Left Dock:** "Pipeline" panel.
- **Right Dock:** "Settings" or "Parameters" panel.
- **Toolbar:** Top strip for global tools (Open, Save, Undo/Redo).
- **Status Bar:** Bottom strip for image info and progress.

## Components
- `MainWindow`: The main container managing docks and central widget.
- `PipelinedWidget`: Custom widget for the left panel.
- `PropertiesWidget`: Custom widget for the right panel.
- `ImageViewer`: Central custom graphics view.

## Design Notes
- Dark theme by default (using Teal/Charcoal palette).
- Floating controls in the image viewer for zoom/fit.
- "Add Step" button prominent in the left panel.
