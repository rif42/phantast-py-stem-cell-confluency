# Image Navigation & Inspection Specification

## Overview
The core workspace for examining single microscope images and reviewing processing results. It provides detailed inspection tools and contextual metadata for researchers to understand their lab assets.

## User Flows
- User clicks, pans, and zooms around high-resolution microscope images using a floating toolbar.
- User selects the ruler tool to draw lines and measure specific cellular structures directly on the image.
- After the active pipeline finishes processing, the user toggles the segmentation mask on/off to compare the PHANTAST output against the raw image.
- User clicks an image in the left-hand Folder Explorer to view its specific data (resolution, bit depth, format) in the right-hand Properties panel.

## UI Requirements
- A large, dark central area for maximum contrast canvas.
- A floating toolbar positioned at the top center of the canvas containing icons for Pan, Measure, Zoom In/Out, and Fit to Screen.
- A toggle switch or button near the image to show/hide the confluency mask.
- Read-only fields in the right sidebar (Image Metadata section) displaying filename, dimensions, file size, bit depth, channels, and calculated confluency percentage.

## Configuration
- shell: true
