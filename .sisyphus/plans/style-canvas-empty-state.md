# Work Plan: Style Canvas Empty State with Dashed Border

## TL;DR
Style the empty canvas state to match the reference design: add a dashed border container with rounded corners, centered content, and update the icon/button styling.

## Visual Changes Required

### 1. Add Dashed Border Container
The `empty_overlay` needs:
- Rounded corners (border-radius: 12px)
- Dashed border (2px dashed #3a3f44)
- Semi-transparent dark background (#15181a or similar)
- Proper margins so it doesn't touch the edges

### 2. Update Content Styling
- Icon: Change from emoji "🖼️" to a styled QLabel with border
- Title: "Select Input Image" - already exists
- Buttons: Keep green styling but ensure proper sizing
- Subtitle: "Supports JPG, PNG, TIFF & RAW formats up to 100MB" - already exists

### 3. Ensure Proper Centering
- Content should be vertically and horizontally centered within the dashed border
- The dashed border container itself should fill the available canvas space (minus margins)

## Files to Modify

**File**: `src/ui/main_window.py`

### Changes:

1. **Add margins around empty_overlay** (line ~223):
   - Wrap empty_overlay in a container with margins, OR
   - Set margins on the canvas_layout

2. **Update empty_overlay stylesheet** (in `apply_styles()` method ~577):
   - Add dashed border styling
   - Add rounded corners
   - Add dark semi-transparent background

3. **Update icon styling** (line ~191):
   - Change from simple emoji to a styled icon container
   - Add border, background, rounded corners

4. **Update layout alignment** (line ~189):
   - Ensure content is centered

## QA Criteria
1. Launch application - verify dashed border container appears
2. Verify border is 2px dashed gray color
3. Verify rounded corners on the container
4. Verify icon is centered and styled
5. Verify buttons are centered
6. Load an image - verify dashed border disappears and image displays
7. Close image - verify dashed border returns

## Verification Command
```bash
cd D:\work\phantast-py-stem-cell-confluency && python src/main.py
```

## Success Criteria
- [ ] Dashed border container with rounded corners visible
- [ ] Content (icon, title, buttons) centered within container
- [ ] Proper spacing/margins around the container
- [ ] Image loading still works correctly
- [ ] Container disappears when image is loaded
