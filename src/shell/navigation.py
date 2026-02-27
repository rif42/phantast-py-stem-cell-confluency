class NavigationManager:
    """
    Manages switching between different central views or modes
    in the application if needed (e.g., Analysis vs Batch mode).
    """
    def __init__(self, stacked_widget, dock_widgets=None):
        self.stacked_widget = stacked_widget
        self.dock_widgets = dock_widgets or {}
        self.modes = {}

    def register_mode(self, mode_name, widget, visible_docks):
        """
        Register a new mode with its central widget and a list
        of dock widget names that should be visible in this mode.
        """
        index = self.stacked_widget.addWidget(widget)
        self.modes[mode_name] = {
            "index": index,
            "visible_docks": visible_docks
        }

    def switch_to(self, mode_name):
        """Switch to a registered mode."""
        if mode_name in self.modes:
            mode_data = self.modes[mode_name]
            self.stacked_widget.setCurrentIndex(mode_data["index"])
            
            # Show/Hide docks based on mode
            for name, dock in self.dock_widgets.items():
                if name in mode_data["visible_docks"]:
                    dock.show()
                else:
                    dock.hide()
