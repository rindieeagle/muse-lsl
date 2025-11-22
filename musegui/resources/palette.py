"""
Retro Rainbow Color Palette for MuseGUI
"""

class RetroRainbowPalette:
    """Retro rainbow color palette for the GUI"""

    # Primary palette colors
    DEEP_TEAL = "#025c7f"
    OCEAN_BLUE = "#027b96"
    AQUA_TEAL = "#069aa4"
    MINT_GREEN = "#87d1ac"
    CREAM_YELLOW = "#fef8be"
    PEACH = "#ffe1a5"
    CORAL = "#ffc991"
    ORANGE = "#ffb085"
    SALMON = "#fb9481"
    ROSE = "#f37986"

    # Semantic colors
    PRIMARY = DEEP_TEAL
    SECONDARY = AQUA_TEAL
    ACCENT = ROSE
    SUCCESS = MINT_GREEN
    WARNING = PEACH
    ERROR = SALMON
    INFO = OCEAN_BLUE

    # UI elements
    BACKGROUND_DARK = "#012a3a"
    BACKGROUND_MEDIUM = "#024a5f"
    BACKGROUND_LIGHT = "#035d7a"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#e0e0e0"
    TEXT_MUTED = "#a0a0a0"

    # Glass effect
    GLASS_OVERLAY = "rgba(2, 92, 127, 0.15)"
    GLASS_BORDER = "rgba(135, 209, 172, 0.3)"
    GLASS_SHADOW = "rgba(0, 0, 0, 0.3)"

    @classmethod
    def get_gradient(cls, start_color, end_color):
        """Generate CSS gradient string"""
        return f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {start_color}, stop:1 {end_color})"

    @classmethod
    def get_glassmorphism_style(cls):
        """Generate glassmorphism effect CSS"""
        return f"""
            background: {cls.GLASS_OVERLAY};
            border: 1px solid {cls.GLASS_BORDER};
            border-radius: 12px;
            backdrop-filter: blur(10px);
        """


# Spacing system (4px base)
class Spacing:
    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48


# Breakpoints
class Breakpoints:
    MOBILE_MAX = 767
    TABLET_MIN = 768
    TABLET_MAX = 1024
    DESKTOP_MIN = 1025
    DESKTOP_MAX = 1440
    LARGE_DESKTOP_MIN = 1441


# Typography
class Typography:
    HEADER_FONT = "Cooper Black, New Kansas, Arial Black, sans-serif"
    BODY_FONT = "Nunito, Arial, sans-serif"

    # Font sizes
    H1_SIZE = 32
    H2_SIZE = 24
    H3_SIZE = 20
    BODY_SIZE = 14
    SMALL_SIZE = 12
