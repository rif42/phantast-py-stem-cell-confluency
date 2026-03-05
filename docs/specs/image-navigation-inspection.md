# Image Navigation & Inspection

## Overview

The core workspace for examining single microscope images and reviewing processing results. It provides detailed inspection tools and contextual metadata for researchers to understand their lab assets.

## User Flows

- User clicks, pans, and zooms around high-resolution microscope images using a floating toolbar.
- User selects the ruler tool to draw lines and measure specific cellular structures directly on the image.
- After the active pipeline finishes processing, the user toggles the segmentation mask on/off to compare the PHANTAST output against the raw image.
- User clicks an image in the left-hand Folder Explorer to view its specific data (resolution, bit depth, format) in the right-hand Properties panel.

## UI Requirements

| Requirement | Description |
|-------------|-------------|
| Canvas | A large, dark central area for maximum contrast |
| Toolbar | Floating toolbar at top center with icons for Pan, Measure, Zoom In/Out, and Fit to Screen |
| Mask Toggle | Toggle switch or button to show/hide the confluency mask |
| Metadata Panel | Read-only fields in right sidebar displaying filename, dimensions, file size, bit depth, channels, and calculated confluency percentage |

## Tools

| Tool | Function |
|------|----------|
| **Pan** | Click and drag to move around the image |
| **Zoom In/Out** | Magnify or reduce image view |
| **Ruler** | Draw measurement lines on cellular structures |
| **Fit to Screen** | Reset view to show entire image |

## Related

- Part of: [Architecture & Design](../architecture.md)
- See also: [User Flows](../user-flows.md) - Phase 1
