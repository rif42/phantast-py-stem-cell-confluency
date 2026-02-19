# Phantast Integration Specification

## Overview
The distinct, final stage of every pipeline that executes the core confluency algorithm. It is permanently attached to the end of the pipeline and provides specific controls for the Phantast algorithm.

## User Flows
- **Configure Analysis**: Select the final "Phantast" node to adjust Sigma and Epsilon parameters.
- **Toggle Visualization**: Use quick-toggle buttons to show/hide the confluency mask (overlay) and feature outlines on the image.
- **Read Metrics**: View the calculated Confluency Percentage in the properties panel.
- **Deactivate**: Toggle the step "Off" to see the pre-analysis image, but the step cannot be deleted.

## UI Requirements
- **Pipeline Node**: Visually distinct "Terminal" node at the bottom of the list. Cannot be deleted or dragged.
- **Properties Panel**:
    - Inputs for Sigma and Epsilon.
    - Large display for **Confluency %**.
    - Toggle buttons for **Show Mask** and **Show Outline**.
- **Interaction**: Standard markers (from Workspace) work on top of this view.

## Configuration
- shell: true
