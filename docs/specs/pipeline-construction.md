# Pipeline Construction

## Overview

A linear visual editor in the left sidebar that manages the sequential steps of an image processing pipeline. It allows researchers to quickly assemble, reorder, and toggle algorithms (nodes) to test their confluency models on the active image.

## User Flows

1. User clicks an **"Add Step"** button and selects a processing node from a simple dropdown menu.
2. A new processing node is appended to the bottom of the pipeline stack.
3. User drags and drops nodes vertically to reorder the sequence of operations.
4. User toggles the active/disabled switch on an individual node to see how the final output changes.
5. User right-clicks on a node and selects **"Delete"** to remove it from the pipeline.
6. The system visually connects the nodes with a semi-transparent, downward-pointing line to reinforce the top-to-bottom flow.

## UI Requirements

| Component | Description |
|-----------|-------------|
| Add Step Button | Opens a popup menu with available processing nodes |
| Pipeline Stack | List of `PipelineNode` components |
| PipelineNode | Displays name, icon, status indicator (active, disabled, error, processing), and ON/OFF toggle |
| Flow Indicator | Visual directional guide (downward line/arrow) between nodes |
| Context Menu | Right-click menu on each node with "Delete" action |
| Run Button | Central "Run Pipeline" execution button at bottom of stack |

## Available Node Types

| Category | Nodes |
|----------|-------|
| **Preprocessing** | CLAHE, Noise Reduction, Crop, Grayscale |
| **Enhancement** | Contrast, Sharpen, Blur |
| **Analysis** | PHANTAST (confluency detection) |
| **Annotation** | Text, Freeform Drawing |

## Status Indicators

| Status | Visual |
|--------|--------|
| Active | Green indicator, toggle ON |
| Disabled | Gray indicator, toggle OFF |
| Processing | Spinner/animation |
| Error | Red indicator with error message |

## Related

- Part of: [Architecture & Design](../architecture.md)
- See also: [User Flows](../user-flows.md) - Phase 2
