"""
Event Markers System
Manages event markers during recording sessions
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from pylsl import StreamInfo, StreamOutlet
import time

logger = logging.getLogger(__name__)


class EventMarker:
    """Represents a single event marker"""

    def __init__(self, timestamp: float, label: str, description: str = ""):
        """
        Initialize event marker

        Args:
            timestamp: Timestamp (LSL time)
            label: Marker label
            description: Optional description
        """
        self.timestamp = timestamp
        self.label = label
        self.description = description
        self.local_time = datetime.now()

    def __repr__(self):
        return f"EventMarker({self.label} @ {self.timestamp:.3f})"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'label': self.label,
            'description': self.description,
            'local_time': self.local_time.isoformat()
        }


class EventMarkerManager:
    """
    Manages event markers during recording

    Provides:
    - LSL marker stream for Lab Recorder
    - Internal marker storage
    - Keyboard shortcut handling
    - Export to various formats
    """

    def __init__(self):
        """Initialize event marker manager"""
        self.markers: List[EventMarker] = []
        self.lsl_outlet: Optional[StreamOutlet] = None
        self.is_streaming = False

        logger.info("Event Marker Manager initialized")

    def start_streaming(self):
        """Start LSL marker stream"""
        if self.is_streaming:
            logger.warning("Marker stream already active")
            return

        try:
            # Create LSL marker stream
            info = StreamInfo(
                name='MuseGUI_Markers',
                type='Markers',
                channel_count=1,
                nominal_srate=0,  # Irregular rate
                channel_format='string',
                source_id='musegui_markers_001'
            )

            # Add metadata
            desc = info.desc()
            desc.append_child_value("manufacturer", "MuseGUI")
            desc.append_child_value("version", "1.0.0")

            # Create outlet
            self.lsl_outlet = StreamOutlet(info)
            self.is_streaming = True

            logger.info("LSL marker stream started")

        except Exception as e:
            logger.error(f"Failed to start marker stream: {e}")
            raise

    def stop_streaming(self):
        """Stop LSL marker stream"""
        if not self.is_streaming:
            return

        self.lsl_outlet = None
        self.is_streaming = False
        logger.info("LSL marker stream stopped")

    def add_marker(self, label: str, description: str = "", custom_timestamp: Optional[float] = None):
        """
        Add an event marker

        Args:
            label: Marker label (e.g., 'Stimulus_A', 'Eyes_Closed')
            description: Optional description
            custom_timestamp: Optional custom timestamp (uses current time if None)

        Returns:
            The created EventMarker
        """
        # Get timestamp
        if custom_timestamp is not None:
            timestamp = custom_timestamp
        else:
            from pylsl import local_clock
            timestamp = local_clock()

        # Create marker
        marker = EventMarker(timestamp, label, description)
        self.markers.append(marker)

        # Send to LSL if streaming
        if self.is_streaming and self.lsl_outlet:
            try:
                self.lsl_outlet.push_sample([label], timestamp)
                logger.debug(f"Marker sent to LSL: {label} @ {timestamp:.3f}")
            except Exception as e:
                logger.error(f"Failed to send marker to LSL: {e}")

        logger.info(f"Marker added: {marker}")
        return marker

    def add_marker_now(self, label: str, description: str = ""):
        """
        Add marker with current timestamp (convenience method)

        Args:
            label: Marker label
            description: Optional description
        """
        return self.add_marker(label, description)

    def get_markers(self, start_time: Optional[float] = None, end_time: Optional[float] = None) -> List[EventMarker]:
        """
        Get markers within time range

        Args:
            start_time: Start timestamp (None = from beginning)
            end_time: End timestamp (None = to end)

        Returns:
            List of markers in range
        """
        if start_time is None and end_time is None:
            return self.markers

        filtered = []
        for marker in self.markers:
            if start_time is not None and marker.timestamp < start_time:
                continue
            if end_time is not None and marker.timestamp > end_time:
                continue
            filtered.append(marker)

        return filtered

    def get_marker_count(self) -> int:
        """Get total number of markers"""
        return len(self.markers)

    def clear_markers(self):
        """Clear all markers"""
        self.markers.clear()
        logger.info("All markers cleared")

    def export_to_dict(self) -> List[Dict]:
        """
        Export markers to list of dictionaries

        Returns:
            List of marker dictionaries
        """
        return [marker.to_dict() for marker in self.markers]

    def export_to_csv(self, filepath: str):
        """
        Export markers to CSV file

        Args:
            filepath: Path to CSV file
        """
        import csv

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Label', 'Description', 'Local Time'])

            for marker in self.markers:
                writer.writerow([
                    marker.timestamp,
                    marker.label,
                    marker.description,
                    marker.local_time.isoformat()
                ])

        logger.info(f"Markers exported to CSV: {filepath}")

    def export_to_json(self, filepath: str):
        """
        Export markers to JSON file

        Args:
            filepath: Path to JSON file
        """
        import json

        data = self.export_to_dict()

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Markers exported to JSON: {filepath}")

    def get_summary(self) -> str:
        """
        Get summary of markers

        Returns:
            Summary string
        """
        if not self.markers:
            return "No markers recorded"

        marker_types = {}
        for marker in self.markers:
            marker_types[marker.label] = marker_types.get(marker.label, 0) + 1

        summary = f"Total markers: {len(self.markers)}\n"
        summary += "Marker types:\n"
        for label, count in sorted(marker_types.items()):
            summary += f"  {label}: {count}\n"

        if len(self.markers) >= 2:
            duration = self.markers[-1].timestamp - self.markers[0].timestamp
            summary += f"Duration: {duration:.1f} seconds\n"

        return summary


class KeyboardMarkerHandler:
    """
    Handles keyboard shortcuts for adding markers

    Default shortcuts:
    - Space: Generic marker
    - 1-9: Numbered markers (Marker_1, Marker_2, etc.)
    - T: Timestamp marker with note
    - E: Event marker
    - S: Stimulus marker
    - R: Response marker
    """

    def __init__(self, marker_manager: EventMarkerManager):
        """
        Initialize keyboard handler

        Args:
            marker_manager: EventMarkerManager instance
        """
        self.marker_manager = marker_manager

        # Define default shortcuts
        self.shortcuts = {
            'Space': 'Marker',
            '1': 'Marker_1',
            '2': 'Marker_2',
            '3': 'Marker_3',
            '4': 'Marker_4',
            '5': 'Marker_5',
            '6': 'Marker_6',
            '7': 'Marker_7',
            '8': 'Marker_8',
            '9': 'Marker_9',
            'T': 'Timestamp',
            'E': 'Event',
            'S': 'Stimulus',
            'R': 'Response'
        }

    def handle_key(self, key: str, description: str = ""):
        """
        Handle keyboard input

        Args:
            key: Key pressed
            description: Optional description
        """
        if key in self.shortcuts:
            label = self.shortcuts[key]
            self.marker_manager.add_marker_now(label, description)
            logger.debug(f"Keyboard marker: {key} -> {label}")
        else:
            logger.debug(f"Unknown marker key: {key}")

    def add_custom_shortcut(self, key: str, label: str):
        """
        Add custom keyboard shortcut

        Args:
            key: Keyboard key
            label: Marker label
        """
        self.shortcuts[key] = label
        logger.info(f"Custom shortcut added: {key} -> {label}")

    def remove_shortcut(self, key: str):
        """
        Remove keyboard shortcut

        Args:
            key: Keyboard key
        """
        if key in self.shortcuts:
            del self.shortcuts[key]
            logger.info(f"Shortcut removed: {key}")

    def get_shortcuts(self) -> Dict[str, str]:
        """Get all keyboard shortcuts"""
        return self.shortcuts.copy()
