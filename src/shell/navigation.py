from PyQt6.QtWidgets import QStackedWidget, QDockWidget
from PyQt6.QtCore import QObject, pyqtSignal

class NavigationManager(QObject):
    """
    Manages navigation between different application modes (e.g., Image Analysis, Batch).
    Controls the visible central widget and the state of dock widgets.
    """
    mode_changed = pyqtSignal(str)

    def __init__(self, central_stack: QStackedWidget, docks: dict):
        super().__init__()
        self.central_stack = central_stack
        self.docks = docks  # Dict mapping dock names to QDockWidget instances
        self.modes = {}     # Dict mapping mode names to widget indices in stack

    def register_mode(self, name: str, widget, visible_docks: list = None):
        """
        Registers a new mode with a central widget and a list of docks that should be visible.
        """
        index = self.central_stack.addWidget(widget)
        self.modes[name] = {
            "index": index,
            "docks": visible_docks if visible_docks is not None else []
        }

    def switch_to(self, mode_name: str):
        """
        Switches the application state to the specified mode.
        """
        if mode_name not in self.modes:
            print(f"Error: Mode '{mode_name}' not registered.")
            return

        mode_info = self.modes[mode_name]
        
        # Switch central widget
        self.central_stack.setCurrentIndex(mode_info["index"])
        
        # Update dock visibility
        required_docks = set(mode_info["docks"])
        for dock_name, dock in self.docks.items():
            if dock_name in required_docks:
                dock.show()
            else:
                dock.hide()

        self.mode_changed.emit(mode_name)
