# Fix Plan: Match Design Exactly

## Problem
The current layout is missing the "Untitled Project" header shown in the design. The left sidebar needs to match the reference image exactly.

## Design Requirements (from screenshot)
Left sidebar should have:
1. **Project Header**:
   - "Untitled Project" with yellow dot indicator
   - "Draft - Unsaved" subtitle
   
2. **Pipeline Stack Section**:
   - "PIPELINE STACK" label (uppercase, muted color)
   - Green "Add" button (rounded, #00B884)
   
3. **Nodes List**:
   - Original (INPUT) - blue badge
   - CLAHE (PROCESS) - gray badge with toggle
   - PHANTAST (OUTPUT) - orange badge at bottom
   
4. **Run Pipeline Button** at bottom

## Changes Required

### File: src/ui/pipeline_view.py

Update `create_left_panel()` to:
1. Add project header with title and status dot
2. Style the "PIPELINE STACK" label correctly
3. Style the Add button with green color and rounded corners
4. Add proper spacing between sections

### Code Changes

```python
def create_left_panel(self):
    panel = QFrame()
    panel.setMinimumWidth(280)
    panel.setObjectName("leftPanel")

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(0)

    # Project Header (matches design)
    project_header = QFrame()
    project_header_layout = QVBoxLayout(project_header)
    project_header_layout.setContentsMargins(0, 0, 0, 12)
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
    layout.addSpacing(16)

    # Pipeline Stack Header
    header_layout = QHBoxLayout()
    header = QLabel("PIPELINE STACK")
    header.setStyleSheet("""
        color: #9AA0A6; 
        font-size: 10px; 
        font-weight: 600; 
        letter-spacing: 1px;
    """)

    add_btn = QPushButton("Add")
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

    # Menu for Add Button
    self.add_menu = QMenu(self)
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

    for node in self.available_nodes:
        action = self.add_menu.addAction(node.get("name"))
        action.setData(node.get("type"))

    add_btn.setMenu(self.add_menu)
    self.add_menu.triggered.connect(
        lambda action: self.add_step.emit(action.data())
    )

    header_layout.addWidget(header)
    header_layout.addStretch()
    header_layout.addWidget(add_btn)
    layout.addLayout(header_layout)
    layout.addSpacing(12)

    # Rest of the method (nodes list, run button) remains the same...
```

## QA
Run `python src/main.py` and verify:
- [ ] Left sidebar shows "Untitled Project" with yellow dot
- [ ] Shows "Draft - Unsaved" subtitle
- [ ] "PIPELINE STACK" label is uppercase and muted
- [ ] Add button is green with rounded corners
- [ ] Clicking Add shows popup menu with CLAHE, Grayscale, Crop
- [ ] Selecting a step adds it to the node list
