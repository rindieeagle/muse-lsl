"""
Settings and Configuration Panel
Provides filter configuration and application settings
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGroupBox, QDoubleSpinBox, QCheckBox,
                             QComboBox, QLineEdit, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class SettingsPanel(QWidget):
    """
    Settings and Configuration Panel

    Manages filters, recording settings, and application preferences
    """

    settings_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.settings = self.load_default_settings()
        self.init_ui()

    def load_default_settings(self):
        """Load default settings"""
        return {
            'filters': {
                'highpass_enabled': False,
                'highpass_freq': 1.0,
                'lowpass_enabled': False,
                'lowpass_freq': 40.0,
                'notch_enabled': True,
                'notch_freq': 60.0,
            },
            'recording': {
                'output_dir': str(Path.home() / 'MuseRecordings'),
                'auto_save': True,
                'save_interval': 5,
                'include_markers': True,
            },
            'display': {
                'update_rate': 30,
                'theme': 'retro_rainbow',
            },
            'lab_recorder': {
                'path': '',
                'auto_launch': False,
            }
        }

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Header
        header = QLabel("Settings & Configuration")
        header.setProperty("class", "h2")
        layout.addWidget(header)

        # Filter Settings
        filters_group = self.create_filter_settings()
        layout.addWidget(filters_group)

        # Recording Settings
        recording_group = self.create_recording_settings()
        layout.addWidget(recording_group)

        # Lab Recorder Settings
        labrecorder_group = self.create_labrecorder_settings()
        layout.addWidget(labrecorder_group)

        # Display Settings
        display_group = self.create_display_settings()
        layout.addWidget(display_group)

        # Action Buttons
        actions_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.clicked.connect(self.save_settings)
        actions_layout.addWidget(self.save_btn)

        self.load_btn = QPushButton("📂 Load Settings")
        self.load_btn.clicked.connect(self.load_settings)
        actions_layout.addWidget(self.load_btn)

        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        actions_layout.addWidget(self.reset_btn)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        layout.addStretch()
        self.setLayout(layout)

    def create_filter_settings(self):
        """Create filter settings group"""
        group = QGroupBox("Signal Filters")
        layout = QVBoxLayout()

        # Highpass filter
        hp_layout = QHBoxLayout()
        self.hp_enabled = QCheckBox("Highpass Filter")
        self.hp_enabled.setChecked(self.settings['filters']['highpass_enabled'])
        hp_layout.addWidget(self.hp_enabled)

        hp_layout.addWidget(QLabel("Cutoff:"))
        self.hp_freq = QDoubleSpinBox()
        self.hp_freq.setRange(0.1, 50.0)
        self.hp_freq.setValue(self.settings['filters']['highpass_freq'])
        self.hp_freq.setSuffix(" Hz")
        self.hp_freq.setDecimals(1)
        hp_layout.addWidget(self.hp_freq)

        hp_layout.addStretch()
        layout.addLayout(hp_layout)

        # Lowpass filter
        lp_layout = QHBoxLayout()
        self.lp_enabled = QCheckBox("Lowpass Filter")
        self.lp_enabled.setChecked(self.settings['filters']['lowpass_enabled'])
        lp_layout.addWidget(self.lp_enabled)

        lp_layout.addWidget(QLabel("Cutoff:"))
        self.lp_freq = QDoubleSpinBox()
        self.lp_freq.setRange(1.0, 200.0)
        self.lp_freq.setValue(self.settings['filters']['lowpass_freq'])
        self.lp_freq.setSuffix(" Hz")
        self.lp_freq.setDecimals(1)
        lp_layout.addWidget(self.lp_freq)

        lp_layout.addStretch()
        layout.addLayout(lp_layout)

        # Notch filter
        notch_layout = QHBoxLayout()
        self.notch_enabled = QCheckBox("Notch Filter (50/60 Hz)")
        self.notch_enabled.setChecked(self.settings['filters']['notch_enabled'])
        notch_layout.addWidget(self.notch_enabled)

        notch_layout.addWidget(QLabel("Frequency:"))
        self.notch_freq = QComboBox()
        self.notch_freq.addItems(['50 Hz', '60 Hz'])
        self.notch_freq.setCurrentText(f"{self.settings['filters']['notch_freq']:.0f} Hz")
        notch_layout.addWidget(self.notch_freq)

        notch_layout.addStretch()
        layout.addLayout(notch_layout)

        # Filter info
        info_label = QLabel(
            "Note: Filters are applied in real-time for visualization only. "
            "Raw data is always recorded."
        )
        info_label.setWordWrap(True)
        info_label.setProperty("class", "muted")
        layout.addWidget(info_label)

        group.setLayout(layout)
        return group

    def create_recording_settings(self):
        """Create recording settings group"""
        group = QGroupBox("Recording Settings")
        layout = QVBoxLayout()

        # Output directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Output Directory:"))

        self.output_dir = QLineEdit()
        self.output_dir.setText(self.settings['recording']['output_dir'])
        dir_layout.addWidget(self.output_dir)

        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self.browse_output_dir)
        dir_layout.addWidget(browse_btn)

        layout.addLayout(dir_layout)

        # Auto-save
        autosave_layout = QHBoxLayout()
        self.auto_save = QCheckBox("Auto-save during recording")
        self.auto_save.setChecked(self.settings['recording']['auto_save'])
        autosave_layout.addWidget(self.auto_save)

        autosave_layout.addWidget(QLabel("Interval:"))
        self.save_interval = QDoubleSpinBox()
        self.save_interval.setRange(1, 60)
        self.save_interval.setValue(self.settings['recording']['save_interval'])
        self.save_interval.setSuffix(" seconds")
        autosave_layout.addWidget(self.save_interval)

        autosave_layout.addStretch()
        layout.addLayout(autosave_layout)

        # Include markers
        self.include_markers = QCheckBox("Include event markers in recordings")
        self.include_markers.setChecked(self.settings['recording']['include_markers'])
        layout.addWidget(self.include_markers)

        group.setLayout(layout)
        return group

    def create_labrecorder_settings(self):
        """Create Lab Recorder settings group"""
        group = QGroupBox("Lab Recorder Integration")
        layout = QVBoxLayout()

        # Lab Recorder path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Lab Recorder Path:"))

        self.labrecorder_path = QLineEdit()
        self.labrecorder_path.setText(self.settings['lab_recorder']['path'])
        self.labrecorder_path.setPlaceholderText("Leave empty to auto-detect")
        path_layout.addWidget(self.labrecorder_path)

        browse_labrecorder_btn = QPushButton("📁 Browse")
        browse_labrecorder_btn.clicked.connect(self.browse_labrecorder_path)
        path_layout.addWidget(browse_labrecorder_btn)

        layout.addLayout(path_layout)

        # Auto-launch
        self.auto_launch = QCheckBox("Auto-launch Lab Recorder when starting streaming")
        self.auto_launch.setChecked(self.settings['lab_recorder']['auto_launch'])
        layout.addWidget(self.auto_launch)

        # Test button
        test_btn = QPushButton("🧪 Test Lab Recorder")
        test_btn.clicked.connect(self.test_labrecorder)
        layout.addWidget(test_btn)

        group.setLayout(layout)
        return group

    def create_display_settings(self):
        """Create display settings group"""
        group = QGroupBox("Display Settings")
        layout = QVBoxLayout()

        # Update rate
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("Visualization Update Rate:"))

        self.update_rate = QDoubleSpinBox()
        self.update_rate.setRange(1, 60)
        self.update_rate.setValue(self.settings['display']['update_rate'])
        self.update_rate.setSuffix(" FPS")
        rate_layout.addWidget(self.update_rate)

        rate_layout.addStretch()
        layout.addLayout(rate_layout)

        # Theme (future expansion)
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Retro Rainbow'])
        self.theme_combo.setCurrentText('Retro Rainbow')
        self.theme_combo.setEnabled(False)  # Only one theme for now
        theme_layout.addWidget(self.theme_combo)

        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        group.setLayout(layout)
        return group

    def browse_output_dir(self):
        """Browse for output directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_dir.text()
        )

        if dir_path:
            self.output_dir.setText(dir_path)

    def browse_labrecorder_path(self):
        """Browse for Lab Recorder executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Lab Recorder Executable",
            "",
            "Executable Files (*.exe *.app *.AppImage);;All Files (*)"
        )

        if file_path:
            self.labrecorder_path.setText(file_path)

    def test_labrecorder(self):
        """Test Lab Recorder integration"""
        from ..backend.recorder import LabRecorderIntegration

        integration = LabRecorderIntegration()

        # Try custom path first
        custom_path = self.labrecorder_path.text()
        if custom_path:
            path = Path(custom_path)
        else:
            path = integration.find_lab_recorder()

        if path and path.exists():
            QMessageBox.information(
                self,
                "Lab Recorder Found",
                f"Lab Recorder found at:\n{path}\n\nIntegration ready!"
            )
        else:
            QMessageBox.warning(
                self,
                "Lab Recorder Not Found",
                "Lab Recorder could not be found.\n\n"
                "Please install Lab Recorder or specify the path manually."
            )

    def get_settings(self):
        """Get current settings from UI"""
        return {
            'filters': {
                'highpass_enabled': self.hp_enabled.isChecked(),
                'highpass_freq': self.hp_freq.value(),
                'lowpass_enabled': self.lp_enabled.isChecked(),
                'lowpass_freq': self.lp_freq.value(),
                'notch_enabled': self.notch_enabled.isChecked(),
                'notch_freq': float(self.notch_freq.currentText().split()[0]),
            },
            'recording': {
                'output_dir': self.output_dir.text(),
                'auto_save': self.auto_save.isChecked(),
                'save_interval': self.save_interval.value(),
                'include_markers': self.include_markers.isChecked(),
            },
            'display': {
                'update_rate': self.update_rate.value(),
                'theme': 'retro_rainbow',
            },
            'lab_recorder': {
                'path': self.labrecorder_path.text(),
                'auto_launch': self.auto_launch.isChecked(),
            }
        }

    def save_settings(self):
        """Save settings to file"""
        settings_dir = Path.home() / '.musegui'
        settings_dir.mkdir(exist_ok=True)
        settings_file = settings_dir / 'settings.json'

        try:
            self.settings = self.get_settings()

            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)

            logger.info(f"Settings saved to {settings_file}")
            QMessageBox.information(
                self,
                "Settings Saved",
                f"Settings saved successfully to:\n{settings_file}"
            )

            self.settings_changed.emit(self.settings)

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save settings:\n{str(e)}"
            )

    def load_settings(self):
        """Load settings from file"""
        settings_dir = Path.home() / '.musegui'
        settings_file = settings_dir / 'settings.json'

        if not settings_file.exists():
            QMessageBox.information(
                self,
                "No Settings Found",
                "No saved settings found. Using defaults."
            )
            return

        try:
            with open(settings_file, 'r') as f:
                self.settings = json.load(f)

            # Update UI
            self.update_ui_from_settings()

            logger.info(f"Settings loaded from {settings_file}")
            QMessageBox.information(
                self,
                "Settings Loaded",
                "Settings loaded successfully!"
            )

            self.settings_changed.emit(self.settings)

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            QMessageBox.critical(
                self,
                "Load Failed",
                f"Failed to load settings:\n{str(e)}"
            )

    def update_ui_from_settings(self):
        """Update UI elements from settings"""
        # Filters
        self.hp_enabled.setChecked(self.settings['filters']['highpass_enabled'])
        self.hp_freq.setValue(self.settings['filters']['highpass_freq'])
        self.lp_enabled.setChecked(self.settings['filters']['lowpass_enabled'])
        self.lp_freq.setValue(self.settings['filters']['lowpass_freq'])
        self.notch_enabled.setChecked(self.settings['filters']['notch_enabled'])
        self.notch_freq.setCurrentText(f"{self.settings['filters']['notch_freq']:.0f} Hz")

        # Recording
        self.output_dir.setText(self.settings['recording']['output_dir'])
        self.auto_save.setChecked(self.settings['recording']['auto_save'])
        self.save_interval.setValue(self.settings['recording']['save_interval'])
        self.include_markers.setChecked(self.settings['recording']['include_markers'])

        # Display
        self.update_rate.setValue(self.settings['display']['update_rate'])

        # Lab Recorder
        self.labrecorder_path.setText(self.settings['lab_recorder']['path'])
        self.auto_launch.setChecked(self.settings['lab_recorder']['auto_launch'])

    def reset_to_defaults(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings = self.load_default_settings()
            self.update_ui_from_settings()
            self.settings_changed.emit(self.settings)
            logger.info("Settings reset to defaults")
