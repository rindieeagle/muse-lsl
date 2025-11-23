"""
UI components for MuseGUI
"""

from .main_window import MainWindow
from .device_panel import DevicePanel
from .streaming_panel import StreamingPanel
from .visualization import VisualizationPanel
from .settings_panel import SettingsPanel
from .testing_panel import TestingPanel
from .band_power_panel import BandPowerPanel
from .markers_panel import MarkersPanel

__all__ = [
    'MainWindow',
    'DevicePanel',
    'StreamingPanel',
    'VisualizationPanel',
    'SettingsPanel',
    'TestingPanel',
    'BandPowerPanel',
    'MarkersPanel',
]
