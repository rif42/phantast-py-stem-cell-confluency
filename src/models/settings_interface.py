"""Settings interface for persistent application configuration.

This module provides abstract interfaces for settings management,
allowing models/ to remain pure Python without PyQt dependencies.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Protocol


class SettingsInterface(Protocol):
    """Protocol for settings persistence.

    Implementations may use QSettings, JSON files, or other backends.
    """

    def get_node_parameters(self, node_type: str) -> Dict[str, Any]:
        """Get saved parameters for a specific node type."""
        ...

    def save_node_parameter(self, node_type: str, param_name: str, value: Any) -> None:
        """Save a single parameter value for a node type."""
        ...

    def save_node_parameters(self, node_type: str, parameters: Dict[str, Any]) -> None:
        """Save all parameters for a node type at once."""
        ...

    def clear_node_parameters(self, node_type: str) -> None:
        """Clear saved parameters for a specific node type."""
        ...

    def get_all_node_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get all saved node parameters."""
        ...


# Global settings interface instance (set by application)
_settings_interface: SettingsInterface | None = None


def set_settings_interface(interface: SettingsInterface) -> None:
    """Set the global settings interface.

    This should be called once during application initialization.
    """
    global _settings_interface
    _settings_interface = interface


def get_settings_interface() -> SettingsInterface:
    """Get the global settings interface.

    Raises:
        RuntimeError: If settings interface has not been set.
    """
    if _settings_interface is None:
        raise RuntimeError(
            "Settings interface not initialized. Call set_settings_interface() first."
        )
    return _settings_interface


def get_node_parameters(node_type: str) -> Dict[str, Any]:
    """Convenience function to get saved parameters for a node type."""
    return get_settings_interface().get_node_parameters(node_type)


def save_node_parameter(node_type: str, param_name: str, value: Any) -> None:
    """Convenience function to save a single parameter value."""
    get_settings_interface().save_node_parameter(node_type, param_name, value)
