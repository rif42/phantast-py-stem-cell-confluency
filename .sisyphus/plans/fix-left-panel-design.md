# Work Plan: Fix Left Panel Design

## Objective
Update the left sidebar in `src/ui/pipeline_view.py` to match the design screenshot exactly.

## Changes Required

### File: `src/ui/pipeline_view.py`

Modify the `create_left_panel()` method (around line 322) to add:

1. **Project Header Section** (BEFORE "PIPELINE STACK"):
   ```python
   # Project Header (matches design)
   project_header = QFrame()
   project_header_layout = QVBoxLayout(project_header)
   project_header_layout.setContentsMargins(0, 0, 0, 0)
   project_header_layout.setSpacing(2)

   project_title_row = QHBoxLayout()
   project_title_row.setSpacing(8)

   project_name = QLabel("Untitled Project")
   project_name.setStyleSheet("color: #E8EAED; font-size: 14px; font-weight: 600;")

   # Yellow dot indicator
   status_dot = QLabel("●")
   status_dot.setStyleSheet("color: #E8A317; font-size: 10px;")

   project_title_row.addWidget(project_name)
   project_title_row.addWidget(status_dot)
   project_title_row.addStretch()
   project_header_layout.addLayout(project_title_row)

   project_status = QLabel("Draft - Unsaved")
   project_status.setStyleSheet("color: #9AA0A6; font-size: 11px;")
   project_header_layout.addWidget(project_status)

   layout.addWidget(project_header)
   layout.addSpacing(20)
   ```

2. **Update Pipeline Stack Header**:
   - Change minimumWidth from 250 to 280
   - Update "PIPELINE STACK" label styling:
     ```python
     header.setStyleSheet("""
         color: #9AA0A6; 
         font-size: 10px; 
         font-weight: 600; 
         letter-spacing: 1px;
     """)
     ```
   - Update Add button styling:
     ```python
     add_btn.setStyleSheet("""
         QPushButton {
             background-color: #00B884;
             color: white;
             border: none;
             border-radius: 6px;
             padding: 6px 16px;
             font-size: 12px;
             font-weight: 600;
         }
         QPushButton:hover {
             background-color: #00D69A;
         }
     """)
     ```

3. **Add Menu Styling**:
   ```python
   self.add_menu.setStyleSheet("""
       QMenu {
           background-color: #1E2224;
           border: 1px solid #2D3336;
           border-radius: 6px;
           padding: 4px;
       }
       QMenu::item {
           padding: 8px 16px;
           color: #E8EAED;
       }
       QMenu::item:selected {
           background-color: #2D3336;
           border-radius: 4px;
       }
   """)
   ```

## Full Method Replacement

Replace the entire `create_left_panel()` method (lines 322-390) with the updated version that includes the project header.

## QA Checklist

Run `python src/main.py` and verify:
- [ ] Left sidebar shows "Untitled Project" with yellow dot indicator
- [ ] Shows "Draft - Unsaved" subtitle below project name
- [ ] "PIPELINE STACK" label is uppercase, muted gray, with letter-spacing
- [ ] Add button is green (#00B884) with rounded corners (6px radius)
- [ ] Add button hover state is lighter green
- [ ] Clicking Add shows styled popup menu with CLAHE, Grayscale, Crop options
- [ ] Menu has dark background (#1E2224) with proper styling
- [ ] Layout spacing matches the design (16px margins, proper gaps)

## Expected Result

The left panel should match the design screenshot exactly:
```
┌─────────────────────────┐
│ Untitled Project ●      │  <- Project title with yellow dot
│ Draft - Unsaved         │  <- Gray subtitle
│                         │
│ PIPELINE STACK    [Add] │  <- Section header + green button
│ ┌─────────────────┐     │
│ │ Original  [ON]  │     │  <- Nodes with toggles
│ └─────────────────┘     │
│ ┌─────────────────┐     │
│ │ CLAHE     [ON]  │     │
│ └─────────────────┘     │
│                         │
│ [Run Pipeline]          │  <- Bottom button
└─────────────────────────┘
```
