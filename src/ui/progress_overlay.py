"""Progress overlay widget for non-blocking processing indication.

This module provides an inline progress overlay that replaces modal
ProcessingDialog, maintaining the single-page application architecture.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtGui import QColor


class ProgressOverlay(QWidget):
    """Non-modal progress overlay for pipeline processing.

    Unlike ProcessingDialog (QDialog), this widget is embedded in the
    canvas area and doesn't block user interaction with the main window.
    """

    def __init__(self, parent=None):
        """Initialize progress overlay.

        Args:
            parent: Parent widget (typically the canvas container)
        """
        super().__init__(parent=parent)

        # Make it an overlay that fills parent
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAutoFillBackground(True)

        # Semi-transparent dark background
        palette = self.palette()
        palette.setColor(
            self.backgroundRole(), QColor(18, 20, 21, 230)
        )  # BG_DARK with alpha
        self.setPalette(palette)

        # Initial state: hidden
        self.hide()

        self._setup_ui()
        self._spinner_timer = None
        self._spinner_index = 0
        self._spinner_frames = ["◐", "◓", "◑", "◒"]

    def _setup_ui(self):
        """Set up the overlay UI components."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Spinner label
        self.spinner_label = QLabel(self._spinner_frames[0], parent=self)
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label.setStyleSheet("""
            font-size: 48px;
            color: #00B884;
            background: transparent;
        """)
        layout.addWidget(self.spinner_label)

        # Status text
        self.status_label = QLabel("Processing...", parent=self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 16px;
            color: #E8EAED;
            background: transparent;
        """)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar(parent=self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2a2e33;
                border-radius: 4px;
                text-align: center;
                color: #E8EAED;
                background: #1a1d21;
                min-width: 200px;
                max-width: 300px;
            }
            QProgressBar::chunk {
                background-color: #00B884;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Cancel button
        self.cancel_button = QPushButton("Cancel", parent=self)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background: #2a2e33;
                border: 1px solid #3a3e43;
                border-radius: 4px;
                color: #E8EAED;
                padding: 8px 16px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #3a3e43;
                border-color: #00B884;
            }
        """)
        self.cancel_button.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def _on_cancel(self):
        """Handle cancel button click."""
        self.cancelled.emit()
        self.hide()

    def show_progress(self, message: str = "Processing...", percent: int = 0):
        """Show the overlay and start progress indication.

        Args:
            message: Status message to display
            percent: Progress percentage (0-100)
        """
        self.status_label.setText(message)
        self.progress_bar.setValue(percent)

        if not self.isVisible():
            self.show()
            self._start_spinner()

    def update_progress(self, message: str, percent: int):
        """Update progress status.

        Args:
            message: New status message
            percent: New progress percentage (0-100)
        """
        self.status_label.setText(message)
        self.progress_bar.setValue(percent)

    def hide_progress(self):
        """Hide the overlay and stop spinner."""
        self._stop_spinner()
        self.hide()

    def _start_spinner(self):
        """Start the spinner animation."""
        if self._spinner_timer is None:
            self._spinner_timer = QTimer(self)
            self._spinner_timer.timeout.connect(self._update_spinner)
        self._spinner_timer.start(100)  # Update every 100ms

    def _stop_spinner(self):
        """Stop the spinner animation."""
        if self._spinner_timer is not None:
            self._spinner_timer.stop()
        self._spinner_index = 0
        self.spinner_label.setText(self._spinner_frames[0])

    def _update_spinner(self):
        """Update spinner frame."""
        self._spinner_index = (self._spinner_index + 1) % len(self._spinner_frames)
        self.spinner_label.setText(self._spinner_frames[self._spinner_index])

    def resizeEvent(self, event):
        """Ensure overlay fills parent on resize."""
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())

    # Signal for cancel button
    cancelled = property(lambda self: self._cancelled_signal)


# Add pyqtSignal to the class
from PyQt6.QtCore import pyqtSignal

ProgressOverlay._cancelled_signal = pyqtSignal()
ProgressOverlay.cancelled = property(lambda self: self._cancelled_signal)
