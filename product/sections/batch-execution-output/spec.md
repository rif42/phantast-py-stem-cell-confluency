# Batch Execution & Output Specification

## Overview
The final step where users apply their configured pipeline to a folder of images. It handles the batch processing, provides real-time progress monitoring, and exports both a comprehensive CSV report and the intermediate processed images for every node so users can review the end-to-end processing steps.

## User Flows
- User selects an input folder of images; the app automatically designates an output folder inside it.
- User clicks "Run Pipeline" and views a real-time progress bar/status log as images are processed.
- Upon completion, a CSV report is generated and a summary data table is displayed directly in the app.
- User can select an image from the results table to "deep dive". This action automatically loads the original source image and all of its associated intermediate processed states (which were saved during the batch step) so the user can easily scrub through the pipeline steps for that specific image.
- User can easily open the output folder from the app for manual file inspection.

## UI Requirements
- Input folder selection mechanism (with display of auto-generated output path).
- Progress indicator (e.g., progress bar, "Processing X of Y images").
- Scrollable data table view for the final CSV results.
- "Inspect" or "Deep Dive" button/action on table rows to review the processing steps of a specific image.
- "Open Output Folder" button for quick file inspection.

## Configuration
- shell: true
