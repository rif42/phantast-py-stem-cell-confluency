# Draft: PHANTAST Output Format Node

## Requirements (confirmed)
- when we add a phantast node, automatically add another node named "output format" below the phantast node.
- when user select this node, parameter "show confluency" will show on right sidebar, can activate/deactivate.
- "show confluency" is activated by default.
- this node will configure what kind of label or extra information that will show up on the final image.
- if "show confluency" is activated, add a small white blank space below the image and put "confluency xx%".
- this confluency number is from PHANTAST segmentation node.

## Technical Decisions
- Auto-insertion should follow `MainWindow.handle_add_step` / `_create_*_node` pattern in `src/ui/main_window.py` because pipeline nodes are currently flat list entries.
- Confluency caption will be rendered in persisted output image files (not display-only).
- Confluency caption rendering applies to both output modes: `mask` and `processed` files.
- Right sidebar toggle should be integrated via `UnifiedRightPanel.show_properties` parameter widget path in `src/ui/unified_right_panel.py`.
- Test approach: minimal tests only.

## Research Findings
- Pipeline node flow and node selection routing live in `src/ui/main_window.py` (`handle_add_step`, `handle_node_selected`).
- Node UI/selection/reordering behavior lives in `src/ui/pipeline_stack_widget.py`.
- Parameter panel generation is metadata-driven via step registry in `src/ui/unified_right_panel.py` and `src/core/steps/__init__.py`.
- PHANTAST confluency is computed in `src/core/steps/phantast_step.py` but currently not rendered as text in output.
- Final overlay/image artifact flow currently lives in `src/core/pipeline_worker.py` and `src/ui/image_canvas.py`.
- Tests exist (pytest + pytest-qt patterns) in `tests/`, including UI integration and worker-signal tests; no in-repo CI workflow detected.

## Open Questions
- None.

## Scope Boundaries
- INCLUDE: auto-creation of output format node, sidebar toggle, default enabled state, final image label rendering using PHANTAST confluency value.
- EXCLUDE: broader pipeline redesign or non-confluency output labels unless required by existing architecture.
