# Work Plan: Add Folder Explorer to Properties Panel

## Problem
When loading a folder, files don't appear in the UI. The folder explorer widget exists in `ImageNavigationWidget` but the actual app uses `UnifiedMainWidget` with `PropertiesPanel`, which has no file list capability.

## Solution
Add a folder explorer section to `PropertiesPanel` that displays files when a folder is loaded.

## Files to Modify

### 1. `src/ui/properties_panel.py`

**Changes:**
1. Add imports for `QScrollArea`, `QPushButton`, and `pyqtSignal`
2. Add `FileListItem` class (copy from image_navigation.py)
3. Add folder explorer UI components:
   - Header: "Folder Explorer" with file count
   - Column headers: FILE, SIZE, STATUS
   - Scrollable file list
   - Previous/Next navigation buttons
   - Counter: "X / Y"
4. Add methods:
   - `update_file_list(files, folder_path)` - populate the list
   - `set_active_file(filename)` - highlight active file with "VIEWING" badge
   - `select_previous_file()` / `select_next_file()` - navigation
   - `_get_file_size(filepath)` - format file size
5. Add signal: `file_selected = pyqtSignal(str)`
6. Update styles for folder explorer theme

### 2. `src/ui/unified_main_widget.py`

**Changes:**
1. Connect `properties_panel.file_selected` signal to controller
2. Update `_on_image_loaded()` to:
   - Check if current image is from a folder
   - Call `properties_panel.update_file_list()` with files
   - Call `properties_panel.set_active_file()` to highlight current file
3. Add method `_on_file_selected_from_panel(filename)` to:
   - Tell controller to load the file
   - Update canvas

### 3. `src/controllers/main_controller.py`

**Changes:**
1. Add method `get_current_folder_files()` - return list of files in current folder
2. Add method `set_active_image_by_filename(filename)` - switch to specific file
3. Update `load_folder()` to store file list in state

## Implementation Steps

**Phase 1: Update PropertiesPanel**
- Add FileListItem widget class
- Add folder explorer UI layout
- Add navigation controls
- Add styling

**Phase 2: Update UnifiedMainWidget**
- Connect file_selected signal
- Update _on_image_loaded to populate file list
- Handle file selection from panel

**Phase 3: Update MainController**
- Add file navigation methods
- Store folder file list in state

## Testing
- Load folder with JPG files
- Verify file list appears with columns
- Click file to switch
- Use Previous/Next buttons
- Verify "VIEWING" badge shows on active file

## UI Layout (Properties Panel)
```
┌─ PROPERTIES ──────────────────────┐
│                                   │
│ [Image metadata section]          │
│                                   │
│ ┌─ Folder Explorer ─────────────┐ │
│ │ FILE        SIZE    STATUS    │ │
│ │ 📄 img1.jpg 2.1 MB  VIEWING   │ │
│ │ 📄 img2.jpg 2.4 MB            │ │
│ │ 📄 img3.jpg 2.1 MB            │ │
│ └───────────────────────────────┘ │
│                                   │
│ [‹ Previous] [2 / 3] [Next ›]    │
│                                   │
└───────────────────────────────────┘
```
