# User Flows

## Overview

Phantast Lab is designed around three primary phases of work, with optional extensions for specific use cases.

---

## Phase 1: Image Navigation & Inspection

The researcher explores the raw dataset to find representative images and identify the processing needed to standardize them.

### Steps

1. **Determine Input** - User selects an input folder containing raw mesenchymal stem cell images.
2. **Browse Dataset** - User navigates the dataset in the Image Navigation view to evaluate overall image quality.
3. **Select Representative Image** - User selects one typical image displaying common artifacts (e.g., uneven lighting, noise).
4. **Inspect Image** - User utilizes Canvas tools (Zoom, Pan, Ruler) to deeply examine the cell structures and plan the required preprocessing steps.

---

## Phase 2: Pipeline Engineering

The researcher constructs a custom image processing sequence designed to perfectly segment the cells in their specific dataset.

### Steps

1. **Construct Pipeline** - User navigates to the Pipeline Construction view and adds processing nodes to the Pipeline Stack (e.g., CLAHE, Noise Reduction, PHANTAST).
2. **Configure Nodes** - User selects each newly added node and fine-tunes its specific mathematical parameters (e.g., adjusting Sigma and Epsilon) using the Node Configuration properties panel.
3. **Apply & Test (Single Image)** - User runs the draft pipeline on the single representative image selected in Phase 1.
4. **Inspect Result** - User reviews the output on the canvas, toggling the generated segmentation mask overlay on/off to evaluate cell detection accuracy.
5. **Iterate & Refine (Repeat)** - If the segmentation is poor, the user modifies the pipeline (reorders nodes, adds new filters, tweaks parameters, or toggles individual nodes off) and re-tests until the mask perfectly isolates the cells.

> **Optional:** The user saves this perfected Pipeline Stack configuration to a template file so the lab can standardize on this protocol.

---

## Phase 3: Batch Processing & Export

The researcher applies the perfected pipeline to their entire dataset to generate final research metrics.

### Steps

1. **Batch Execution** - User navigates to the Batch Execution screen and runs the perfected pipeline against the entire input folder.
2. **Review Batch Output** - User monitors the Folder Explorer table. As files finish processing, the user clicks through them to review the final confluency percentages, computed cell counts, and segmented masks.
3. **Export Metrics** - User exports the final confluency calculations as a CSV report for their research.

---

## Alternative Flows

### Flow Extension A: Quick Single-Image Analysis

*Skips Phase 3 entirely.*

For users who just need to calculate confluency for a single image, they execute Phase 1, build a minimal pipeline in Phase 2 with just the PHANTAST algorithm, test it once, and read the confluency percentage directly from the Image Metadata panel.

### Flow Extension B: Manual Image Annotation

*Skips Phase 2 and 3.*

For creating figures for publication, the user completes Phase 1, applies basic cropping, and uses the annotation tools (text labels, freeform drawing) to highlight specific features before exporting just that single annotated image.

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1: NAVIGATION                       │
│  Input Folder → Browse → Select Image → Inspect (Zoom/Pan)  │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 2: PIPELINE                         │
│  Add Nodes → Configure → Test Single → Refine (Iterate)     │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 3: BATCH                            │
│  Run Batch → Review Results → Export CSV                    │
└─────────────────────────────────────────────────────────────┘
```
