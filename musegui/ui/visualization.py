"""
Real-time Data Visualization Panel
Displays EEG, PPG, and IMU data with retro rainbow styling
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGroupBox, QCheckBox, QComboBox, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal
import pyqtgraph as pg
import numpy as np
from collections import deque
import logging

logger = logging.getLogger(__name__)


class VisualizationPanel(QWidget):
    """
    Real-time Data Visualization Panel

    Displays multi-channel data with customizable views
    """

    def __init__(self, lsl_manager):
        super().__init__()
        self.lsl_manager = lsl_manager

        # Data buffers (ring buffers for efficiency)
        self.buffer_size = 1280  # 5 seconds at 256 Hz
        self.eeg_buffer = [deque(maxlen=self.buffer_size) for _ in range(5)]
        self.ppg_buffer = [deque(maxlen=320) for _ in range(3)]  # 5 seconds at 64 Hz
        self.acc_buffer = [deque(maxlen=260) for _ in range(3)]  # 5 seconds at 52 Hz
        self.gyro_buffer = [deque(maxlen=260) for _ in range(3)]  # 5 seconds at 52 Hz

        # Time buffers
        self.eeg_time = deque(maxlen=self.buffer_size)
        self.ppg_time = deque(maxlen=320)
        self.acc_time = deque(maxlen=260)
        self.gyro_time = deque(maxlen=260)

        # Channel names
        self.eeg_channels = ['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX']
        self.ppg_channels = ['PPG1', 'PPG2', 'PPG3']
        self.acc_channels = ['X', 'Y', 'Z']
        self.gyro_channels = ['X', 'Y', 'Z']

        # Retro rainbow colors for channels
        self.channel_colors = [
            '#069aa4',  # Aqua Teal
            '#87d1ac',  # Mint Green
            '#fef8be',  # Cream Yellow
            '#ffc991',  # Coral
            '#fb9481',  # Salmon
            '#f37986',  # Rose
            '#ffe1a5',  # Peach
            '#ffb085',  # Orange
        ]

        # Register callbacks
        self.lsl_manager.register_callback('eeg', self.on_eeg_data)
        self.lsl_manager.register_callback('ppg', self.on_ppg_data)
        self.lsl_manager.register_callback('acc', self.on_acc_data)
        self.lsl_manager.register_callback('gyro', self.on_gyro_data)

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Header
        header = QLabel("Real-Time Data Visualization")
        header.setProperty("class", "h2")
        layout.addWidget(header)

        # Controls
        controls = self.create_controls()
        layout.addWidget(controls)

        # Plot widget
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.setBackground('#012a3a')
        layout.addWidget(self.plot_widget)

        # Create plots
        self.create_plots()

        # Status
        self.status_label = QLabel("Waiting for data...")
        self.status_label.setProperty("class", "muted")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def create_controls(self):
        """Create control panel"""
        controls_group = QGroupBox("Display Controls")
        controls_layout = QHBoxLayout()

        # Data type selection
        controls_layout.addWidget(QLabel("View:"))
        self.view_combo = QComboBox()
        self.view_combo.addItems(['EEG', 'PPG', 'Accelerometer', 'Gyroscope', 'All'])
        self.view_combo.setCurrentText('EEG')
        self.view_combo.currentTextChanged.connect(self.on_view_changed)
        controls_layout.addWidget(self.view_combo)

        # Time scale
        controls_layout.addWidget(QLabel("Time Scale:"))
        self.time_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_scale_slider.setRange(1, 10)
        self.time_scale_slider.setValue(5)
        self.time_scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.time_scale_slider.setTickInterval(1)
        self.time_scale_slider.valueChanged.connect(self.on_time_scale_changed)
        controls_layout.addWidget(self.time_scale_slider)

        self.time_scale_label = QLabel("5s")
        controls_layout.addWidget(self.time_scale_label)

        # Auto-scale
        self.autoscale_check = QCheckBox("Auto-scale")
        self.autoscale_check.setChecked(True)
        controls_layout.addWidget(self.autoscale_check)

        # Clear button
        clear_btn = QPushButton("🗑 Clear")
        clear_btn.clicked.connect(self.clear_buffers)
        controls_layout.addWidget(clear_btn)

        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)
        return controls_group

    def create_plots(self):
        """Create plot items"""
        self.plots = {}
        self.curves = {}

        # EEG plots (5 channels)
        self.plots['eeg'] = []
        self.curves['eeg'] = []

        for i, channel in enumerate(self.eeg_channels):
            plot = self.plot_widget.addPlot(row=i, col=0, title=channel)
            plot.setLabel('left', 'μV')
            plot.setLabel('bottom', 'Time (s)')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.setYRange(-200, 200)

            # Create curve
            color = self.channel_colors[i % len(self.channel_colors)]
            curve = plot.plot(pen=pg.mkPen(color=color, width=2))

            self.plots['eeg'].append(plot)
            self.curves['eeg'].append(curve)

        # PPG plots (hidden by default)
        self.plots['ppg'] = []
        self.curves['ppg'] = []

        for i, channel in enumerate(self.ppg_channels):
            plot = pg.PlotItem(title=channel)
            plot.setLabel('left', 'Value')
            plot.setLabel('bottom', 'Time (s)')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.hideAxis('bottom')

            color = self.channel_colors[i % len(self.channel_colors)]
            curve = plot.plot(pen=pg.mkPen(color=color, width=2))

            self.plots['ppg'].append(plot)
            self.curves['ppg'].append(curve)

        # ACC plots (hidden by default)
        self.plots['acc'] = []
        self.curves['acc'] = []

        for i, channel in enumerate(self.acc_channels):
            plot = pg.PlotItem(title=f"ACC {channel}")
            plot.setLabel('left', 'g')
            plot.setLabel('bottom', 'Time (s)')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.hideAxis('bottom')

            color = self.channel_colors[i % len(self.channel_colors)]
            curve = plot.plot(pen=pg.mkPen(color=color, width=2))

            self.plots['acc'].append(plot)
            self.curves['acc'].append(curve)

        # GYRO plots (hidden by default)
        self.plots['gyro'] = []
        self.curves['gyro'] = []

        for i, channel in enumerate(self.gyro_channels):
            plot = pg.PlotItem(title=f"GYRO {channel}")
            plot.setLabel('left', 'deg/s')
            plot.setLabel('bottom', 'Time (s)')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.hideAxis('bottom')

            color = self.channel_colors[i % len(self.channel_colors)]
            curve = plot.plot(pen=pg.mkPen(color=color, width=2))

            self.plots['gyro'].append(plot)
            self.curves['gyro'].append(curve)

    def on_view_changed(self, view):
        """Handle view change"""
        # Clear current view
        self.plot_widget.clear()

        # Show selected plots
        if view == 'EEG' or view == 'All':
            for i, plot in enumerate(self.plots['eeg']):
                self.plot_widget.addItem(plot, row=i, col=0)
                plot.showAxis('bottom')

        if view == 'PPG':
            for i, plot in enumerate(self.plots['ppg']):
                self.plot_widget.addItem(plot, row=i, col=0)
                plot.showAxis('bottom')

        if view == 'Accelerometer':
            for i, plot in enumerate(self.plots['acc']):
                self.plot_widget.addItem(plot, row=i, col=0)
                plot.showAxis('bottom')

        if view == 'Gyroscope':
            for i, plot in enumerate(self.plots['gyro']):
                self.plot_widget.addItem(plot, row=i, col=0)
                plot.showAxis('bottom')

        # Update plots
        self.update_plots()

    def on_time_scale_changed(self, value):
        """Handle time scale change"""
        self.time_scale_label.setText(f"{value}s")
        self.buffer_size = value * 256  # Assume 256 Hz for EEG

        # Resize buffers
        for i in range(5):
            self.eeg_buffer[i] = deque(list(self.eeg_buffer[i])[-self.buffer_size:], maxlen=self.buffer_size)

        self.eeg_time = deque(list(self.eeg_time)[-self.buffer_size:], maxlen=self.buffer_size)

    def on_eeg_data(self, timestamp, data):
        """Handle incoming EEG data"""
        # Add to buffer
        if self.eeg_time:
            # Use relative time
            rel_time = timestamp - self.eeg_time[0]
        else:
            rel_time = 0.0

        self.eeg_time.append(rel_time)

        for i, value in enumerate(data[:5]):  # 5 channels
            self.eeg_buffer[i].append(value)

        # Update plots
        self.update_plots('eeg')
        self.status_label.setText(f"Receiving EEG data... ({len(self.eeg_time)} samples)")

    def on_ppg_data(self, timestamp, data):
        """Handle incoming PPG data"""
        if self.ppg_time:
            rel_time = timestamp - self.ppg_time[0]
        else:
            rel_time = 0.0

        self.ppg_time.append(rel_time)

        for i, value in enumerate(data[:3]):  # 3 channels
            self.ppg_buffer[i].append(value)

        self.update_plots('ppg')

    def on_acc_data(self, timestamp, data):
        """Handle incoming accelerometer data"""
        if self.acc_time:
            rel_time = timestamp - self.acc_time[0]
        else:
            rel_time = 0.0

        self.acc_time.append(rel_time)

        for i, value in enumerate(data[:3]):  # 3 channels
            self.acc_buffer[i].append(value)

        self.update_plots('acc')

    def on_gyro_data(self, timestamp, data):
        """Handle incoming gyroscope data"""
        if self.gyro_time:
            rel_time = timestamp - self.gyro_time[0]
        else:
            rel_time = 0.0

        self.gyro_time.append(rel_time)

        for i, value in enumerate(data[:3]):  # 3 channels
            self.gyro_buffer[i].append(value)

        self.update_plots('gyro')

    def update_plots(self, data_type=None):
        """Update plot displays"""
        current_view = self.view_combo.currentText()

        # Update EEG plots
        if (data_type == 'eeg' or data_type is None) and (current_view == 'EEG' or current_view == 'All'):
            if len(self.eeg_time) > 0:
                time_array = np.array(self.eeg_time)
                for i, curve in enumerate(self.curves['eeg']):
                    data_array = np.array(self.eeg_buffer[i])
                    curve.setData(time_array, data_array)

                    if self.autoscale_check.isChecked():
                        self.plots['eeg'][i].enableAutoRange(axis='y')

        # Update PPG plots
        if (data_type == 'ppg' or data_type is None) and current_view == 'PPG':
            if len(self.ppg_time) > 0:
                time_array = np.array(self.ppg_time)
                for i, curve in enumerate(self.curves['ppg']):
                    data_array = np.array(self.ppg_buffer[i])
                    curve.setData(time_array, data_array)

                    if self.autoscale_check.isChecked():
                        self.plots['ppg'][i].enableAutoRange(axis='y')

        # Update ACC plots
        if (data_type == 'acc' or data_type is None) and current_view == 'Accelerometer':
            if len(self.acc_time) > 0:
                time_array = np.array(self.acc_time)
                for i, curve in enumerate(self.curves['acc']):
                    data_array = np.array(self.acc_buffer[i])
                    curve.setData(time_array, data_array)

                    if self.autoscale_check.isChecked():
                        self.plots['acc'][i].enableAutoRange(axis='y')

        # Update GYRO plots
        if (data_type == 'gyro' or data_type is None) and current_view == 'Gyroscope':
            if len(self.gyro_time) > 0:
                time_array = np.array(self.gyro_time)
                for i, curve in enumerate(self.curves['gyro']):
                    data_array = np.array(self.gyro_buffer[i])
                    curve.setData(time_array, data_array)

                    if self.autoscale_check.isChecked():
                        self.plots['gyro'][i].enableAutoRange(axis='y')

    def clear_buffers(self):
        """Clear all data buffers"""
        for buffer in self.eeg_buffer:
            buffer.clear()
        for buffer in self.ppg_buffer:
            buffer.clear()
        for buffer in self.acc_buffer:
            buffer.clear()
        for buffer in self.gyro_buffer:
            buffer.clear()

        self.eeg_time.clear()
        self.ppg_time.clear()
        self.acc_time.clear()
        self.gyro_time.clear()

        self.update_plots()
        self.status_label.setText("Buffers cleared")
        logger.info("Data buffers cleared")
