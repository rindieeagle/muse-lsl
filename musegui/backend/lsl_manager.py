"""
LSL Manager for MuseGUI
Manages LSL streaming and integrates with UDP streamer for dual-protocol output
"""

import logging
import threading
from typing import Optional, Callable, Dict, List
import time
from pylsl import StreamInlet, resolve_byprop, local_clock
import numpy as np

logger = logging.getLogger(__name__)


class LSLManager:
    """
    Manages LSL stream connection and data forwarding

    Integrates with both GUI visualization and UDP streaming
    """

    def __init__(self):
        """Initialize LSL manager"""
        self.inlets: Dict[str, StreamInlet] = {}
        self.is_running = False
        self.threads: List[threading.Thread] = []

        # Callbacks for data
        self.callbacks = {
            'eeg': [],
            'ppg': [],
            'acc': [],
            'gyro': []
        }

        # Statistics
        self.stats = {
            'eeg': {'samples': 0, 'errors': 0},
            'ppg': {'samples': 0, 'errors': 0},
            'acc': {'samples': 0, 'errors': 0},
            'gyro': {'samples': 0, 'errors': 0}
        }

        logger.info("LSL Manager initialized")

    def discover_streams(self, timeout: float = 5.0) -> Dict[str, bool]:
        """
        Discover available Muse LSL streams

        Args:
            timeout: Discovery timeout in seconds

        Returns:
            Dictionary with stream availability: {'eeg': True, 'ppg': False, ...}
        """
        logger.info(f"Discovering LSL streams (timeout: {timeout}s)...")

        available = {
            'eeg': False,
            'ppg': False,
            'acc': False,
            'gyro': False
        }

        try:
            # Search for Muse streams
            streams = resolve_byprop('type', 'EEG', timeout=timeout)
            if streams:
                available['eeg'] = True
                logger.info(f"Found EEG stream: {streams[0].name()}")

            streams = resolve_byprop('type', 'PPG', timeout=1.0)
            if streams:
                available['ppg'] = True
                logger.info(f"Found PPG stream: {streams[0].name()}")

            streams = resolve_byprop('type', 'Accelerometer', timeout=1.0)
            if streams:
                available['acc'] = True
                logger.info(f"Found ACC stream: {streams[0].name()}")

            streams = resolve_byprop('type', 'Gyroscope', timeout=1.0)
            if streams:
                available['gyro'] = True
                logger.info(f"Found GYRO stream: {streams[0].name()}")

        except Exception as e:
            logger.error(f"Error discovering streams: {e}")

        return available

    def connect_stream(self, stream_type: str) -> bool:
        """
        Connect to a specific LSL stream

        Args:
            stream_type: Type of stream ('eeg', 'ppg', 'acc', 'gyro')

        Returns:
            True if connected successfully
        """
        if stream_type in self.inlets:
            logger.warning(f"{stream_type.upper()} stream already connected")
            return True

        try:
            # Map stream types to LSL types
            lsl_type_map = {
                'eeg': 'EEG',
                'ppg': 'PPG',
                'acc': 'Accelerometer',
                'gyro': 'Gyroscope'
            }

            lsl_type = lsl_type_map.get(stream_type)
            if not lsl_type:
                logger.error(f"Invalid stream type: {stream_type}")
                return False

            # Resolve stream
            logger.info(f"Connecting to {stream_type.upper()} stream...")
            streams = resolve_byprop('type', lsl_type, timeout=5.0)

            if not streams:
                logger.warning(f"No {stream_type.upper()} stream found")
                return False

            # Create inlet
            inlet = StreamInlet(streams[0], max_buflen=360)
            self.inlets[stream_type] = inlet

            logger.info(f"Connected to {stream_type.upper()} stream: {streams[0].name()}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to {stream_type.upper()} stream: {e}")
            return False

    def disconnect_stream(self, stream_type: str):
        """
        Disconnect from a specific LSL stream

        Args:
            stream_type: Type of stream ('eeg', 'ppg', 'acc', 'gyro')
        """
        if stream_type in self.inlets:
            del self.inlets[stream_type]
            logger.info(f"Disconnected from {stream_type.upper()} stream")

    def start_receiving(self):
        """Start receiving data from connected streams"""
        if self.is_running:
            logger.warning("Already receiving data")
            return

        self.is_running = True

        # Start worker thread for each connected stream
        for stream_type, inlet in self.inlets.items():
            thread = threading.Thread(
                target=self._receive_worker,
                args=(stream_type, inlet),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)

        logger.info("Started receiving LSL data")

    def stop_receiving(self):
        """Stop receiving data"""
        if not self.is_running:
            return

        self.is_running = False

        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=1.0)

        self.threads.clear()
        logger.info(f"Stopped receiving LSL data. Stats: {self.get_stats()}")

    def _receive_worker(self, stream_type: str, inlet: StreamInlet):
        """
        Worker thread for receiving data from LSL stream

        Args:
            stream_type: Type of stream ('eeg', 'ppg', 'acc', 'gyro')
            inlet: LSL StreamInlet object
        """
        logger.debug(f"Started LSL worker for {stream_type}")

        while self.is_running:
            try:
                # Pull sample from LSL stream
                sample, timestamp = inlet.pull_sample(timeout=1.0)

                if sample:
                    # Update statistics
                    self.stats[stream_type]['samples'] += 1

                    # Call all registered callbacks
                    for callback in self.callbacks[stream_type]:
                        try:
                            callback(timestamp, sample)
                        except Exception as e:
                            logger.error(f"Error in {stream_type} callback: {e}")

            except Exception as e:
                if self.is_running:
                    logger.error(f"Error receiving {stream_type} data: {e}")
                    self.stats[stream_type]['errors'] += 1

        logger.debug(f"Stopped LSL worker for {stream_type}")

    def register_callback(self, stream_type: str, callback: Callable):
        """
        Register a callback for data from a specific stream

        Args:
            stream_type: Type of stream ('eeg', 'ppg', 'acc', 'gyro')
            callback: Callback function(timestamp, sample)
        """
        if stream_type not in self.callbacks:
            logger.error(f"Invalid stream type: {stream_type}")
            return

        self.callbacks[stream_type].append(callback)
        logger.debug(f"Registered callback for {stream_type}")

    def unregister_callback(self, stream_type: str, callback: Callable):
        """
        Unregister a callback

        Args:
            stream_type: Type of stream ('eeg', 'ppg', 'acc', 'gyro')
            callback: Callback function to remove
        """
        if stream_type in self.callbacks and callback in self.callbacks[stream_type]:
            self.callbacks[stream_type].remove(callback)
            logger.debug(f"Unregistered callback for {stream_type}")

    def get_stats(self) -> dict:
        """Get receiving statistics"""
        return {
            'connected_streams': list(self.inlets.keys()),
            'is_running': self.is_running,
            'stats': self.stats.copy()
        }

    def reset_stats(self):
        """Reset statistics"""
        for stream_type in self.stats:
            self.stats[stream_type] = {'samples': 0, 'errors': 0}

    def disconnect_all(self):
        """Disconnect from all streams"""
        self.stop_receiving()
        stream_types = list(self.inlets.keys())
        for stream_type in stream_types:
            self.disconnect_stream(stream_type)

    def __del__(self):
        """Cleanup on deletion"""
        self.disconnect_all()
