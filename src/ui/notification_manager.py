"""Notification manager for non-blocking toast notifications.

This module provides inline toast notifications that replace modal
QMessageBox dialogs, maintaining the single-page application architecture.
"""

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtGui import QColor, QPainter, QFont


class NotificationWidget(QWidget):
    """Individual toast notification widget."""

    # Color schemes for different notification types
    COLORS = {
        "info": {
            "bg": "#1a1d21",
            "border": "#2a2e33",
            "text": "#E8EAED",
            "accent": "#00B884",
        },
        "warning": {
            "bg": "#2a2a1a",
            "border": "#4a4a2a",
            "text": "#E8EAED",
            "accent": "#f59e0b",
        },
        "error": {
            "bg": "#2a1a1a",
            "border": "#4a2a2a",
            "text": "#E8EAED",
            "accent": "#ef4444",
        },
        "success": {
            "bg": "#1a2a1a",
            "border": "#2a4a2a",
            "text": "#E8EAED",
            "accent": "#22c55e",
        },
    }

    ICONS = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅",
    }

    def __init__(self, message: str, notification_type: str = "info", parent=None):
        """Initialize notification widget.

        Args:
            message: The notification message to display
            notification_type: One of 'info', 'warning', 'error', 'success'
            parent: Parent widget (typically the main window)
        """
        super().__init__(parent=parent)

        self.notification_type = notification_type
        self.colors = self.COLORS.get(notification_type, self.COLORS["info"])

        # Setup widget
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Size and styling
        self.setFixedWidth(320)
        self.setMinimumHeight(60)

        self._setup_ui(message)
        self._setup_animation()

        # Auto-hide timer
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide_notification)

    def _setup_ui(self, message: str):
        """Set up the notification UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Icon and message in horizontal layout would be better
        # For simplicity, using stacked layout
        icon_label = QLabel(self.ICONS.get(self.notification_type, "ℹ️"), parent=self)
        icon_label.setStyleSheet(f"font-size: 20px; background: transparent;")
        layout.addWidget(icon_label)

        # Message label
        self.message_label = QLabel(message, parent=self)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet(f"""
            color: {self.colors["text"]};
            font-size: 13px;
            background: transparent;
            font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
        """)
        layout.addWidget(self.message_label)

        # Apply background styling
        self.setStyleSheet(f"""
            NotificationWidget {{
                background-color: {self.colors["bg"]};
                border: 1px solid {self.colors["border"]};
                border-left: 4px solid {self.colors["accent"]};
                border-radius: 8px;
            }}
        """)

    def _setup_animation(self):
        """Setup fade animation."""
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_in.setDuration(200)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_out.setDuration(200)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out.finished.connect(self.close)

    def show_notification(self, duration_ms: int = 5000):
        """Show the notification with fade-in and auto-hide.

        Args:
            duration_ms: How long to show the notification (default 5 seconds)
        """
        self.show()
        self._fade_in.start()
        self._hide_timer.start(duration_ms)

    def hide_notification(self):
        """Hide the notification with fade-out."""
        self._fade_out.start()

    def paintEvent(self, event):
        """Custom paint for rounded corners and border."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor(self.colors["bg"]))

        # Draw border
        painter.setPen(QColor(self.colors["border"]))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 8, 8)

        # Draw accent line on left
        painter.setPen(QColor(self.colors["accent"]))
        painter.setBrush(QColor(self.colors["accent"]))
        painter.drawRect(0, 0, 4, self.height())

        super().paintEvent(event)


class NotificationManager:
    """Manager for displaying toast notifications.

    This is a singleton that manages a queue of notifications
    and displays them in a stack layout.
    """

    _instance: "NotificationManager" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._parent: QWidget = None
        self._notifications: list[NotificationWidget] = []
        self._max_notifications = 3

    def set_parent(self, parent: QWidget):
        """Set the parent widget for notifications.

        Should be called once during application initialization.
        """
        self._parent = parent

    def _get_parent(self) -> QWidget:
        """Get the parent widget, raising if not set."""
        if self._parent is None:
            raise RuntimeError(
                "NotificationManager parent not set. Call set_parent() first."
            )
        return self._parent

    def _position_notification(self, notification: NotificationWidget, index: int):
        """Position notification in the stack."""
        parent = self._get_parent()

        # Position from top-right with offset
        margin = 20
        x = parent.width() - notification.width() - margin
        y = margin + (index * (notification.height() + 10))

        notification.move(x, y)

    def _cleanup_notification(self, notification: NotificationWidget):
        """Remove notification from tracking and reposition others."""
        if notification in self._notifications:
            self._notifications.remove(notification)
            notification.deleteLater()

            # Reposition remaining notifications
            for i, notif in enumerate(self._notifications):
                self._position_notification(notif, i)

    def show_info(self, message: str, duration_ms: int = 5000):
        """Show an info notification."""
        self._show_notification(message, "info", duration_ms)

    def show_warning(self, message: str, duration_ms: int = 5000):
        """Show a warning notification."""
        self._show_notification(message, "warning", duration_ms)

    def show_error(self, message: str, duration_ms: int = 8000):
        """Show an error notification (longer duration)."""
        self._show_notification(message, "error", duration_ms)

    def show_success(self, message: str, duration_ms: int = 3000):
        """Show a success notification."""
        self._show_notification(message, "success", duration_ms)

    def _show_notification(
        self, message: str, notification_type: str, duration_ms: int
    ):
        """Create and show a notification."""
        # Remove oldest if at max
        if len(self._notifications) >= self._max_notifications:
            oldest = self._notifications[0]
            oldest.hide_notification()
            self._cleanup_notification(oldest)

        # Create new notification
        parent = self._get_parent()
        notification = NotificationWidget(message, notification_type, parent=parent)

        # Position and show
        index = len(self._notifications)
        self._position_notification(notification, index)
        notification.show_notification(duration_ms)

        # Track it
        self._notifications.append(notification)

        # Connect cleanup
        notification._fade_out.finished.connect(
            lambda: self._cleanup_notification(notification)
        )


# Global singleton instance
_notification_manager: NotificationManager = None


def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


def initialize_notifications(parent: QWidget) -> None:
    """Initialize the notification system with a parent widget.

    Should be called once during application startup.
    """
    get_notification_manager().set_parent(parent)


def show_info(message: str, duration_ms: int = 5000):
    """Show an info notification."""
    get_notification_manager().show_info(message, duration_ms)


def show_warning(message: str, duration_ms: int = 5000):
    """Show a warning notification."""
    get_notification_manager().show_warning(message, duration_ms)


def show_error(message: str, duration_ms: int = 8000):
    """Show an error notification."""
    get_notification_manager().show_error(message, duration_ms)


def show_success(message: str, duration_ms: int = 3000):
    """Show a success notification."""
    get_notification_manager().show_success(message, duration_ms)
