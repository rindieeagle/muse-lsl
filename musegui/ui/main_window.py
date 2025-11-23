"""
Main Window for MuseGUI
Brings together all panels with retro rainbow glassmorphism design
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QLabel, QStatusBar, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
import logging
from pathlib import Path

from .device_panel import DevicePanel
from .streaming_panel import StreamingPanel
from .visualization import VisualizationPanel
from .settings_panel import SettingsPanel
from .testing_panel import TestingPanel
from .band_power_panel import BandPowerPanel
from .markers_panel import MarkersPanel
from ..backend.lsl_manager import LSLManager
from ..backend.udp_streamer import UDPStreamer
from ..backend.recorder import LabRecorderIntegration
from ..backend.event_markers import EventMarkerManager
from ..backend.artifact_detection import ArtifactDetector
from ..resources.palette import RetroRainbowPalette, Spacing

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main Application Window

    Integrates all components with retro rainbow glassmorphism design
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MuseGUI - Retro Rainbow EEG Interface")
        self.setMinimumSize(1200, 800)

        # Backend components
        self.lsl_manager = LSLManager()
        self.udp_streamer = UDPStreamer()
        self.lab_recorder = LabRecorderIntegration()
        self.event_marker_manager = EventMarkerManager()
        self.artifact_detector = ArtifactDetector()

        # Initialize UI
        self.init_ui()
        self.load_stylesheet()

        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second

        logger.info("MuseGUI initialized")

    def init_ui(self):
        """Initialize UI components"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(Spacing.MD)
        main_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Tab widget for main content
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(False)

        # Create panels
        self.device_panel = DevicePanel()
        self.streaming_panel = StreamingPanel(self.lsl_manager, self.udp_streamer)
        self.visualization_panel = VisualizationPanel(self.lsl_manager)
        self.band_power_panel = BandPowerPanel(self.lsl_manager)
        self.markers_panel = MarkersPanel(self.event_marker_manager)
        self.settings_panel = SettingsPanel()
        self.testing_panel = TestingPanel()

        # Add tabs
        self.tabs.addTab(self.device_panel, "🔌 Device")
        self.tabs.addTab(self.streaming_panel, "📡 Streaming")
        self.tabs.addTab(self.visualization_panel, "📊 Visualization")
        self.tabs.addTab(self.band_power_panel, "🧠 Band Power")
        self.tabs.addTab(self.markers_panel, "📍 Markers")
        self.tabs.addTab(self.settings_panel, "⚙️ Settings")
        self.tabs.addTab(self.testing_panel, "🧪 Testing")

        main_layout.addWidget(self.tabs)

        central_widget.setLayout(main_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Status bar widgets
        self.device_status = QLabel("Device: Disconnected")
        self.lsl_status = QLabel("LSL: Inactive")
        self.udp_status = QLabel("UDP: Inactive")

        self.status_bar.addPermanentWidget(self.device_status)
        self.status_bar.addPermanentWidget(self.lsl_status)
        self.status_bar.addPermanentWidget(self.udp_status)

        # Connect signals
        self.connect_signals()

    def create_header(self):
        """Create application header"""
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setSpacing(Spacing.SM)

        # Title
        title = QLabel("MuseGUI")
        title.setProperty("class", "h1")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Retro Rainbow EEG Interface for Muse Headsets")
        subtitle.setProperty("class", "h3")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        # Description
        description = QLabel(
            "LSL Streaming • UDP/MATLAB Integration • Lab Recorder Compatible • XDF Export"
        )
        description.setProperty("class", "muted")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(description)

        header_widget.setLayout(header_layout)
        return header_widget

    def load_stylesheet(self):
        """Load QSS stylesheet"""
        try:
            stylesheet_path = Path(__file__).parent / 'styles.qss'

            if stylesheet_path.exists():
                with open(stylesheet_path, 'r') as f:
                    stylesheet = f.read()
                    self.setStyleSheet(stylesheet)
                logger.info("Stylesheet loaded successfully")
            else:
                logger.warning(f"Stylesheet not found: {stylesheet_path}")

        except Exception as e:
            logger.error(f"Failed to load stylesheet: {e}")

    def connect_signals(self):
        """Connect signals between components"""
        # Device panel signals
        self.device_panel.device_connected.connect(self.on_device_connected)
        self.device_panel.device_disconnected.connect(self.on_device_disconnected)

        # Streaming panel signals
        self.streaming_panel.lsl_started.connect(self.on_lsl_started)
        self.streaming_panel.lsl_stopped.connect(self.on_lsl_stopped)
        self.streaming_panel.udp_started.connect(self.on_udp_started)
        self.streaming_panel.udp_stopped.connect(self.on_udp_stopped)

        # Settings panel signals
        self.settings_panel.settings_changed.connect(self.on_settings_changed)

        # Register artifact detector callbacks
        self.lsl_manager.register_callback('eeg', lambda ts, data: self.artifact_detector.add_eeg_sample(data))
        self.lsl_manager.register_callback('acc', lambda ts, data: self.artifact_detector.add_acc_sample(data))
        self.lsl_manager.register_callback('gyro', lambda ts, data: self.artifact_detector.add_gyro_sample(data))

        # Register periodic artifact detection
        self.artifact_timer = QTimer()
        self.artifact_timer.timeout.connect(self.check_artifacts)
        self.artifact_timer.setInterval(2000)  # Check every 2 seconds

    def on_device_connected(self, address, name):
        """Handle device connection"""
        logger.info(f"Device connected: {name} ({address})")
        self.device_status.setText(f"Device: {name}")

        # Auto-switch to streaming tab
        self.tabs.setCurrentIndex(1)

        # Show welcome message
        self.testing_panel.add_log(f"Device connected: {name}")

    def on_device_disconnected(self):
        """Handle device disconnection"""
        logger.info("Device disconnected")
        self.device_status.setText("Device: Disconnected")

        # Stop streaming if active
        if self.streaming_panel.is_streaming():
            self.streaming_panel.stop_lsl_streaming()
            self.streaming_panel.stop_udp_streaming()

        self.testing_panel.add_log("Device disconnected")

    def on_lsl_started(self):
        """Handle LSL streaming start"""
        logger.info("LSL streaming started")
        self.lsl_status.setText("LSL: Active")
        self.testing_panel.add_log("LSL streaming started")

        # Start event marker stream
        try:
            self.event_marker_manager.start_streaming()
            self.markers_panel.start_recording()
        except Exception as e:
            logger.error(f"Failed to start marker stream: {e}")

        # Start artifact detection
        self.artifact_timer.start()
        self.band_power_panel.start()

        # Auto-launch Lab Recorder if enabled
        settings = self.settings_panel.get_settings()
        if settings['lab_recorder']['auto_launch']:
            self.launch_lab_recorder()

    def on_lsl_stopped(self):
        """Handle LSL streaming stop"""
        logger.info("LSL streaming stopped")
        self.lsl_status.setText("LSL: Inactive")
        self.testing_panel.add_log("LSL streaming stopped")

        # Stop event marker stream
        self.event_marker_manager.stop_streaming()
        self.markers_panel.stop_recording()

        # Stop artifact detection
        self.artifact_timer.stop()
        self.band_power_panel.stop()

    def on_udp_started(self):
        """Handle UDP streaming start"""
        logger.info("UDP streaming started")
        self.udp_status.setText("UDP: Active")
        self.testing_panel.add_log("UDP streaming started")

    def on_udp_stopped(self):
        """Handle UDP streaming stop"""
        logger.info("UDP streaming stopped")
        self.udp_status.setText("UDP: Inactive")
        self.testing_panel.add_log("UDP streaming stopped")

    def on_settings_changed(self, settings):
        """Handle settings changes"""
        logger.info("Settings updated")
        self.testing_panel.add_log("Settings updated")

        # Apply settings (if needed)
        # e.g., update visualization update rate, etc.

    def launch_lab_recorder(self):
        """Launch Lab Recorder"""
        try:
            settings = self.settings_panel.get_settings()
            custom_path = settings['lab_recorder']['path']

            if self.lab_recorder.launch(custom_path if custom_path else None):
                self.testing_panel.add_log("Lab Recorder launched")
                logger.info("Lab Recorder launched successfully")
            else:
                logger.warning("Failed to launch Lab Recorder")

        except Exception as e:
            logger.error(f"Error launching Lab Recorder: {e}")

    def update_status(self):
        """Update status bar periodically"""
        # Update status colors
        if self.device_panel.is_connected():
            self.device_status.setProperty("class", "status-connected")
        else:
            self.device_status.setProperty("class", "status-disconnected")

        if self.streaming_panel.lsl_active:
            self.lsl_status.setProperty("class", "status-connected")
        else:
            self.lsl_status.setProperty("class", "status-disconnected")

        if self.streaming_panel.udp_active:
            self.udp_status.setProperty("class", "status-connected")
        else:
            self.udp_status.setProperty("class", "status-disconnected")

        # Force style update
        self.device_status.style().unpolish(self.device_status)
        self.device_status.style().polish(self.device_status)
        self.lsl_status.style().unpolish(self.lsl_status)
        self.lsl_status.style().polish(self.lsl_status)
        self.udp_status.style().unpolish(self.udp_status)
        self.udp_status.style().polish(self.udp_status)

    def check_artifacts(self):
        """Check for artifacts and update UI"""
        try:
            from pylsl import local_clock
            timestamp = local_clock()

            # Detect artifacts
            artifacts = self.artifact_detector.detect_artifacts(timestamp)

            # Log significant artifacts
            for artifact in artifacts:
                if artifact.severity > 0.5:  # Only log moderate to severe
                    self.testing_panel.add_log(f"⚠ Artifact: {artifact.description}")
                    logger.warning(f"Artifact detected: {artifact}")

            # Update signal quality score in status
            quality = self.artifact_detector.get_signal_quality_score()
            if quality < 70:
                self.testing_panel.add_log(f"⚠ Signal quality: {quality:.0f}/100")

        except Exception as e:
            logger.error(f"Error checking artifacts: {e}")

    def closeEvent(self, event):
        """Handle window close"""
        # Check if streaming is active
        if self.streaming_panel.is_streaming():
            reply = QMessageBox.question(
                self,
                "Streaming Active",
                "Streaming is currently active. Are you sure you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        # Stop everything
        try:
            logger.info("Shutting down MuseGUI...")

            # Stop streaming
            self.streaming_panel.stop_lsl_streaming()
            self.streaming_panel.stop_udp_streaming()

            # Disconnect device
            if self.device_panel.is_connected():
                self.device_panel.disconnect_device()

            # Close Lab Recorder
            self.lab_recorder.close()

            # Cleanup managers
            self.lsl_manager.disconnect_all()
            self.udp_streamer.stop()

            logger.info("MuseGUI shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

        event.accept()
