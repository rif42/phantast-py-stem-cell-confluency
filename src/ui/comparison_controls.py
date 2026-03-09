"""Comparison controls for original/processed and mask overlay toggles."""

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class ComparisonControls(QWidget):
    """Widget with toggle buttons for before/after comparison and mask overlay."""

    view_mode_changed = pyqtSignal(str)  # 'original' or 'processed'
    mask_visibility_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._mask_available = False
        self._current_mode = "processed"
        self._mask_visible = False
        self._setup_ui()
        self.hide()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        self.view_toggle = QPushButton("Original | Processed", parent=self)
        self.view_toggle.setCheckable(True)
        self.view_toggle.setChecked(True)
        self.view_toggle.toggled.connect(self._on_view_toggled)
        layout.addWidget(self.view_toggle)

        layout.addStretch()

        self.mask_toggle = QPushButton("Show Mask", parent=self)
        self.mask_toggle.setCheckable(True)
        self.mask_toggle.setEnabled(False)
        self.mask_toggle.toggled.connect(self._on_mask_toggled)
        layout.addWidget(self.mask_toggle)

        self.setStyleSheet(
            """
            ComparisonControls {
                background-color: #1a1d21;
                border: 1px solid #2a2e33;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #2d3336;
                color: #e8eaed;
                border: 1px solid #3a3f44;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                border-color: #00b884;
            }
            QPushButton:checked {
                background-color: #00b884;
                border-color: #00d69a;
                color: #121415;
            }
            QPushButton:disabled {
                background-color: #22272a;
                border-color: #2a2e33;
                color: #6b7280;
            }
            """
        )

    @pyqtSlot(bool)
    def _on_view_toggled(self, checked: bool):
        """Handle Original/Processed toggle."""
        mode = "processed" if checked else "original"
        self._current_mode = mode
        self.view_mode_changed.emit(mode)

    @pyqtSlot(bool)
    def _on_mask_toggled(self, checked: bool):
        """Handle Show Mask toggle."""
        self._mask_visible = checked
        self.mask_visibility_changed.emit(checked)

    def set_mask_available(self, available: bool):
        """Enable/disable mask toggle based on availability."""
        self._mask_available = available
        self.mask_toggle.setEnabled(available)
        if not available:
            was_blocked = self.mask_toggle.blockSignals(True)
            self.mask_toggle.setChecked(False)
            self.mask_toggle.blockSignals(was_blocked)
            self._mask_visible = False

    def set_view_mode(self, mode: str):
        """Set view mode externally ('original' or 'processed')."""
        if mode not in ("original", "processed"):
            return
        self._current_mode = mode
        was_blocked = self.view_toggle.blockSignals(True)
        self.view_toggle.setChecked(mode == "processed")
        self.view_toggle.blockSignals(was_blocked)

    def reset(self):
        """Reset to default state and hide."""
        self._mask_available = False
        self._current_mode = "processed"
        self._mask_visible = False

        view_blocked = self.view_toggle.blockSignals(True)
        mask_blocked = self.mask_toggle.blockSignals(True)
        self.view_toggle.setChecked(True)
        self.mask_toggle.setChecked(False)
        self.mask_toggle.setEnabled(False)
        self.view_toggle.blockSignals(view_blocked)
        self.mask_toggle.blockSignals(mask_blocked)

        self.hide()
