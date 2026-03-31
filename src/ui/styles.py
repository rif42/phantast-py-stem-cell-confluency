"""
Global Stylesheet System for Phantast Lab

This module provides a centralized, component-based stylesheet system similar to React's
styled-components. All design tokens and component styles are defined here for consistency
across the entire application.

Usage:
    from src.ui.styles import Styles, Theme

    # Apply global stylesheet to QApplication
    app.setStyleSheet(Styles.get_global_stylesheet())

    # Use design tokens in code
    widget.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")

Architecture:
    - Theme: Design tokens (colors, typography, spacing)
    - ComponentStyles: Reusable component style generators
    - Styles: Global stylesheet combiner and manager
"""

from typing import Optional


class Theme:
    """
    Design tokens - Single source of truth for all visual values.

    All colors, fonts, and spacing values are defined here and referenced
    throughout the application. Changing a value here updates it everywhere.
    """

    # Primary Colors
    PRIMARY = "#00B884"  # Emerald green - main accent
    PRIMARY_HOVER = "#00C890"  # Lighter green for hover states
    PRIMARY_LIGHT = "rgba(0, 184, 132, 0.15)"  # For checked/selected backgrounds

    # Secondary Colors
    SECONDARY = "#E8A317"  # Amber/Yellow - secondary accent

    # Semantic Colors
    INFO = "#0078D4"  # Blue - input nodes, info states
    SUCCESS = "#00B884"  # Green - success states (same as primary)
    WARNING = "#E8A317"  # Yellow/amber - warnings (same as secondary)

    # Background Colors
    BG_DARK = "#121415"  # Main background (sidebars, panels)
    BG_DARKER = "#0d0f10"  # Canvas area - even darker
    BG_CARD = "#1E2224"  # Cards, toolbars, elevated surfaces
    BG_INPUT = "#121415"  # Input backgrounds (file lists)
    BG_TOOL_ACTIVE = "#2D3336"  # Active tool button background

    # Border Colors
    BORDER = "#2D3336"  # Default borders
    BORDER_LIGHT = "#3A4044"  # Lighter borders for emphasis

    # Text Colors
    TEXT_PRIMARY = "#E8EAED"  # Main text color
    TEXT_SECONDARY = "#9AA0A6"  # Secondary/muted text
    TEXT_DISABLED = "#5F6368"  # Disabled text
    TEXT_ON_PRIMARY = "#FFFFFF"  # Text on primary color background
    TEXT_ON_SECONDARY = "#121415"  # Text on secondary color background (dark)

    # Typography
    FONT_FAMILY = '"Inter", "Segoe UI", sans-serif'
    FONT_FAMILY_MONO = '"JetBrains Mono", "Consolas", monospace'

    # Font Sizes
    FONT_SIZE_XS = "10px"  # Badges, small labels
    FONT_SIZE_SM = "11px"  # Descriptions, metadata
    FONT_SIZE_BASE = "13px"  # Body text
    FONT_SIZE_MD = "14px"  # Canvas text
    FONT_SIZE_LG = "15px"  # Titles, headers
    FONT_SIZE_XL = "16px"  # Icons, toolbar buttons
    FONT_SIZE_2XL = "20px"  # Section headers
    FONT_SIZE_3XL = "48px"  # Large icons (empty states)

    # Font Weights
    FONT_WEIGHT_NORMAL = "400"
    FONT_WEIGHT_MEDIUM = "500"
    FONT_WEIGHT_SEMIBOLD = "600"
    FONT_WEIGHT_BOLD = "700"

    # Spacing (in pixels, for use in stylesheets)
    SPACE_1 = "4px"
    SPACE_2 = "8px"
    SPACE_3 = "12px"
    SPACE_4 = "16px"
    SPACE_5 = "20px"
    SPACE_6 = "24px"

    # Border Radius
    RADIUS_SM = "4px"
    RADIUS_MD = "6px"
    RADIUS_LG = "8px"
    RADIUS_FULL = "9999px"  # For circular elements (avatars)

    # Transitions
    TRANSITION_FAST = "150ms"
    TRANSITION_BASE = "200ms"
    TRANSITION_SLOW = "300ms"


class ComponentStyles:
    """
    Reusable component style generators.

    Each method returns a QSS string for a specific component type.
    Styles are defined using Theme tokens for consistency.

    Usage in widgets:
        widget.setObjectName("primaryButton")  # Matches the selector in button_primary()
    """

    @staticmethod
    def base() -> str:
        """Base styles applied to all widgets."""
        return f"""
            QWidget {{
                background-color: {Theme.BG_DARK};
                color: {Theme.TEXT_PRIMARY};
                font-family: {Theme.FONT_FAMILY};
                font-size: {Theme.FONT_SIZE_BASE};
            }}
        """

    @staticmethod
    def main_window() -> str:
        """Main window and header styles."""
        return f"""
            QMainWindow {{
                background-color: {Theme.BG_DARK};
            }}
            
            #AppHeader {{
                background-color: {Theme.BG_DARK};
                border-bottom: 1px solid {Theme.BORDER};
            }}
            
            #appLogo {{
                font-size: 20px;
                color: {Theme.PRIMARY};
            }}
            
            #appTitle {{
                font-size: {Theme.FONT_SIZE_LG};
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                color: {Theme.TEXT_PRIMARY};
            }}
            
            #appAvatar {{
                background-color: {Theme.SECONDARY};
                border-radius: 16px;
            }}
        """

    @staticmethod
    def panels() -> str:
        """Left and right panel styles."""
        return f"""
            #leftPanel, #rightPanel {{
                background-color: {Theme.BG_DARK};
                border-left: 1px solid {Theme.BORDER};
                border-right: 1px solid {Theme.BORDER};
            }}
        """

    @staticmethod
    def canvas() -> str:
        """Canvas and image display area."""
        return f"""
            #canvasArea {{
                background-color: {Theme.BG_DARKER};
            }}
            
            #canvasImage {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_MD};
            }}
        """

    @staticmethod
    def buttons() -> str:
        """All button variants."""
        return f"""
            /* Primary Button - Main actions */
            #primaryButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.TEXT_ON_PRIMARY};
                border: none;
                border-radius: {Theme.RADIUS_SM};
                padding: 8px 16px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                font-size: {Theme.FONT_SIZE_BASE};
            }}
            
            #primaryButton:hover {{
                background-color: {Theme.PRIMARY_HOVER};
            }}
            
            /* Secondary Button - Secondary actions */
            #secondaryButton {{
                background-color: {Theme.BG_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.RADIUS_SM};
                padding: 6px 12px;
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                font-size: {Theme.FONT_SIZE_SM};
            }}
            
            #secondaryButton:checked {{
                background-color: {Theme.PRIMARY_LIGHT};
                color: {Theme.PRIMARY};
                border: 1px solid {Theme.PRIMARY};
            }}
            
            /* Toolbar Button - Icon buttons */
            #toolBtn {{
                background-color: transparent;
                color: {Theme.TEXT_SECONDARY};
                border: none;
                font-size: {Theme.FONT_SIZE_XL};
                padding: 4px;
            }}
            
            #toolBtn:hover {{
                color: {Theme.TEXT_PRIMARY};
            }}
            
            #toolBtnActive {{
                background-color: {Theme.BG_TOOL_ACTIVE};
                color: {Theme.TEXT_PRIMARY};
                border: none;
                border-radius: {Theme.RADIUS_SM};
                font-size: {Theme.FONT_SIZE_XL};
                padding: 4px;
            }}
            
            #toolBtnActive:hover {{
                background-color: {Theme.BORDER_LIGHT};
            }}
        """

    @staticmethod
    def toolbar() -> str:
        """Floating toolbar styles."""
        return f"""
            #floatingToolbar {{
                background-color: {Theme.BG_CARD};
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.RADIUS_MD};
            }}
            
            #toolLabel {{
                background-color: {Theme.BG_DARK};
                border-radius: {Theme.RADIUS_SM};
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_SM};
                font-family: {Theme.FONT_FAMILY_MONO};
                padding: 4px 0px;
            }}
        """

    @staticmethod
    def typography() -> str:
        """Text and label styles."""
        return f"""
            /* Panel Header - Section titles in sidebars */
            #panelHeader {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_SM};
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                margin-bottom: 16px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            /* Section Header - Subsection titles */
            #sectionHeader {{
                color: {Theme.TEXT_PRIMARY};
                font-size: {Theme.FONT_SIZE_BASE};
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                margin-top: 16px;
                margin-bottom: 12px;
            }}
            
            #sectionHeaderLarge {{
                font-size: {Theme.FONT_SIZE_2XL};
                font-weight: {Theme.FONT_WEIGHT_BOLD};
            }}
            
            /* Property Label - Metadata keys */
            #propertyLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_SM};
            }}
            
            /* Property Value - Metadata values */
            #propertyValue {{
                color: #FFFFFF;
                font-family: {Theme.FONT_FAMILY_MONO};
                font-size: {Theme.FONT_SIZE_SM};
            }}
            
            /* Filename Label - File names, important text */
            #filenameLabel {{
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                font-size: {Theme.FONT_SIZE_BASE};
                color: #FFFFFF;
            }}
            
            /* File Description - Secondary file info */
            #fileDesc {{
                font-size: {Theme.FONT_SIZE_SM};
                color: {Theme.TEXT_SECONDARY};
                margin-top: 2px;
            }}
            
            /* Empty Label - Placeholder text */
            #emptyLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_SM};
                line-height: 1.4;
                margin-top: 16px;
            }}
            
            /* Large Icon - Empty state icons */
            #largeIcon {{
                font-size: {Theme.FONT_SIZE_3XL};
            }}
            
            /* Standard Icon - Regular icons */
            #icon {{
                font-size: {Theme.FONT_SIZE_2XL};
            }}
        """

    @staticmethod
    def nodes() -> str:
        """Pipeline node widget styles."""
        return f"""
            /* Input Node - Blue border */
            #nodeWidget {{
                background-color: {Theme.BG_CARD};
                border: 1px solid {Theme.INFO};
                border-radius: {Theme.RADIUS_MD};
            }}
            
            /* Output Node - Yellow/Amber border */
            #nodeWidgetOutput {{
                background-color: {Theme.BG_CARD};
                border: 1px solid {Theme.SECONDARY};
                border-radius: {Theme.RADIUS_MD};
            }}
            
            /* Processing Node - Green border (for future use) */
            #nodeWidgetProcessing {{
                background-color: {Theme.BG_CARD};
                border: 1px solid {Theme.PRIMARY};
                border-radius: {Theme.RADIUS_MD};
            }}
            
            /* Input Badge */
            #badgeInput {{
                background-color: {Theme.INFO};
                color: white;
                font-size: {Theme.FONT_SIZE_XS};
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                padding: 2px 6px;
                border-radius: {Theme.RADIUS_SM};
            }}
            
            /* Output Badge */
            #badgeOutput {{
                background-color: {Theme.SECONDARY};
                color: {Theme.TEXT_ON_SECONDARY};
                font-size: {Theme.FONT_SIZE_XS};
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                padding: 2px 6px;
                border-radius: {Theme.RADIUS_SM};
            }}
            
            /* Processing Badge */
            #badgeProcessing {{
                background-color: {Theme.PRIMARY};
                color: white;
                font-size: {Theme.FONT_SIZE_XS};
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                padding: 2px 6px;
                border-radius: {Theme.RADIUS_SM};
            }}
            
            /* Arrow between nodes */
            #nodeArrow {{
                color: {Theme.BORDER};
                font-weight: {Theme.FONT_WEIGHT_BOLD};
            }}
        """

    @staticmethod
    def lists() -> str:
        """List and file browser styles."""
        return f"""
            #fileList {{
                background-color: {Theme.BG_INPUT};
                border: none;
                color: {Theme.TEXT_PRIMARY};
                outline: none;
            }}
            
            #fileList::item {{
                padding: 8px;
                border-bottom: 1px solid {Theme.BORDER};
            }}
            
            #fileList::item:selected {{
                background-color: {Theme.BG_CARD};
            }}
            
            #fileList::item:hover:!selected {{
                background-color: {Theme.BG_TOOL_ACTIVE};
            }}
        """

    @staticmethod
    def cards() -> str:
        """Card and elevated surface styles."""
        return f"""
            #fileBox {{
                background-color: {Theme.BG_CARD};
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.RADIUS_MD};
                margin-bottom: 8px;
            }}
            
            #card {{
                background-color: {Theme.BG_CARD};
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.RADIUS_MD};
            }}
            
            #cardElevated {{
                background-color: {Theme.BG_CARD};
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.RADIUS_MD};
            }}
        """

    @staticmethod
    def scrollbars() -> str:
        """Custom scrollbar styles."""
        return f"""
            QScrollBar:vertical {{
                background-color: {Theme.BG_DARK};
                width: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {Theme.BORDER};
                border-radius: 4px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {Theme.TEXT_SECONDARY};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {Theme.BG_DARK};
                height: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {Theme.BORDER};
                border-radius: 4px;
                min-width: 30px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {Theme.TEXT_SECONDARY};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            QScrollArea {{
                border: none;
                background: transparent;
            }}
        """

    @staticmethod
    def inputs() -> str:
        """Form input styles."""
        return f"""
            QLineEdit {{
                background-color: {Theme.BG_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.RADIUS_SM};
                padding: 8px 12px;
                font-size: {Theme.FONT_SIZE_BASE};
            }}
            
            QLineEdit:focus {{
                border: 1px solid {Theme.PRIMARY};
            }}
            
            QComboBox {{
                background-color: {Theme.BG_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.RADIUS_SM};
                padding: 8px 12px;
                min-width: 100px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {Theme.BG_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                selection-background-color: {Theme.BG_TOOL_ACTIVE};
            }}
            
            QSpinBox, QDoubleSpinBox {{
                background-color: {Theme.BG_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.RADIUS_SM};
                padding: 4px 8px;
            }}
            
            QSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background-color: {Theme.BORDER};
                border-radius: 2px;
            }}
            
            QSlider::handle:horizontal {{
                background-color: {Theme.PRIMARY};
                border: none;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            
            QSlider::sub-page:horizontal {{
                background-color: {Theme.PRIMARY};
                border-radius: 2px;
            }}
        """

    @staticmethod
    def dialogs() -> str:
        """Dialog and overlay styles."""
        return f"""
            QMenu {{
                background-color: {Theme.BG_CARD};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                padding: 4px;
            }}
            
            QMenu::item {{
                padding: 8px 24px;
                border-radius: {Theme.RADIUS_SM};
            }}
            
            QMenu::item:selected {{
                background-color: {Theme.BG_TOOL_ACTIVE};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {Theme.BORDER};
                margin: 4px 8px;
            }}
        """


class Styles:
    """
    Global stylesheet manager.

    Combines all component styles into a single stylesheet that can be
    applied to the QApplication. This ensures consistency across all windows.

    Usage:
        app = QApplication(sys.argv)
        app.setStyleSheet(Styles.get_global_stylesheet())
    """

    @staticmethod
    def get_global_stylesheet() -> str:
        """
        Generate the complete application stylesheet.

        Combines all component styles into one string. This is applied once
        to QApplication and affects all widgets in the application.

        Returns:
            Complete QSS stylesheet string
        """
        components = [
            ComponentStyles.base(),
            ComponentStyles.main_window(),
            ComponentStyles.panels(),
            ComponentStyles.canvas(),
            ComponentStyles.buttons(),
            ComponentStyles.toolbar(),
            ComponentStyles.typography(),
            ComponentStyles.nodes(),
            ComponentStyles.lists(),
            ComponentStyles.cards(),
            ComponentStyles.scrollbars(),
            ComponentStyles.inputs(),
            ComponentStyles.dialogs(),
        ]

        return "\n".join(components)

    @staticmethod
    def get_stylesheet_for(names: list[str]) -> str:
        """
        Get stylesheet for specific components only.

        Useful for partial updates or specific widget styling.

        Args:
            names: List of component names to include

        Returns:
            Stylesheet string for specified components

        Example:
            sheet = Styles.get_stylesheet_for(["buttons", "panels"])
        """
        component_map = {
            "base": ComponentStyles.base,
            "main_window": ComponentStyles.main_window,
            "panels": ComponentStyles.panels,
            "canvas": ComponentStyles.canvas,
            "buttons": ComponentStyles.buttons,
            "toolbar": ComponentStyles.toolbar,
            "typography": ComponentStyles.typography,
            "nodes": ComponentStyles.nodes,
            "lists": ComponentStyles.lists,
            "cards": ComponentStyles.cards,
            "scrollbars": ComponentStyles.scrollbars,
            "inputs": ComponentStyles.inputs,
            "dialogs": ComponentStyles.dialogs,
        }

        components = []
        for name in names:
            if name in component_map:
                components.append(component_map[name]())

        return "\n".join(components)


class StyleManager:
    """
    Runtime style manager for dynamic theme switching.

    Provides methods to switch themes at runtime and hot-reload styles
    during development. Optional enhancement beyond basic global stylesheet.

    Usage:
        manager = StyleManager(app)
        manager.apply_theme("dark")
        # Later...
        manager.reload_styles()  # Hot-reload during dev
    """

    def __init__(self, app):
        """
        Initialize style manager.

        Args:
            app: QApplication instance
        """
        self.app = app
        self.current_theme = "dark"

    def apply_theme(self, theme_name: str) -> None:
        """
        Apply a theme by name.

        Args:
            theme_name: Name of theme to apply ("dark", "light", etc.)
        """
        if theme_name == "dark":
            self.app.setStyleSheet(Styles.get_global_stylesheet())
            self.current_theme = "dark"
        # Future themes can be added here
        # elif theme_name == "light":
        #     self.app.setStyleSheet(LightStyles.get_global_stylesheet())

    def reload_styles(self) -> None:
        """
        Reload current theme styles.

        Useful during development when modifying styles.py.
        Call this to see style changes without restarting the app.
        """
        self.apply_theme(self.current_theme)

    def get_current_theme(self) -> str:
        """Return name of currently active theme."""
        return self.current_theme


# Convenience exports - for simple imports
__all__ = [
    "Theme",
    "ComponentStyles",
    "Styles",
    "StyleManager",
]
