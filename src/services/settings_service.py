"""Settings service for persisting application configuration.

This module provides a QSettings-based implementation of the SettingsInterface.
It belongs in the services/ layer since it depends on PyQt6.
"""

from typing import Any, Dict, Optional
from PyQt6.QtCore import QSettings

from src.models.settings_interface import SettingsInterface


class SettingsService(SettingsInterface):
    """QSettings-based implementation of settings persistence.

    This class manages persistent application settings using Qt's QSettings.
    All node parameters for CLAHE and PHANTAST are automatically persisted
    when changed, and loaded when nodes are created.
    """

    _instance: Optional["SettingsService"] = None

    def __new__(cls) -> "SettingsService":
        """Singleton pattern to ensure single settings instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the settings service."""
        if self._initialized:
            return

        self._settings = QSettings("PhantastLab", "PhantastLab")
        self._initialized = True

    def get_node_parameters(self, node_type: str) -> Dict[str, Any]:
        """Get saved parameters for a specific node type.

        Args:
            node_type: The type of node (e.g., 'clahe', 'phantast')

        Returns:
            Dictionary of parameter names and values, or empty dict if none saved
        """
        key = f"nodes/{node_type}/parameters"
        value = self._settings.value(key, {})

        # QSettings may return various types, ensure we return a dict
        if isinstance(value, dict):
            return value
        return {}

    def save_node_parameter(self, node_type: str, param_name: str, value: Any) -> None:
        """Save a single parameter value for a node type.

        Args:
            node_type: The type of node (e.g., 'clahe', 'phantast')
            param_name: Name of the parameter
            value: Value to save
        """
        # Get existing parameters
        params = self.get_node_parameters(node_type)

        # Update the specific parameter
        params[param_name] = value

        # Save back to settings
        key = f"nodes/{node_type}/parameters"
        self._settings.setValue(key, params)
        self._settings.sync()  # Ensure immediate persistence

    def save_node_parameters(self, node_type: str, parameters: Dict[str, Any]) -> None:
        """Save all parameters for a node type at once.

        Args:
            node_type: The type of node (e.g., 'clahe', 'phantast')
            parameters: Dictionary of all parameter names and values
        """
        key = f"nodes/{node_type}/parameters"
        self._settings.setValue(key, parameters)
        self._settings.sync()  # Ensure immediate persistence

    def clear_node_parameters(self, node_type: str) -> None:
        """Clear saved parameters for a specific node type.

        Args:
            node_type: The type of node to clear parameters for
        """
        key = f"nodes/{node_type}/parameters"
        self._settings.remove(key)
        self._settings.sync()

    def get_all_node_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get all saved node parameters.

        Returns:
            Dictionary mapping node types to their parameter dictionaries
        """
        result = {}
        self._settings.beginGroup("nodes")
        for node_type in self._settings.childGroups():
            self._settings.beginGroup(node_type)
            params = self._settings.value("parameters", {})
            if isinstance(params, dict):
                result[node_type] = params
            self._settings.endGroup()
        self._settings.endGroup()
        return result


# Global singleton instance
_settings_service: Optional[SettingsService] = None


def get_settings_service() -> SettingsService:
    """Get the global settings service instance.

    Returns:
        The singleton SettingsService instance
    """
    global _settings_service
    if _settings_service is None:
        _settings_service = SettingsService()
    return _settings_service


def initialize_settings_interface() -> None:
    """Initialize the global settings interface.

    This should be called once during application startup.
    """
    from src.models.settings_interface import set_settings_interface

    set_settings_interface(get_settings_service())
