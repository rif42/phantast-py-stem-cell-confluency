# Image Analysis Workspace Specification

## Overview
The primary interface for inspecting images as they move through the processing pipeline. It allows deep inspection (pan/zoom, histogram) and direct comparison between any two processing stages.

## User Flows
- **Inspect Step Output**: Select a step in the pipeline list (vertical side panel) to view its processed image.
- **Compare Nodes**: Select two different steps (e.g., "Original" vs "Final") to activate the split-screen comparison slider.
- **Micro-Measurement**: Use a temporary ruler to measure pixel distances.
- **Markup**: Add persistent markers (points/labels) to annotate features of interest.

## UI Requirements
- **Main View**: High-performance image canvas (pan/zoom).
- **Comparison Mode**: Draggable vertical slider revealing Image A vs Image B.
- **Pipeline Strip**: A visual vertical list of nodes/steps on the side to select for viewing.
- **Info Panel**: Live Histogram and pixel intensity values under cursor.
- **Toolbar**: Tools for Pan, Ruler, and Marker.

## Configuration
- shell: true
