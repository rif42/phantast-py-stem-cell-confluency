# Batch Execution & Output

## Overview

The final step where users apply their configured pipeline to a folder of images. It handles the batch processing, provides real-time progress monitoring, and exports both a comprehensive CSV report and the intermediate processed images for every node so users can review the end-to-end processing steps.

## User Flows

1. **Select Input** - User selects an input folder of images; the app automatically designates an output folder inside it.
2. **Execute** - User clicks **"Run Pipeline"** and views a real-time progress bar/status log as images are processed.
3. **Review Results** - Upon completion, a CSV report is generated and a summary data table is displayed directly in the app.
4. **Deep Dive** - User can select an image from the results table to "deep dive". This loads the original source image and all associated intermediate processed states for easy review.
5. **Export** - User can easily open the output folder from the app for manual file inspection.

## UI Requirements

| Component | Description |
|-----------|-------------|
| Input Selector | Folder selection mechanism with display of auto-generated output path |
| Progress Indicator | Progress bar showing "Processing X of Y images" |
| Status Log | Real-time processing log |
| Results Table | Scrollable data table view for final CSV results |
| Inspect Button | "Deep Dive" action on table rows to review processing steps |
| Open Folder Button | Quick access to output folder |

## Output Structure

```
input_folder/
├── original_image_1.jpg
├── original_image_2.jpg
└── output/
    ├── results.csv
    ├── image_1/
    │   ├── 01_clahe.jpg
    │   ├── 02_denoised.jpg
    │   ├── 03_phantast_mask.png
    │   └── metadata.json
    └── image_2/
        ├── 01_clahe.jpg
        ├── 02_denoised.jpg
        ├── 03_phantast_mask.png
        └── metadata.json
```

## CSV Report Columns

| Column | Description |
|--------|-------------|
| filename | Original image filename |
| confluency_pct | Calculated confluency percentage |
| cell_count | Estimated cell count |
| total_area | Total image area in pixels |
| processed_at | Timestamp of processing |

## Related

- Part of: [Architecture & Design](../architecture.md)
- See also: [User Flows](../user-flows.md) - Phase 3
