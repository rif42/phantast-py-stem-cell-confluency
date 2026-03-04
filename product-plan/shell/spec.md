# Application Shell Specification

## Overview
The application shell for Phantast Lab serves as a unified workspace for image analysis. It provides persistent navigation elements, sidebars for pipeline construction and node configuration, and a central area for image inspection.

## Navigation Structure
- **Left Panel (Pipeline Stack):** Manages the sequence of processing steps. Continues logically from input data down to final algorithm output.
- **Center Area (Image Viewer):** The primary view for the active microscope image. Contains floating or top toolbars for image tools (pan, measure, zoom).
- **Right Panel (Properties):** Context-sensitive properties panel that updates based on the selected step in the pipeline or the loaded image. Includes folder exploration, image metadata, and a histogram.

## Layout Pattern
Workspace Panels (Dock Widgets / Fixed Sidebars).
The UI features a persistent Top Header, flanked by deep dark left and right sidebars, with a darker central image canvas, providing high contrast for examining lab assets.

## Components
- **Top Header (`QFrame`):** App branding on left, user profile on right. Background `#1E2224`.
- **Main Splitting Container (`QSplitter` or `QMainWindow` docks):** 
- **Left Sidebar:** Dark `#121415` background. Contains project title, Add nodes button, Pipeline list, and a prominent bottom Action Button (`#00B884`).
- **Right Sidebar:** Dark `#121415` background. Accordion/collapsible style sections for deep property inspection.
- **Central Canvas:** Background dark/black to isolate the image.

## Design Notes
- **Colors:**
  - Primary: `#00B884` (Teal/Emerald)
  - Secondary: `#E8A317` (Amber)
  - Neutral Backgrounds: `#121415` for sidebars, `#1E2224` for header/cards.
  - Borders: `#2D3336`
  - Text: `#E8EAED` (Primary), `#9AA0A6` (Muted)
- **Typography:**
  - Headings/UI: `Inter`
  - Data/Metrics: `JetBrains Mono`
- Button states should contrast clearly, with the primary action (Run Pipeline) standing out significantly from the rest of the dark UI.
