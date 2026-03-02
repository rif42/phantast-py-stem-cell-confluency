
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QComboBox, QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, 
    QFormLayout, QGroupBox, QStackedWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon

from ..core.pipeline import ImagePipeline
from ..core.steps import PipelineStep, GrayscaleStep, GaussianBlurStep, ClaheStep, PhantastStep

class PipelineEditorWidget(QWidget):
    """
    Widget to manage the list of pipeline steps.
    """
    step_selected = pyqtSignal(object) # Emits the selected PipelineStep
    pipeline_changed = pyqtSignal()   # Emits when the pipeline structure changes

    def __init__(self, pipeline: ImagePipeline, parent=None):
        super().__init__(parent)
        self.pipeline = pipeline
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- Project Header ---
        project_header = QWidget()
        ph_layout = QVBoxLayout(project_header)
        ph_layout.setContentsMargins(16, 16, 16, 16)
        ph_layout.setSpacing(4)
        
        proj_title = QLabel("Untitled Project")
        proj_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        
        proj_status = QLabel("● Draft - Unsaved")
        proj_status.setStyleSheet("font-size: 11px; color: #D4AF37;") # Gold color for draft dot
        
        ph_layout.addWidget(proj_title)
        ph_layout.addWidget(proj_status)
        layout.addWidget(project_header)
        
        # Separator line
        sep1 = QWidget()
        sep1.setFixedHeight(1)
        sep1.setStyleSheet("background-color: #2A3331;")
        layout.addWidget(sep1)

        # --- Pipeline Stack Header ---
        stack_header = QWidget()
        sh_layout = QHBoxLayout(stack_header)
        sh_layout.setContentsMargins(16, 12, 16, 12)
        
        stack_title = QLabel("❖ PIPELINE STACK")
        stack_title.setProperty("class", "section-header")
        
        add_btn = QPushButton("⊕")
        add_btn.setFixedSize(24, 24)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #889996;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover { color: #FFFFFF; }
        """)
        add_btn.setToolTip("Add new step (Placeholder)")
        # In a real app, this would open a popup menu of steps.
        # For now we'll just add a default step to test.
        add_btn.clicked.connect(lambda: self.add_step_by_name("Gaussian Blur"))
        
        sh_layout.addWidget(stack_title)
        sh_layout.addStretch()
        sh_layout.addWidget(add_btn)
        layout.addWidget(stack_header)

        # --- Main Content Area (Stack for List vs Empty State) ---
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack)
        
        # 1. Empty State
        self.empty_state_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_state_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Dashed container styling would usually require a custom paint event or complex QSS. 
        # For simplicity, we create a container with a border.
        empty_container = QWidget()
        empty_container.setStyleSheet("""
            QWidget {
                border: 1px dashed #2A3331;
                border-radius: 8px;
                background-color: transparent;
            }
        """)
        ec_layout = QVBoxLayout(empty_container)
        ec_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ec_layout.setContentsMargins(20, 40, 20, 40)
        
        icon_lbl = QLabel("≣+")
        icon_lbl.setStyleSheet("font-size: 24px; color: #889996; background-color: #232B29; border-radius: 20px; padding: 8px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFixedSize(40, 40)
        
        empty_title = QLabel("No active steps")
        empty_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #889996; border: none;")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_desc = QLabel("Import an image to begin building your\nprocessing pipeline.")
        empty_desc.setStyleSheet("font-size: 11px; color: #556663; border: none;")
        empty_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ec_layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        ec_layout.addSpacing(16)
        ec_layout.addWidget(empty_title)
        ec_layout.addSpacing(4)
        ec_layout.addWidget(empty_desc)
        
        empty_layout.addWidget(empty_container)
        self.content_stack.addWidget(self.empty_state_widget)

        # 2. List State
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.on_selection_changed)
        # We also need to add the Move/Remove buttons here optionally, or they can be row actions.
        list_container = QWidget()
        lc_layout = QVBoxLayout(list_container)
        lc_layout.setContentsMargins(16, 0, 16, 0)
        lc_layout.addWidget(self.list_widget)
        
        # Temporary Action Buttons (Usually you'd want these on hover per item)
        action_layout = QHBoxLayout()
        up_btn = QPushButton("Up")
        up_btn.clicked.connect(self.move_up)
        down_btn = QPushButton("Down")
        down_btn.clicked.connect(self.move_down)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_step)
        action_layout.addWidget(up_btn)
        action_layout.addWidget(down_btn)
        action_layout.addWidget(remove_btn)
        lc_layout.addLayout(action_layout)
        
        self.content_stack.addWidget(list_container)
        
        # Spacer
        layout.addStretch()
        
        # --- Session Log Header ---
        sep2 = QWidget()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background-color: #2A3331;")
        layout.addWidget(sep2)
        
        log_header = QWidget()
        lh_layout = QVBoxLayout(log_header)
        lh_layout.setContentsMargins(16, 12, 16, 12)
        
        log_title = QLabel("◷ SESSION LOG")
        log_title.setProperty("class", "section-header")
        
        log_text1 = QLabel("> System initialized")
        log_text1.setStyleSheet("font-family: 'Cascadia Code', monospace; font-size: 10px; color: #556663;")
        log_text2 = QLabel("> Workspace ready")
        log_text2.setStyleSheet("font-family: 'Cascadia Code', monospace; font-size: 10px; color: #556663;")
        log_text3 = QLabel("> Awaiting input...")
        log_text3.setStyleSheet("font-family: 'Cascadia Code', monospace; font-size: 10px; color: #334441;")
        
        lh_layout.addWidget(log_title)
        lh_layout.addSpacing(8)
        lh_layout.addWidget(log_text1)
        lh_layout.addWidget(log_text2)
        lh_layout.addWidget(log_text3)
        layout.addWidget(log_header)

        self.refresh_list()

    def add_step_by_name(self, step_name):
        step = None
        if step_name == "Grayscale":
            step = GrayscaleStep()
        elif step_name == "Gaussian Blur":
            step = GaussianBlurStep()
        elif step_name == "CLAHE":
            step = ClaheStep()
        elif step_name == "PHANTAST Confluency":
            step = PhantastStep()
            
        if step:
            self.pipeline.add_step(step)
            self.refresh_list()
            self.pipeline_changed.emit()
            # Select the new step
            self.list_widget.setCurrentRow(len(self.pipeline.steps) - 1)

    def remove_step(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.pipeline.remove_step(row)
            self.refresh_list()
            self.pipeline_changed.emit()

    def move_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            self.pipeline.move_step(row, row - 1)
            self.refresh_list()
            self.list_widget.setCurrentRow(row - 1)
            self.pipeline_changed.emit()

    def move_down(self):
        row = self.list_widget.currentRow()
        if row >= 0 and row < len(self.pipeline.steps) - 1:
            self.pipeline.move_step(row, row + 1)
            self.refresh_list()
            self.list_widget.setCurrentRow(row + 1)
            self.pipeline_changed.emit()

    def refresh_list(self):
        self.list_widget.clear()
        if not self.pipeline.steps:
            self.content_stack.setCurrentIndex(0) # Empty state
            return
            
        self.content_stack.setCurrentIndex(1) # List state
        for step in self.pipeline.steps:
            item = QListWidgetItem(step.name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            item.setCheckState(Qt.CheckState.Checked if step.enabled else Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)
    
    def on_selection_changed(self, row):
        if row >= 0:
            step = self.pipeline.steps[row]
            self.step_selected.emit(step)
        else:
            self.step_selected.emit(None)

    # Handle check state changes for enabling/disabling steps
    # QListWidget doesn't emit a specific signal for check state change easily without subclassing or using itemChanged
    # We can connect itemChanged
    def on_item_changed(self, item):
        row = self.list_widget.row(item)
        if row >= 0:
            step = self.pipeline.steps[row]
            step.enabled = (item.checkState() == Qt.CheckState.Checked)
            self.pipeline_changed.emit()

    def setup_connections(self):
        # Call this after init to avoid recursion during initial population if needed
        self.list_widget.itemChanged.connect(self.on_item_changed)


class StepConfigWidget(QWidget):
    """
    Widget to edit parameters of a selected pipeline step.
    """
    param_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = None
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Properties Header ---
        prop_header = QWidget()
        ph_layout = QHBoxLayout(prop_header)
        ph_layout.setContentsMargins(16, 16, 16, 16)
        
        prop_title = QLabel("☷ PROPERTIES")
        prop_title.setProperty("class", "section-header")
        
        ph_layout.addWidget(prop_title)
        ph_layout.addStretch()
        main_layout.addWidget(prop_header)
        
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #2A3331;")
        main_layout.addWidget(sep)
        
        # --- Content Stack ---
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)
        
        # 1. Empty State
        self.empty_state_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_state_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_lbl = QLabel("ılı")
        icon_lbl.setStyleSheet("font-size: 24px; color: #889996; background-color: #232B29; border-radius: 20px; padding: 8px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFixedSize(40, 40)
        
        empty_title = QLabel("No Selection")
        empty_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #889996;")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_desc = QLabel("Select an element or import an image to\nview properties.")
        empty_desc.setStyleSheet("font-size: 11px; color: #556663;")
        empty_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_layout.addStretch()
        empty_layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        empty_layout.addSpacing(16)
        empty_layout.addWidget(empty_title)
        empty_layout.addSpacing(4)
        empty_layout.addWidget(empty_desc)
        empty_layout.addStretch()
        
        self.content_stack.addWidget(self.empty_state_widget)
        
        # 2. Form State
        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)
        self.form_layout.setContentsMargins(16, 16, 16, 16)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.content_stack.addWidget(self.form_widget)

    def set_step(self, step: PipelineStep):
        self.current_step = step
        # Clear existing controls
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if step is None:
            self.content_stack.setCurrentIndex(0)
            return

        self.content_stack.setCurrentIndex(1)

        # Add Name Label
        name_label = QLabel(step.name)
        font = name_label.font()
        font.setBold(True)
        name_label.setFont(font)
        self.form_layout.addRow("Step Type:", name_label)

        # Add controls for each parameter
        for param in step.define_params():
            current_val = step.get_param(param.name)
            
            if param.type == 'int':
                spin = QSpinBox()
                if param.min is not None: spin.setMinimum(param.min)
                if param.max is not None: spin.setMaximum(param.max)
                spin.setValue(int(current_val))
                spin.valueChanged.connect(lambda val, n=param.name: self.update_param(n, val))
                self.form_layout.addRow(param.name, spin)
            
            elif param.type == 'float':
                spin = QDoubleSpinBox()
                if param.min is not None: spin.setMinimum(param.min)
                if param.max is not None: spin.setMaximum(param.max)
                spin.setSingleStep(0.1)
                spin.setValue(float(current_val))
                spin.valueChanged.connect(lambda val, n=param.name: self.update_param(n, val))
                self.form_layout.addRow(param.name, spin)
            
            elif param.type == 'bool':
                chk = QCheckBox()
                chk.setChecked(bool(current_val))
                chk.stateChanged.connect(lambda state, n=param.name: self.update_param(n, state == Qt.CheckState.Checked.value))
                self.form_layout.addRow(param.name, chk)
                
            elif param.type == 'choice':
                # TODO: Implement choice if needed
                pass

    def update_param(self, name, value):
        if self.current_step:
            self.current_step.set_param(name, value)
            self.param_changed.emit()
