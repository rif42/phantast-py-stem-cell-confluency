# Batch Workflow Specification

## Overview
Manages the execution of batch processing and the formatting of results. It handles the "running" state when a user executes a pipeline on a folder of images and controls how final images are generated.

## User Flows
- **Execute Batch**: Click "Run" in the Pipeline Builder with a folder input selected.
- **Monitor Progress**: Watch a modal progress bar that blocks the UI during processing (app becomes unresponsive to prevent interference).
- **Configure Output**: Set global preferences for formatting result images.

## UI Requirements
- **Progress Modal**: Centered, blocking dialog with progress bar and status text ("Processing image X of Y").
- **Output Formatting**: Global setting to add a **Data Header** (white space at the top of the image) containing:
    - Parameter values (Sigma, Epsilon).
    - Calculated Confluency %.
- **Completion Summary**: Simple notification showing success/failure counts.

## Configuration
- shell: true
