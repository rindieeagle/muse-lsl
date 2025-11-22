"""
Recorder Module for MuseGUI
Handles recording LSL streams to XDF format and Lab Recorder integration
"""

import logging
import os
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class LabRecorderIntegration:
    """
    Integration with Lab Recorder application

    Provides utilities for launching Lab Recorder and managing recordings
    """

    def __init__(self):
        """Initialize Lab Recorder integration"""
        self.process: Optional[subprocess.Popen] = None
        self.config_file: Optional[Path] = None
        logger.info("Lab Recorder integration initialized")

    def find_lab_recorder(self) -> Optional[Path]:
        """
        Try to find Lab Recorder executable

        Returns:
            Path to Lab Recorder executable or None
        """
        system = platform.system()

        # Common installation paths
        search_paths = []

        if system == "Windows":
            search_paths = [
                Path("C:/Program Files/labstreaminglayer/LabRecorder/LabRecorder.exe"),
                Path("C:/Program Files (x86)/labstreaminglayer/LabRecorder/LabRecorder.exe"),
                Path(os.path.expanduser("~/AppData/Local/LabRecorder/LabRecorder.exe")),
            ]
        elif system == "Darwin":  # macOS
            search_paths = [
                Path("/Applications/LabRecorder.app/Contents/MacOS/LabRecorder"),
                Path(os.path.expanduser("~/Applications/LabRecorder.app/Contents/MacOS/LabRecorder")),
            ]
        elif system == "Linux":
            search_paths = [
                Path("/usr/local/bin/LabRecorder"),
                Path("/usr/bin/LabRecorder"),
                Path(os.path.expanduser("~/bin/LabRecorder")),
            ]

        # Check each path
        for path in search_paths:
            if path.exists():
                logger.info(f"Found Lab Recorder at: {path}")
                return path

        logger.warning("Lab Recorder not found in standard locations")
        return None

    def launch(self, custom_path: Optional[str] = None) -> bool:
        """
        Launch Lab Recorder application

        Args:
            custom_path: Optional custom path to Lab Recorder executable

        Returns:
            True if launched successfully
        """
        if self.process and self.process.poll() is None:
            logger.warning("Lab Recorder already running")
            return True

        try:
            # Find executable
            executable = Path(custom_path) if custom_path else self.find_lab_recorder()

            if not executable or not executable.exists():
                logger.error("Lab Recorder executable not found")
                return False

            # Launch Lab Recorder
            logger.info(f"Launching Lab Recorder: {executable}")
            self.process = subprocess.Popen([str(executable)],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

            logger.info("Lab Recorder launched successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to launch Lab Recorder: {e}")
            return False

    def is_running(self) -> bool:
        """Check if Lab Recorder is running"""
        return self.process is not None and self.process.poll() is None

    def close(self):
        """Close Lab Recorder application"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("Lab Recorder closed")
            except:
                self.process.kill()
                logger.warning("Lab Recorder killed (forced)")

            self.process = None

    def create_config(self, output_dir: str, filename_template: str = "muse_%n.xdf",
                     streams: Optional[List[str]] = None) -> Path:
        """
        Create Lab Recorder configuration file

        Args:
            output_dir: Output directory for recordings
            filename_template: Filename template (%n = number, %b = block)
            streams: List of stream names to record (None = all)

        Returns:
            Path to configuration file
        """
        config = {
            "StorageLocation": str(Path(output_dir).absolute()),
            "SessionBlocks": [1],
            "RootLocation": str(Path(output_dir).absolute()),
            "PathTemplate": filename_template,
            "RequiredStreams": streams or [],
            "OnlineSync": True,
            "SyncPostProcessing": True,
            "UnsampledStreams": False
        }

        # Save config file
        config_dir = Path.home() / ".musegui"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "labrecorder_config.json"

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        self.config_file = config_file
        logger.info(f"Created Lab Recorder config: {config_file}")
        return config_file


class RecordingSession:
    """
    Manages a recording session

    Handles metadata, file paths, and recording state
    """

    def __init__(self, output_dir: str, session_name: Optional[str] = None):
        """
        Initialize recording session

        Args:
            output_dir: Directory for saving recordings
            session_name: Optional session name (default: timestamp-based)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if session_name is None:
            session_name = datetime.now().strftime("muse_recording_%Y%m%d_%H%M%S")

        self.session_name = session_name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.is_recording = False

        # Metadata
        self.metadata = {
            'session_name': session_name,
            'created': datetime.now().isoformat(),
            'streams_recorded': [],
            'participant_id': '',
            'notes': ''
        }

        logger.info(f"Recording session created: {session_name}")

    def start(self):
        """Start recording"""
        if self.is_recording:
            logger.warning("Recording already started")
            return

        self.is_recording = True
        self.start_time = datetime.now()
        self.metadata['start_time'] = self.start_time.isoformat()
        logger.info(f"Recording started: {self.session_name}")

    def stop(self):
        """Stop recording"""
        if not self.is_recording:
            logger.warning("Recording not started")
            return

        self.is_recording = False
        self.end_time = datetime.now()
        self.metadata['end_time'] = self.end_time.isoformat()

        if self.start_time:
            duration = (self.end_time - self.start_time).total_seconds()
            self.metadata['duration_seconds'] = duration

        # Save metadata
        self.save_metadata()

        logger.info(f"Recording stopped: {self.session_name} (duration: {duration:.1f}s)")

    def save_metadata(self):
        """Save session metadata to JSON file"""
        metadata_file = self.output_dir / f"{self.session_name}_metadata.json"

        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

        logger.info(f"Metadata saved: {metadata_file}")

    def set_participant_id(self, participant_id: str):
        """Set participant ID"""
        self.metadata['participant_id'] = participant_id

    def add_note(self, note: str):
        """Add a note to the session"""
        if 'notes' not in self.metadata:
            self.metadata['notes'] = []

        self.metadata['notes'].append({
            'timestamp': datetime.now().isoformat(),
            'note': note
        })

    def get_duration(self) -> float:
        """Get recording duration in seconds"""
        if self.start_time is None:
            return 0.0

        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    def get_output_path(self, extension: str = '.xdf') -> Path:
        """Get output file path for recording"""
        return self.output_dir / f"{self.session_name}{extension}"


class XDFUtilities:
    """
    Utilities for working with XDF files

    Provides validation, conversion, and inspection tools
    """

    @staticmethod
    def validate_xdf(filepath: str) -> Dict:
        """
        Validate an XDF file and return information

        Args:
            filepath: Path to XDF file

        Returns:
            Dictionary with file info and validation status
        """
        try:
            import pyxdf

            # Load XDF file
            data, header = pyxdf.load_xdf(filepath, verbose=False)

            info = {
                'valid': True,
                'filepath': filepath,
                'num_streams': len(data),
                'streams': [],
                'total_samples': 0,
                'duration': 0.0
            }

            # Analyze each stream
            for stream in data:
                stream_info = {
                    'name': stream['info']['name'][0],
                    'type': stream['info']['type'][0],
                    'channel_count': int(stream['info']['channel_count'][0]),
                    'nominal_srate': float(stream['info']['nominal_srate'][0]),
                    'num_samples': len(stream['time_stamps'])
                }

                info['streams'].append(stream_info)
                info['total_samples'] += stream_info['num_samples']

                # Calculate duration
                if len(stream['time_stamps']) > 0:
                    duration = stream['time_stamps'][-1] - stream['time_stamps'][0]
                    if duration > info['duration']:
                        info['duration'] = duration

            logger.info(f"XDF file validated: {filepath} ({info['num_streams']} streams, {info['duration']:.1f}s)")
            return info

        except Exception as e:
            logger.error(f"Failed to validate XDF file: {e}")
            return {
                'valid': False,
                'error': str(e),
                'filepath': filepath
            }

    @staticmethod
    def get_stream_info(filepath: str) -> List[Dict]:
        """
        Get information about streams in XDF file without loading data

        Args:
            filepath: Path to XDF file

        Returns:
            List of stream information dictionaries
        """
        try:
            import pyxdf

            # Load only headers
            streams, header = pyxdf.load_xdf(filepath, verbose=False)

            stream_info = []
            for stream in streams:
                info = {
                    'name': stream['info']['name'][0],
                    'type': stream['info']['type'][0],
                    'channel_count': int(stream['info']['channel_count'][0]),
                    'nominal_srate': float(stream['info']['nominal_srate'][0]),
                }

                # Get channel labels if available
                if 'desc' in stream['info'] and 'channels' in stream['info']['desc'][0]:
                    channels = stream['info']['desc'][0]['channels'][0]['channel']
                    info['channel_labels'] = [ch['label'][0] for ch in channels]

                stream_info.append(info)

            return stream_info

        except Exception as e:
            logger.error(f"Failed to get stream info: {e}")
            return []
