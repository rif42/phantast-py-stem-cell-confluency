# Work Plan: Enhanced Folder Explorer

## Problem Statement
1. Opening a folder doesn't correctly load JPG images
2. Folder explorer needs redesign to match reference: table layout with FILE/SIZE/STATUS columns, Previous/Next navigation, and "VIEWING" status indicator

## Analysis

### Current Implementation
- `ImageNavigationWidget` uses `QListWidget` for file list (simple text items)
- `ImageSessionModel` filters files by extensions (`.png`, `.jpg`, `.jpeg`, etc.)
- `ImageController` handles folder loading and file selection

### Issues to Fix
1. **JPG Loading**: Extension check may have case-sensitivity issues
2. **UI Redesign**: Need QTableWidget with custom columns and styling
3. **Navigation**: Add Previous/Next buttons with file counter (e.g., "2 / 48")
4. **Selection State**: Show "VIEWING" label on active file row

## Implementation Plan

### Phase 1: Fix JPG Loading (ImageSessionModel)
**File:** `src/models/image_model.py`

**Change:** Make extension check case-insensitive
```python
# Current (line 45):
self.files = [f for f in all_files if f.lower().endswith(self.valid_extensions)]
# This is already correct! Issue might be elsewhere.
```

Verify `valid_extensions` includes both cases:
```python
valid_extensions = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp",
                    ".PNG", ".JPG", ".JPEG", ".TIF", ".TIFF", ".BMP")
```

### Phase 2: Redesign File List Widget (ImageNavigationWidget)
**File:** `src/ui/image_navigation.py`

**Changes to `create_right_panel()`:**

Replace QListWidget with custom table-like layout:

```python
# Header row with columns
header_layout = QHBoxLayout()
header_layout.addWidget(QLabel("FILE"), stretch=3)
header_layout.addWidget(QLabel("SIZE"), stretch=1)
header_layout.addWidget(QLabel("STATUS"), stretch=1)

# File list container with custom items
self.file_list_container = QWidget()
self.file_list_layout = QVBoxLayout(self.file_list_container)
self.file_list_layout.setContentsMargins(0, 0, 0, 0)
self.file_list_layout.setSpacing(0)

# Store file widgets for updates
self.file_item_widgets = {}  # filename -> widget
```

**Create `FileListItem` class:**
- Row widget with: filename label, size label, status label
- Click handler to select file
- Selected state styling (highlighted background)
- "VIEWING" badge for active file

### Phase 3: Add Navigation Controls
**In `create_right_panel()`:**

Add below file list:
```python
nav_layout = QHBoxLayout()
self.btn_prev = QPushButton("< Previous")
self.lbl_counter = QLabel("1 / 48")
self.btn_next = QPushButton("Next >")
nav_layout.addWidget(self.btn_prev)
nav_layout.addWidget(self.lbl_counter)
nav_layout.addWidget(self.btn_next)
```

**Connect signals:**
- `btn_prev.clicked` → select previous file
- `btn_next.clicked` → select next file
- Update counter when selection changes

### Phase 4: Update Methods

**Update `update_file_list()`:**
```python
def update_file_list(self, files: list, folder_path: str = ""):
    # Clear existing widgets
    self._clear_file_list()
    
    # Create FileListItem for each file
    for filename in files:
        filepath = os.path.join(folder_path, filename)
        file_size = self._get_file_size(filepath)
        
        item = FileListItem(filename, file_size)
        item.clicked.connect(lambda f=filename: self.on_file_selected(f))
        self.file_list_layout.addWidget(item)
        self.file_item_widgets[filename] = item
    
    self.file_list_layout.addStretch()
```

**Add `set_active_file()`:**
```python
def set_active_file(self, filename: str):
    """Update UI to show which file is being viewed."""
    # Clear previous VIEWING status
    for name, widget in self.file_item_widgets.items():
        widget.set_status("" if name != filename else "VIEWING")
        widget.set_selected(name == filename)
    
    # Update counter
    if self.current_files:
        idx = self.current_files.index(filename) + 1
        self.lbl_counter.setText(f"{idx} / {len(self.current_files)}")
```

**Add navigation methods:**
```python
def select_previous(self):
    if not self.current_files or self.current_index <= 0:
        return
    self.current_index -= 1
    filename = self.current_files[self.current_index]
    self.on_file_selected(filename)

def select_next(self):
    if not self.current_files or self.current_index >= len(self.current_files) - 1:
        return
    self.current_index += 1
    filename = self.current_files[self.current_index]
    self.on_file_selected(filename)
```

### Phase 5: Styling

**Add to stylesheet:**
```css
#fileListItem {
    background-color: transparent;
    border-bottom: 1px solid #2D3336;
    padding: 8px;
}
#fileListItem:hover {
    background-color: #1E2224;
}
#fileListItem:selected {
    background-color: #0078D4;
}
#fileListItem QLabel {
    color: #E8EAED;
    font-size: 12px;
}
#statusLabel {
    color: #00B884;
    font-weight: bold;
    font-size: 10px;
}
#navButton {
    background-color: #1E2224;
    border: 1px solid #2D3336;
    color: #E8EAED;
    padding: 4px 12px;
    border-radius: 4px;
}
#navCounter {
    color: #9AA0A6;
    font-family: 'JetBrains Mono';
    font-size: 12px;
}
```

## Files to Modify
1. `src/models/image_model.py` - Verify/fix JPG extension handling
2. `src/ui/image_navigation.py` - Complete file list redesign
3. `src/controllers/image_controller.py` - Update to call set_active_file()

## Verification Checklist
- [ ] JPG files load correctly (both .jpg and .JPG)
- [ ] Folder explorer shows columns: FILE, SIZE, STATUS
- [ ] Each file shows correct size
- [ ] Selected file shows "VIEWING" status
- [ ] Previous/Next buttons work
- [ ] Counter shows correct position (e.g., "2 / 48")
- [ ] Clicking file loads it in canvas
- [ ] Styling matches dark theme
