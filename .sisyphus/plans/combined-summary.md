# Consolidated Change Summary (`.sisyphus/plans`)

This document combines the proposed and completed changes described across all plan files in `.sisyphus/plans/`.

## High-Level Themes

1. **Main window architecture churn**
   - Multiple plans move the app between two layouts:
     - image-navigation-first (`restore-image-navigation.md`), and
     - unified image + pipeline construction (`combine-image-pipeline.md`, `fix-layout.md`).
   - The long-term direction is a **single-page integrated workspace** with left panel (nodes/navigation), center canvas, and right contextual panel.

2. **Pipeline system maturation**
   - A registry-driven node system was introduced (`pipeline-nodes.md`) with dynamic steps and dynamic parameter rendering.
   - CLAHE became the first functional processing step; Grayscale and Crop were scaffolded as placeholders.
   - Main-window integration and right-panel node property rendering became key follow-up work (`fix-clahe-params-bug.md`).

3. **Right panel UX upgrades (folder explorer + contextual content)**
   - The right sidebar was expanded to include a folder file list, refresh, selection behavior, and metadata (`folder-explorer-fix.md`).
   - Additional mode-specific behavior was planned for single-image workflows: hide folder explorer and auto-insert a single-image input node (`folder-explorer-single-image.md`).

4. **Visual and layout refinements**
   - Repeated efforts target left panel design fidelity (`fix-design.md`, `fix-left-panel-design.md`).
   - Empty canvas visuals and centering were iterated (`style-canvas-empty-state.md`, `fix-canvas-centering.md`, `remove-canvas-blank-space.md`).
   - A broad style architecture refactor proposes centralized theme tokens and global stylesheet ownership (`global-stylesheet-refactor.md`).

5. **Critical bug fixes and guardrails**
   - Widget parenting bug causing stray windows was identified and fixed at source (`fix-window-spawn.md`).
   - CLAHE parameter controls missing due to uninitialized node definitions were diagnosed and fixed (`fix-clahe-params-bug.md`).
   - Several plans explicitly enforce no popups/new windows and strict Qt parent assignment.

## Changes by Plan File

### `combine-image-pipeline.md`
- Integrates image navigation and pipeline editing into one `MainWindow` experience.
- Extracts reusable `PipelineStackWidget` and introduces `UnifiedRightPanel` with stacked metadata/property views.
- Requires signal routing through `MainWindow`, controller wiring, and Add-node enable/disable state tied to image load.
- Emphasizes single-page UX and no direct controller-to-controller coupling.

### `fix-canvas-centering.md`
- Fixes empty-state centering while preserving full-size image rendering.
- Keeps `image_canvas` with stretch and centers content using layout stretches instead of forced layout alignment.

### `fix-clahe-params-bug.md`
- Restores missing CLAHE parameter widgets in right properties panel.
- Adds `_load_available_nodes()` in `main_window.py` to build node definitions from `STEP_REGISTRY`.
- Ensures node metadata/parameter schema is available for dynamic property UI.

### `fix-design.md`
- Updates left panel visual design: project header, draft badge, stack title styling, and green Add button/menu styling.
- Keeps functional behavior unchanged (node list and run workflow remain intact).

### `fix-layout.md`
- Removes duplicate split rendering of image-navigation and pipeline widgets.
- Simplifies `MainWindow` to show only `PipelineConstructionWidget` and its controller in that plan direction.

### `fix-left-panel-design.md`
- Expanded version of left-panel visual refactor with stronger layout/spacing constraints.
- Includes wider panel, ordered hierarchy (project info -> stack header -> nodes -> run button), and styled Add menu popup.

### `fix-window-spawn.md`
- Fixes separate-window spawn by passing `parent=self` to `ToggleSwitch` inside `PipelineNodeWidget`.
- Reinforces strict parent propagation for all QWidget subclasses.

### `folder-explorer-fix.md`
- Implements folder explorer inside right metadata panel (list, refresh, empty state, selection visuals).
- Connects explorer events through `MainWindow` to `ImageNavigationController` for file loading.
- Revives logic that was missing due to `MainWindow.update_file_list()` being a no-op.

### `folder-explorer-single-image.md`
- Adds mode switching behavior:
  - folder mode -> show explorer,
  - single-image mode -> hide explorer.
- Auto-creates a single-image input node on direct image open, with duplicate prevention.

### `global-stylesheet-refactor.md`
- Proposes migration from scattered inline styles to centralized `styles.py` tokens/components.
- Applies app-wide stylesheet from startup and relies on object-name selectors.
- Targets consistency, maintainability, and elimination of hardcoded color duplication in UI modules.

### `pipeline-nodes.md`
- Introduces node/step architecture under `src/core/steps/` with registry and parameter schema.
- Ships CLAHE processing step and placeholder Grayscale/Crop steps.
- Integrates dynamic add-menu and dynamic right-panel parameter controls.

### `remove-canvas-blank-space.md`
- Removes extra top spacing between floating toolbar and empty-state content.
- Uses zero top margin on toolbar container and stretch on empty overlay.

### `restore-image-navigation.md`
- Reverts main window flow back to image-navigation-first architecture.
- Restores `ImageSessionModel` + `ImageNavigationWidget` + `ImageNavigationController` as core path.
- Keeps right sidebar explorer/metadata and empty-canvas open actions.

### `style-canvas-empty-state.md`
- Adds polished empty-state card (dashed rounded border, centered content, styled icon container).
- Keeps open-image/open-folder UX and hides empty-state container when an image is present.

## Net Effect Across Plans

- The codebase iterates between restoration and integration phases while converging toward a robust single-page scientific workflow UI.
- Pipeline capabilities evolve from static UI controls to registry-backed, dynamic node configuration.
- Right panel behavior becomes increasingly contextual (metadata vs node properties vs folder explorer visibility by mode).
- Visual consistency and maintainability are recurring priorities, culminating in a centralized stylesheet strategy.
- Stability issues (window spawning, missing parameter controls, spacing regressions) are addressed with targeted, architecture-aware fixes.
