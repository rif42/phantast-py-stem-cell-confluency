# Pipeline Construction Specification

## Overview
A linear visual editor in the left sidebar that manages the sequential steps of an image processing pipeline. It allows researchers to quickly assemble, reorder, and toggle algorithms (nodes) to test their confluency models on the active image.

## User Flows
- User clicks an "Add Step" button and selects a processing node from a simple dropdown menu.
- A new processing node is appended to the bottom of the pipeline stack.
- User drags and drops nodes vertically to reorder the sequence of operations.
- User toggles the active/disabled switch on an individual node to see how the final output changes.
- User right-clicks on a node and selects "Delete" to remove it from the pipeline.
- The system visually connects the nodes with a semi-transparent, downward-pointing line to reinforce the top-to-bottom flow.

## UI Requirements
- An "Add Step" button opening a small popup menu.
- A list of `PipelineNode` components.
- Each `PipelineNode` must display its name, an icon, a status indicator (active, disabled, error, processing), and an ON/OFF toggle switch.
- A visual directional guide (downward line/arrow) rendered between the nodes.
- A right-click context menu on each node containing a "Delete" action.
- A central "Run Pipeline" execution button at the bottom of the stack.

## Configuration
- shell: true
