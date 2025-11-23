"""
Frequency Band Power Display Panel
Shows real-time EEG frequency band powers with visual bars
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QProgressBar, QGroupBox, QCheckBox, QPushButton)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)


class BandPowerPanel(QWidget):
    """
    Real-time Frequency Band Power Display

    Shows power in standard EEG frequency bands with visual progress bars
    """

    def __init__(self, lsl_manager):
        super().__init__()
        self.lsl_manager = lsl_manager

        # Frequency bands (Hz)
        self.bands = {
            'Delta': (0.5, 4),
            'Theta': (4, 8),
            'Alpha': (8, 13),
            'Beta': (13, 30),
            'Gamma': (30, 50)
        }

        # Band colors (retro rainbow)
        self.band_colors = {
            'Delta': '#fb9481',   # Salmon
            'Theta': '#ffc991',   # Coral
            'Alpha': '#87d1ac',   # Mint Green (most important)
            'Beta': '#069aa4',    # Aqua Teal
            'Gamma': '#f37986'    # Rose
        }

        # Data buffers for power calculation
        self.buffer_size = 512  # 2 seconds at 256 Hz
        self.eeg_buffer = []
        self.sample_rate = 256

        # Band power values (per channel)
        self.band_powers = {band: [0, 0, 0, 0, 0] for band in self.bands.keys()}

        # Baseline values for normalization
        self.baseline_powers = None
        self.use_baseline = False

        # Register callback
        self.lsl_manager.register_callback('eeg', self.on_eeg_data)

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.setInterval(500)  # Update every 500ms

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Header
        header = QLabel("Frequency Band Power")
        header.setProperty("class", "h2")
        layout.addWidget(header)

        # Channel selection
        channel_layout = QHBoxLayout()
        channel_layout.addWidget(QLabel("Display Channel:"))

        self.channel_buttons = []
        channels = ['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX', 'Average']

        for i, ch in enumerate(channels):
            btn = QPushButton(ch)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self.set_display_channel(idx))
            channel_layout.addWidget(btn)
            self.channel_buttons.append(btn)

        # Default to AF7 (frontal, good for general use)
        self.channel_buttons[1].setChecked(True)
        self.display_channel = 1

        channel_layout.addStretch()
        layout.addLayout(channel_layout)

        # Controls
        controls_layout = QHBoxLayout()

        self.baseline_btn = QPushButton("📍 Set Baseline")
        self.baseline_btn.clicked.connect(self.set_baseline)
        controls_layout.addWidget(self.baseline_btn)

        self.use_baseline_check = QCheckBox("Normalize to Baseline")
        self.use_baseline_check.stateChanged.connect(self.toggle_baseline)
        controls_layout.addWidget(self.use_baseline_check)

        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_baseline)
        controls_layout.addWidget(self.reset_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Band power displays
        bands_group = QGroupBox("EEG Frequency Bands")
        bands_layout = QVBoxLayout()

        self.band_widgets = {}

        for band_name, (low, high) in self.bands.items():
            # Band container
            band_container = QHBoxLayout()

            # Band name and frequency
            label = QLabel(f"{band_name}\n({low}-{high} Hz)")
            label.setMinimumWidth(100)
            label.setProperty("class", "h3")
            band_container.addWidget(label)

            # Progress bar
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(0)
            progress.setTextVisible(True)
            progress.setFormat("%v%")

            # Set custom color
            color = self.band_colors[band_name]
            progress.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid rgba(135, 209, 172, 0.3);
                    border-radius: 6px;
                    background: rgba(2, 92, 127, 0.3);
                    text-align: center;
                    color: #ffffff;
                    font-weight: bold;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 {color}, stop:1 rgba(255, 255, 255, 0.3));
                    border-radius: 5px;
                }}
            """)

            band_container.addWidget(progress)

            # Power value label
            value_label = QLabel("0.00 µV²")
            value_label.setMinimumWidth(120)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            band_container.addWidget(value_label)

            bands_layout.addLayout(band_container)

            # Store widgets
            self.band_widgets[band_name] = {
                'progress': progress,
                'label': value_label
            }

        bands_group.setLayout(bands_layout)
        layout.addWidget(bands_group)

        # Status
        self.status_label = QLabel("Collecting data...")
        self.status_label.setProperty("class", "muted")
        layout.addWidget(self.status_label)

        # Band ratios (useful metrics)
        ratios_group = QGroupBox("Band Ratios")
        ratios_layout = QVBoxLayout()

        self.ratio_labels = {}
        ratios = [
            ('Theta/Alpha', 'Relaxation indicator'),
            ('Beta/Alpha', 'Alertness indicator'),
            ('Alpha/Delta', 'Arousal level')
        ]

        for ratio_name, description in ratios:
            ratio_layout = QHBoxLayout()
            name_label = QLabel(f"{ratio_name}:")
            name_label.setMinimumWidth(120)
            ratio_layout.addWidget(name_label)

            value_label = QLabel("0.00")
            value_label.setMinimumWidth(80)
            ratio_layout.addWidget(value_label)

            desc_label = QLabel(f"({description})")
            desc_label.setProperty("class", "muted")
            ratio_layout.addWidget(desc_label)

            ratio_layout.addStretch()
            ratios_layout.addLayout(ratio_layout)

            self.ratio_labels[ratio_name] = value_label

        ratios_group.setLayout(ratios_layout)
        layout.addWidget(ratios_group)

        layout.addStretch()
        self.setLayout(layout)

    def set_display_channel(self, channel_idx):
        """Set which channel to display"""
        # Uncheck all other buttons
        for i, btn in enumerate(self.channel_buttons):
            btn.setChecked(i == channel_idx)

        self.display_channel = channel_idx
        logger.info(f"Display channel set to: {channel_idx}")

    def on_eeg_data(self, timestamp, data):
        """Handle incoming EEG data"""
        # Add to buffer
        self.eeg_buffer.append(data[:5])  # First 5 channels

        # Keep buffer size limited
        if len(self.eeg_buffer) > self.buffer_size:
            self.eeg_buffer.pop(0)

        # Start update timer if enough data
        if len(self.eeg_buffer) >= 256 and not self.update_timer.isActive():
            self.update_timer.start()

    def compute_band_power(self, data, band_range):
        """
        Compute power in a specific frequency band

        Args:
            data: 1D array of EEG data
            band_range: Tuple of (low_freq, high_freq)

        Returns:
            Power in the band (µV²)
        """
        # Compute power spectral density using Welch's method
        try:
            freqs, psd = signal.welch(data, fs=self.sample_rate,
                                     nperseg=min(256, len(data)),
                                     scaling='density')

            # Find frequencies in band
            idx_band = np.logical_and(freqs >= band_range[0], freqs <= band_range[1])

            # Integrate power in band
            band_power = np.trapz(psd[idx_band], freqs[idx_band])

            return band_power

        except Exception as e:
            logger.error(f"Error computing band power: {e}")
            return 0.0

    def update_display(self):
        """Update band power display"""
        if len(self.eeg_buffer) < 256:
            return

        try:
            # Convert buffer to numpy array
            buffer_array = np.array(self.eeg_buffer)

            # Get channel data
            if self.display_channel == 5:  # Average
                channel_data = np.mean(buffer_array, axis=1)
            else:
                channel_data = buffer_array[:, self.display_channel]

            # Compute power for each band
            max_power = 0.0

            for band_name, band_range in self.bands.items():
                power = self.compute_band_power(channel_data, band_range)

                # Store power
                if self.display_channel < 5:
                    self.band_powers[band_name][self.display_channel] = power

                # Normalize to baseline if enabled
                if self.use_baseline and self.baseline_powers is not None:
                    baseline = self.baseline_powers.get(band_name, 1.0)
                    if baseline > 0:
                        power_normalized = (power / baseline) * 100
                    else:
                        power_normalized = 100
                else:
                    power_normalized = power * 100  # Scale for display

                # Track max for scaling
                max_power = max(max_power, power_normalized)

                # Update widgets
                widgets = self.band_widgets[band_name]
                widgets['progress'].setValue(int(min(power_normalized, 100)))
                widgets['label'].setText(f"{power:.2f} µV²")

            # Compute band ratios
            alpha_power = self.band_powers['Alpha'][self.display_channel if self.display_channel < 5 else 0]
            theta_power = self.band_powers['Theta'][self.display_channel if self.display_channel < 5 else 0]
            beta_power = self.band_powers['Beta'][self.display_channel if self.display_channel < 5 else 0]
            delta_power = self.band_powers['Delta'][self.display_channel if self.display_channel < 5 else 0]

            if alpha_power > 0:
                theta_alpha = theta_power / alpha_power
                beta_alpha = beta_power / alpha_power
                self.ratio_labels['Theta/Alpha'].setText(f"{theta_alpha:.2f}")
                self.ratio_labels['Beta/Alpha'].setText(f"{beta_alpha:.2f}")

            if delta_power > 0:
                alpha_delta = alpha_power / delta_power
                self.ratio_labels['Alpha/Delta'].setText(f"{alpha_delta:.2f}")

            # Update status
            n_samples = len(self.eeg_buffer)
            self.status_label.setText(f"Active ({n_samples} samples, updating every 500ms)")

        except Exception as e:
            logger.error(f"Error updating band power display: {e}")

    def set_baseline(self):
        """Set current values as baseline"""
        if len(self.eeg_buffer) < 256:
            self.status_label.setText("Not enough data for baseline. Keep recording...")
            return

        # Store current band powers as baseline
        self.baseline_powers = {}

        buffer_array = np.array(self.eeg_buffer)

        if self.display_channel == 5:  # Average
            channel_data = np.mean(buffer_array, axis=1)
        else:
            channel_data = buffer_array[:, self.display_channel]

        for band_name, band_range in self.bands.items():
            power = self.compute_band_power(channel_data, band_range)
            self.baseline_powers[band_name] = power

        self.status_label.setText("✓ Baseline set! Powers now shown relative to baseline.")
        logger.info(f"Baseline set: {self.baseline_powers}")

    def toggle_baseline(self, state):
        """Toggle baseline normalization"""
        self.use_baseline = state == Qt.CheckState.Checked.value

        if self.use_baseline and self.baseline_powers is None:
            self.status_label.setText("⚠ No baseline set. Click 'Set Baseline' first.")
            self.use_baseline_check.setChecked(False)

    def reset_baseline(self):
        """Reset baseline"""
        self.baseline_powers = None
        self.use_baseline = False
        self.use_baseline_check.setChecked(False)
        self.status_label.setText("Baseline reset")
        logger.info("Baseline reset")

    def start(self):
        """Start band power monitoring"""
        if not self.update_timer.isActive():
            self.update_timer.start()

    def stop(self):
        """Stop band power monitoring"""
        self.update_timer.stop()
