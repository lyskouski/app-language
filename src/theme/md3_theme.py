# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

"""
Material Design 3 Theme Constants and Styling System
Provides consistent colors, typography, and spacing across the entire application
"""

from kivy.metrics import dp
from kivy.core.window import Window

# ==============================================================================
# MATERIAL DESIGN 3 COLOR PALETTE (Blue Primary)
# ==============================================================================

class MD3Colors:
    """Material Design 3 Color System with Blue as primary color"""

    # Primary Colors
    PRIMARY = "#2196F3"           # Blue
    PRIMARY_CONTAINER = "#BBDEFB"  # Light Blue

    # Secondary Colors
    SECONDARY = "#1976D2"        # Darker Blue
    SECONDARY_CONTAINER = "#64B5F6"  # Medium Blue

    # Tertiary Colors
    TERTIARY = "#0D47A1"         # Dark Blue
    TERTIARY_CONTAINER = "#90CAF9"   # Sky Blue

    # Neutral/Grayscale
    BACKGROUND = "#FFFFFF"       # White
    SURFACE = "#F5F5F5"          # Light Gray
    SURFACE_VARIANT = "#EEEEEE"  # Lighter Gray

    # Error/Status Colors
    ERROR = "#B3261E"            # Red
    ERROR_CONTAINER = "#F9DEDC"  # Light Red

    # Text/On Colors
    ON_PRIMARY = "#FFFFFF"       # White text on primary
    ON_SECONDARY = "#FFFFFF"     # White text on secondary
    ON_SURFACE = "#1C1B1F"       # Dark text on surface
    ON_SURFACE_VARIANT = "#49454E"  # Medium text
    ON_ERROR = "#FFFFFF"         # White text on error

    # Accent Colors
    ACCENT = "#FF6F00"           # Orange (for highlights)
    ACCENT_LIGHT = "#FFB74D"     # Light Orange

    # Semantic Colors
    SUCCESS = "#4CAF50"          # Green
    WARNING = "#FFC107"          # Amber
    INFO = "#2196F3"             # Blue


class MD3Typography:
    """Material Design 3 Typography Scales"""

    # Font Family
    FONT_FAMILY = "Roboto"  # Default to system Roboto; Kivy uses default if not available

    # Display Scale (Large headings)
    DISPLAY_LARGE = {"size": dp(57), "line_height": 1.4}
    DISPLAY_MEDIUM = {"size": dp(45), "line_height": 1.4}
    DISPLAY_SMALL = {"size": dp(36), "line_height": 1.3}

    # Headline Scale
    HEADLINE_LARGE = {"size": dp(32), "line_height": 1.3}
    HEADLINE_MEDIUM = {"size": dp(28), "line_height": 1.3}
    HEADLINE_SMALL = {"size": dp(24), "line_height": 1.3}

    # Title Scale
    TITLE_LARGE = {"size": dp(22), "line_height": 1.3}
    TITLE_MEDIUM = {"size": dp(18), "line_height": 1.4}
    TITLE_SMALL = {"size": dp(14), "line_height": 1.4}

    # Body Scale (Main text)
    BODY_LARGE = {"size": dp(16), "line_height": 1.5}  # Default body text
    BODY_MEDIUM = {"size": dp(14), "line_height": 1.5}  # Secondary body
    BODY_SMALL = {"size": dp(12), "line_height": 1.5}   # Tertiary body

    # Label Scale (Buttons, tags)
    LABEL_LARGE = {"size": dp(14), "line_height": 1.4}  # Button labels
    LABEL_MEDIUM = {"size": dp(12), "line_height": 1.4}  # Small labels
    LABEL_SMALL = {"size": dp(11), "line_height": 1.3}   # Smallest labels


class MD3Spacing:
    """Material Design 3 Spacing and Sizing System"""

    # Base spacing unit (4dp)
    UNIT = dp(4)

    # Spacing scale
    SPACING_0 = dp(0)
    SPACING_1 = dp(4)
    SPACING_2 = dp(8)
    SPACING_3 = dp(12)
    SPACING_4 = dp(16)
    SPACING_5 = dp(20)
    SPACING_6 = dp(24)
    SPACING_7 = dp(28)
    SPACING_8 = dp(32)
    SPACING_9 = dp(36)
    SPACING_10 = dp(40)

    # Common padding/margin combinations
    PADDING_SMALL = dp(8)
    PADDING_MEDIUM = dp(16)
    PADDING_LARGE = dp(24)

    # Component dimensions
    BUTTON_HEIGHT = dp(40)
    BUTTON_HEIGHT_COMPACT = dp(36)
    TEXTFIELD_HEIGHT = dp(56)
    TEXTFIELD_HEIGHT_DENSE = dp(48)
    TOPAPPBAR_HEIGHT = dp(56)
    TOPAPPBAR_HEIGHT_LARGE = dp(96)

    # Icon sizes
    ICON_SMALL = dp(16)
    ICON_MEDIUM = dp(24)
    ICON_LARGE = dp(32)
    ICON_XLARGE = dp(48)

    # Corner radius
    RADIUS_NONE = dp(0)
    RADIUS_EXTRA_SMALL = dp(4)
    RADIUS_SMALL = dp(8)
    RADIUS_MEDIUM = dp(12)
    RADIUS_LARGE = dp(16)
    RADIUS_EXTRA_LARGE = dp(28)
    RADIUS_FULL = dp(500)  # Fully rounded


class MD3Elevation:
    """Material Design 3 Elevation/Shadow Levels"""
    LEVEL_0 = 0      # No shadow
    LEVEL_1 = 1      # Raised surface
    LEVEL_2 = 2      # Cards, buttons
    LEVEL_3 = 3      # Dialog
    LEVEL_4 = 4      # FAB
    LEVEL_5 = 5      # Modal bottom sheet


class MD3ThemeConfig:
    """Configuration for MDTheme in Material Design 3"""

    # Theme configuration
    THEME_STYLE = "Light"      # "Light" or "Dark"
    MATERIAL_STYLE = "M3"       # Material Design 3
    PRIMARY_PALETTE = "Blue"    # Primary color palette
    ACCENT_PALETTE = "Amber"    # Accent palette

    @staticmethod
    def apply_to_app(app):
        """Apply MD3 theme to a KivyMD app"""
        app.theme_cls.theme_style = MD3ThemeConfig.THEME_STYLE
        app.theme_cls.material_style = MD3ThemeConfig.MATERIAL_STYLE
        app.theme_cls.primary_palette = MD3ThemeConfig.PRIMARY_PALETTE
        app.theme_cls.accent_palette = MD3ThemeConfig.ACCENT_PALETTE


# ==============================================================================
# KV STYLE SNIPPETS (Copy-paste friendly constants for KV files)
# ==============================================================================

class KVStyles:
    """Ready-to-use KV style snippets"""

    # Standard button group
    BUTTON_GROUP_STYLE = """
    MDRaisedButton:
        size_hint_x: 1
        height: dp(40)
    MDFlatButton:
        size_hint_x: 1
        height: dp(40)
    """

    # Standard text field
    TEXTFIELD_STYLE = """
    MDTextField:
        mode: "rectangle"
        height: dp(56)
        size_hint_x: 1
    """

    # Standard top app bar
    TOPAPPBAR_STYLE = """
    MDTopAppBar:
        title: "Screen Title"
        elevation: 1
        height: dp(56)
    """

    # Standard padding for screens
    SCREEN_PADDING = """
    padding: dp(16), dp(16), dp(16), dp(16)
    """


# ==============================================================================
# RESPONSIVE DESIGN HELPER
# ==============================================================================

class MD3Responsive:
    """Responsive design helpers for different screen sizes"""

    @staticmethod
    def get_button_width():
        """Adaptive button width based on window"""
        return Window.width * 0.9 if Window.width < dp(480) else dp(400)

    @staticmethod
    def get_column_count():
        """Number of columns based on screen width"""
        if Window.width < dp(600):
            return 1
        elif Window.width < dp(900):
            return 2
        else:
            return 3

    @staticmethod
    def get_grid_item_width():
        """Grid item width for responsive layout"""
        cols = MD3Responsive.get_column_count()
        padding = MD3Spacing.SPACING_4 * 2  # Left and right padding
        return (Window.width - padding) / cols
