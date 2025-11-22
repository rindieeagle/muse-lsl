"""
Streaming Control Panel
Manages LSL and UDP streaming with real-time statistics
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGroupBox, QCheckBox, QSpinBox, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class StreamingPanel(QWidget):
    """
    Streaming Control Panel

    Manages LSL and UDP streaming protocols with statistics
    """

    lsl_started = pyqtSignal()
    lsl_stopped = pyqtSignal()
    udp_started = pyqtSignal()
    udp_stopped = pyqtSignal()

    def __init__(self, lsl_manager, udp_streamer):
        super().__init__()
        self.lsl_manager = lsl_manager
        self.udp_streamer = udp_streamer

        self.lsl_active = False
        self.udp_active = False

        # Statistics update timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.setInterval(1000)  # Update every second

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Header
        header = QLabel("Streaming Control")
        header.setProperty("class", "h2")
        layout.addWidget(header)

        # LSL Streaming Section
        lsl_group = QGroupBox("Lab Streaming Layer (LSL)")
        lsl_layout = QVBoxLayout()

        # LSL controls
        lsl_controls = QHBoxLayout()

        self.lsl_start_btn = QPushButton("▶ Start LSL Streaming")
        self.lsl_start_btn.setProperty("class", "success")
        self.lsl_start_btn.clicked.connect(self.start_lsl_streaming)
        lsl_controls.addWidget(self.lsl_start_btn)

        self.lsl_stop_btn = QPushButton("⏹ Stop LSL")
        self.lsl_stop_btn.setProperty("class", "danger")
        self.lsl_stop_btn.setEnabled(False)
        self.lsl_stop_btn.clicked.connect(self.stop_lsl_streaming)
        lsl_controls.addWidget(self.lsl_stop_btn)

        lsl_layout.addLayout(lsl_controls)

        # LSL stream selection
        stream_selection = QHBoxLayout()
        stream_selection.addWidget(QLabel("Active Streams:"))

        self.eeg_check = QCheckBox("EEG")
        self.eeg_check.setChecked(True)
        stream_selection.addWidget(self.eeg_check)

        self.ppg_check = QCheckBox("PPG")
        self.ppg_check.setChecked(True)
        stream_selection.addWidget(self.ppg_check)

        self.acc_check = QCheckBox("ACC")
        self.acc_check.setChecked(True)
        stream_selection.addWidget(self.acc_check)

        self.gyro_check = QCheckBox("GYRO")
        self.gyro_check.setChecked(True)
        stream_selection.addWidget(self.gyro_check)

        stream_selection.addStretch()
        lsl_layout.addLayout(stream_selection)

        # LSL status
        lsl_status = QHBoxLayout()
        lsl_status.addWidget(QLabel("Status:"))
        self.lsl_status_label = QLabel("Inactive")
        self.lsl_status_label.setProperty("class", "status-disconnected")
        lsl_status.addWidget(self.lsl_status_label)
        lsl_status.addStretch()
        lsl_layout.addLayout(lsl_status)

        lsl_group.setLayout(lsl_layout)
        layout.addWidget(lsl_group)

        # UDP Streaming Section
        udp_group = QGroupBox("UDP Streaming (MATLAB)")
        udp_layout = QVBoxLayout()

        # UDP configuration
        udp_config = QHBoxLayout()
        udp_config.addWidget(QLabel("Target IP:"))

        self.udp_host_input = QLineEdit()
        self.udp_host_input.setText("127.0.0.1")
        self.udp_host_input.setPlaceholderText("127.0.0.1")
        udp_config.addWidget(self.udp_host_input)

        udp_config.addWidget(QLabel("Port:"))

        self.udp_port_input = QSpinBox()
        self.udp_port_input.setRange(1024, 65535)
        self.udp_port_input.setValue(5000)
        udp_config.addWidget(self.udp_port_input)

        udp_config.addStretch()
        udp_layout.addLayout(udp_config)

        # UDP controls
        udp_controls = QHBoxLayout()

        self.udp_start_btn = QPushButton("▶ Start UDP Streaming")
        self.udp_start_btn.setProperty("class", "success")
        self.udp_start_btn.clicked.connect(self.start_udp_streaming)
        udp_controls.addWidget(self.udp_start_btn)

        self.udp_stop_btn = QPushButton("⏹ Stop UDP")
        self.udp_stop_btn.setProperty("class", "danger")
        self.udp_stop_btn.setEnabled(False)
        self.udp_stop_btn.clicked.connect(self.stop_udp_streaming)
        udp_controls.addWidget(self.udp_stop_btn)

        udp_layout.addLayout(udp_controls)

        # UDP status
        udp_status = QHBoxLayout()
        udp_status.addWidget(QLabel("Status:"))
        self.udp_status_label = QLabel("Inactive")
        self.udp_status_label.setProperty("class", "status-disconnected")
        udp_status.addWidget(self.udp_status_label)
        udp_status.addStretch()
        udp_layout.addLayout(udp_status)

        udp_group.setLayout(udp_layout)
        layout.addWidget(udp_group)

        # Statistics Section
        stats_group = QGroupBox("Streaming Statistics")
        stats_layout = QVBoxLayout()

        # Statistics table
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels(['Stream', 'Samples Received', 'Packets Sent (UDP)', 'Errors'])
        self.stats_table.setRowCount(4)
        self.stats_table.setVerticalHeaderLabels(['EEG', 'PPG', 'ACC', 'GYRO'])

        # Set table properties
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.stats_table.setMaximumHeight(180)

        # Initialize with zeros
        for row in range(4):
            for col in range(4):
                if col == 0:
                    stream_names = ['EEG', 'PPG', 'ACC', 'GYRO']
                    item = QTableWidgetItem(stream_names[row])
                else:
                    item = QTableWidgetItem('0')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.stats_table.setItem(row, col, item)

        stats_layout.addWidget(self.stats_table)

        # Reset button
        reset_btn = QPushButton("🔄 Reset Statistics")
        reset_btn.clicked.connect(self.reset_statistics)
        stats_layout.addWidget(reset_btn)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        layout.addStretch()
        self.setLayout(layout)

    def start_lsl_streaming(self):
        """Start LSL streaming"""
        try:
            logger.info("Starting LSL streaming...")

            # Discover streams
            available = self.lsl_manager.discover_streams(timeout=5.0)

            # Connect to selected streams
            connected = []
            if self.eeg_check.isChecked() and available['eeg']:
                if self.lsl_manager.connect_stream('eeg'):
                    connected.append('EEG')

            if self.ppg_check.isChecked() and available['ppg']:
                if self.lsl_manager.connect_stream('ppg'):
                    connected.append('PPG')

            if self.acc_check.isChecked() and available['acc']:
                if self.lsl_manager.connect_stream('acc'):
                    connected.append('ACC')

            if self.gyro_check.isChecked() and available['gyro']:
                if self.lsl_manager.connect_stream('gyro'):
                    connected.append('GYRO')

            if not connected:
                self.lsl_status_label.setText("No streams available")
                self.lsl_status_label.setProperty("class", "status-error")
                return

            # Start receiving data
            self.lsl_manager.start_receiving()

            # Update UI
            self.lsl_active = True
            self.lsl_status_label.setText(f"Active ({', '.join(connected)})")
            self.lsl_status_label.setProperty("class", "status-connected")
            self.lsl_status_label.style().unpolish(self.lsl_status_label)
            self.lsl_status_label.style().polish(self.lsl_status_label)

            self.lsl_start_btn.setEnabled(False)
            self.lsl_stop_btn.setEnabled(True)

            # Start statistics timer
            self.stats_timer.start()

            self.lsl_started.emit()
            logger.info("LSL streaming started")

        except Exception as e:
            logger.error(f"Failed to start LSL streaming: {e}")
            self.lsl_status_label.setText(f"Error: {str(e)}")
            self.lsl_status_label.setProperty("class", "status-error")

    def stop_lsl_streaming(self):
        """Stop LSL streaming"""
        try:
            logger.info("Stopping LSL streaming...")

            self.lsl_manager.stop_receiving()

            # Update UI
            self.lsl_active = False
            self.lsl_status_label.setText("Inactive")
            self.lsl_status_label.setProperty("class", "status-disconnected")
            self.lsl_status_label.style().unpolish(self.lsl_status_label)
            self.lsl_status_label.style().polish(self.lsl_status_label)

            self.lsl_start_btn.setEnabled(True)
            self.lsl_stop_btn.setEnabled(False)

            # Stop timer if UDP also inactive
            if not self.udp_active:
                self.stats_timer.stop()

            self.lsl_stopped.emit()
            logger.info("LSL streaming stopped")

        except Exception as e:
            logger.error(f"Failed to stop LSL streaming: {e}")

    def start_udp_streaming(self):
        """Start UDP streaming"""
        try:
            logger.info("Starting UDP streaming...")

            # Get configuration
            host = self.udp_host_input.text() or "127.0.0.1"
            port = self.udp_port_input.value()

            # Update UDP streamer configuration
            self.udp_streamer.host = host
            self.udp_streamer.port = port

            # Start UDP streamer
            self.udp_streamer.start()

            # Register callbacks with LSL manager to forward data to UDP
            self.lsl_manager.register_callback('eeg', lambda ts, data: self.udp_streamer.send_eeg_sample(ts, data))
            self.lsl_manager.register_callback('ppg', lambda ts, data: self.udp_streamer.send_ppg_sample(ts, data))
            self.lsl_manager.register_callback('acc', lambda ts, data: self.udp_streamer.send_acc_sample(ts, data))
            self.lsl_manager.register_callback('gyro', lambda ts, data: self.udp_streamer.send_gyro_sample(ts, data))

            # Update UI
            self.udp_active = True
            self.udp_status_label.setText(f"Active ({host}:{port})")
            self.udp_status_label.setProperty("class", "status-connected")
            self.udp_status_label.style().unpolish(self.udp_status_label)
            self.udp_status_label.style().polish(self.udp_status_label)

            self.udp_start_btn.setEnabled(False)
            self.udp_stop_btn.setEnabled(True)
            self.udp_host_input.setEnabled(False)
            self.udp_port_input.setEnabled(False)

            # Start statistics timer
            self.stats_timer.start()

            self.udp_started.emit()
            logger.info(f"UDP streaming started to {host}:{port}")

        except Exception as e:
            logger.error(f"Failed to start UDP streaming: {e}")
            self.udp_status_label.setText(f"Error: {str(e)}")
            self.udp_status_label.setProperty("class", "status-error")

    def stop_udp_streaming(self):
        """Stop UDP streaming"""
        try:
            logger.info("Stopping UDP streaming...")

            self.udp_streamer.stop()

            # Update UI
            self.udp_active = False
            self.udp_status_label.setText("Inactive")
            self.udp_status_label.setProperty("class", "status-disconnected")
            self.udp_status_label.style().unpolish(self.udp_status_label)
            self.udp_status_label.style().polish(self.udp_status_label)

            self.udp_start_btn.setEnabled(True)
            self.udp_stop_btn.setEnabled(False)
            self.udp_host_input.setEnabled(True)
            self.udp_port_input.setEnabled(True)

            # Stop timer if LSL also inactive
            if not self.lsl_active:
                self.stats_timer.stop()

            self.udp_stopped.emit()
            logger.info("UDP streaming stopped")

        except Exception as e:
            logger.error(f"Failed to stop UDP streaming: {e}")

    def update_statistics(self):
        """Update streaming statistics"""
        if self.lsl_active:
            lsl_stats = self.lsl_manager.get_stats()

            # Update LSL statistics
            for idx, stream_type in enumerate(['eeg', 'ppg', 'acc', 'gyro']):
                if stream_type in lsl_stats['stats']:
                    samples = lsl_stats['stats'][stream_type]['samples']
                    errors = lsl_stats['stats'][stream_type]['errors']

                    self.stats_table.item(idx, 1).setText(str(samples))
                    self.stats_table.item(idx, 3).setText(str(errors))

        if self.udp_active:
            udp_stats = self.udp_streamer.get_stats()

            # Update UDP statistics
            stream_map = {'eeg': 0, 'ppg': 1, 'acc': 2, 'gyro': 3}
            for stream_type, row in stream_map.items():
                packets = udp_stats['packets_sent'].get(stream_type, 0)
                self.stats_table.item(row, 2).setText(str(packets))

    def reset_statistics(self):
        """Reset all statistics"""
        self.lsl_manager.reset_stats()
        self.udp_streamer.reset_stats()

        # Reset table
        for row in range(4):
            for col in range(1, 4):
                self.stats_table.item(row, col).setText('0')

        logger.info("Statistics reset")

    def is_streaming(self):
        """Check if any streaming is active"""
        return self.lsl_active or self.udp_active
