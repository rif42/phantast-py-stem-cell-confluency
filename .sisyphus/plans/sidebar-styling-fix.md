# Work Plan: Fix Right Sidebar Styling to Match Target Design

## Current Issues vs Target Design

### 1. Metadata Section
**Current:** Shows properties in a custom layout
**Target:** Simple labels (Dimensions, Bit Depth, Channels, File Size) in vertical list, values on right

### 2. Folder Explorer List Items
**Current:** Transparent background, basic styling
**Target:** Dark rounded background (#1E2224), file icon, green status pill

### 3. Navigation Controls
**Current:** Large buttons
**Target:** Compact "< Previous", "1 / 4", "Next >" style

### 4. Overall Spacing & Typography
**Current:** Various margins
**Target:** Consistent 16px padding, proper font hierarchy

## Files to Modify

### 1. `src/ui/properties_panel.py`

#### Changes to FileListItem:
```python
# Add dark rounded container
self.setStyleSheet("""
    FileListItem {
        background-color: #1E2224;
        border-radius: 6px;
        margin: 2px 0px;
    }
""")

# Change status to green pill instead of text
self.status_indicator = QWidget()  # Small green dot/pill
self.status_indicator.setFixedSize(8, 8)
self.status_indicator.setStyleSheet("""
    background-color: #00B884;
    border-radius: 4px;
""")
```

#### Changes to _setup_folder_explorer:
```python
# Add container with dark background for list
self.file_list_container.setStyleSheet("""
    background-color: transparent;
""")

# Update nav buttons to compact style
self.btn_prev.setText("< Previous")
self.btn_next.setText("Next >")
```

#### Changes to _show_properties:
```python
# Add metadata labels in vertical list with values on right
metadata_items = [
    ("Dimensions", dimensions),
    ("Bit Depth", bitdepth),
    ("Channels", channels),
    ("File Size", filesize),
]
for label, value in metadata_items:
    row = QHBoxLayout()
    row.addWidget(QLabel(label))
    row.addStretch()
    row.addWidget(QLabel(value))
```

### 2. Stylesheet Updates

#### File list item:
- Background: #1E2224
- Border-radius: 6px
- Padding: 10px 12px
- Margin: 2px 0

#### Status indicator:
- Green dot (#00B884)
- 8x8px circle
- Or green pill with "VIEWING" text

#### Navigation buttons:
- Smaller padding
- "< Previous" / "Next >" text
- Counter: "1 / 4" centered

## Implementation Steps

1. Update FileListItem styling (dark background, rounded)
2. Change status from text to green pill/dot
3. Update navigation button text and sizing
4. Fix metadata section layout
5. Adjust overall spacing and margins
