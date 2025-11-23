"""
Backend modules for MuseGUI
"""

from .lsl_manager import LSLManager
from .udp_streamer import UDPStreamer
from .recorder import LabRecorderIntegration, RecordingSession, XDFUtilities
from .event_markers import EventMarkerManager, EventMarker, KeyboardMarkerHandler
from .artifact_detection import ArtifactDetector, ArtifactEvent, ArtifactType

__all__ = [
    'LSLManager',
    'UDPStreamer',
    'LabRecorderIntegration',
    'RecordingSession',
    'XDFUtilities',
    'EventMarkerManager',
    'EventMarker',
    'KeyboardMarkerHandler',
    'ArtifactDetector',
    'ArtifactEvent',
    'ArtifactType',
]
