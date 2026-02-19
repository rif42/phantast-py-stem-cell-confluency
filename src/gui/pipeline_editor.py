
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QComboBox, QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, 
    QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal

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
        
        # Add Step Controls
        add_layout = QHBoxLayout()
        self.step_combo = QComboBox()
        self.step_combo.addItems([
            "Grayscale",
            "Gaussian Blur",
            "CLAHE",
            "PHANTAST Confluency"
        ])
        add_btn = QPushButton("Add Step")
        add_btn.clicked.connect(self.add_step)
        add_layout.addWidget(self.step_combo)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)

        # Step List
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)

        # Step Actions (Move Up/Down, Remove)
        action_layout = QHBoxLayout()
        
        up_btn = QPushButton("Up")
        up_btn.clicked.connect(self.move_up)
        action_layout.addWidget(up_btn)
        
        down_btn = QPushButton("Down")
        down_btn.clicked.connect(self.move_down)
        action_layout.addWidget(down_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_step)
        action_layout.addWidget(remove_btn)
        
        layout.addLayout(action_layout)

        self.refresh_list()

    def add_step(self):
        step_name = self.step_combo.currentText()
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
        for step in self.pipeline.steps:
            item = QListWidgetItem(step.name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
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
        self.layout = QFormLayout(self)
        self.layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

    def set_step(self, step: PipelineStep):
        self.current_step = step
        # Clear existing controls
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if step is None:
            self.layout.addRow(QLabel("No step selected"))
            return

        # Add Name Label
        name_label = QLabel(step.name)
        font = name_label.font()
        font.setBold(True)
        name_label.setFont(font)
        self.layout.addRow("Step Type:", name_label)

        # Add controls for each parameter
        for param in step.define_params():
            current_val = step.get_param(param.name)
            
            if param.type == 'int':
                spin = QSpinBox()
                if param.min is not None: spin.setMinimum(param.min)
                if param.max is not None: spin.setMaximum(param.max)
                spin.setValue(int(current_val))
                spin.valueChanged.connect(lambda val, n=param.name: self.update_param(n, val))
                self.layout.addRow(param.name, spin)
            
            elif param.type == 'float':
                spin = QDoubleSpinBox()
                if param.min is not None: spin.setMinimum(param.min)
                if param.max is not None: spin.setMaximum(param.max)
                spin.setSingleStep(0.1)
                spin.setValue(float(current_val))
                spin.valueChanged.connect(lambda val, n=param.name: self.update_param(n, val))
                self.layout.addRow(param.name, spin)
            
            elif param.type == 'bool':
                chk = QCheckBox()
                chk.setChecked(bool(current_val))
                chk.stateChanged.connect(lambda state, n=param.name: self.update_param(n, state == Qt.CheckState.Checked.value))
                self.layout.addRow(param.name, chk)
                
            elif param.type == 'choice':
                # TODO: Implement choice if needed
                pass

    def update_param(self, name, value):
        if self.current_step:
            self.current_step.set_param(name, value)
            self.param_changed.emit()
