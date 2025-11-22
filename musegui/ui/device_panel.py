"""
Device Discovery and Connection Panel
Provides UI for discovering and connecting to Muse devices
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QListWidgetItem, QGroupBox,
                             QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class DeviceDiscoveryThread(QThread):
    """Thread for discovering Muse devices without blocking UI"""

    devices_found = pyqtSignal(list)
    discovery_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, backend='auto'):
        super().__init__()
        self.backend = backend

    def run(self):
        """Run device discovery"""
        try:
            from muselsl import list_muses

            logger.info(f"Starting device discovery (backend: {self.backend})")
            devices = list_muses(backend=self.backend)

            # Format device list
            device_list = []
            for device in devices:
                if isinstance(device, dict):
                    device_list.append({
                        'name': device.get('name', 'Unknown'),
                        'address': device.get('address', 'Unknown')
                    })
                else:
                    # Handle different backend formats
                    device_list.append({
                        'name': str(device),
                        'address': str(device)
                    })

            self.devices_found.emit(device_list)
            logger.info(f"Found {len(device_list)} device(s)")

        except Exception as e:
            logger.error(f"Device discovery error: {e}")
            self.error_occurred.emit(str(e))

        finally:
            self.discovery_complete.emit()


class DeviceConnectionThread(QThread):
    """Thread for connecting to Muse device"""

    connection_success = pyqtSignal()
    connection_failed = pyqtSignal(str)
    progress_update = pyqtSignal(str)

    def __init__(self, address, backend='auto', preset='p21'):
        super().__init__()
        self.address = address
        self.backend = backend
        self.preset = preset

    def run(self):
        """Connect to device"""
        try:
            from muselsl import stream
            import multiprocessing

            self.progress_update.emit("Connecting to device...")
            logger.info(f"Connecting to device: {self.address}")

            # Start streaming in a separate process
            self.stream_process = multiprocessing.Process(
                target=stream,
                args=(self.address,),
                kwargs={
                    'backend': self.backend,
                    'preset': self.preset,
                    'ppg_enabled': True,
                    'acc_enabled': True,
                    'gyro_enabled': True
                }
            )

            self.stream_process.start()
            self.progress_update.emit("Streaming started!")

            logger.info("Device connected and streaming")
            self.connection_success.emit()

        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connection_failed.emit(str(e))


class DevicePanel(QWidget):
    """
    Device Discovery and Connection Panel

    Allows users to discover and connect to Muse devices
    """

    device_connected = pyqtSignal(str, str)  # address, name
    device_disconnected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.discovery_thread = None
        self.connection_thread = None
        self.stream_process = None
        self.connected_device = None

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Header
        header = QLabel("Device Connection")
        header.setProperty("class", "h2")
        layout.addWidget(header)

        # Backend selection
        backend_group = QGroupBox("Bluetooth Backend")
        backend_layout = QHBoxLayout()

        self.backend_label = QLabel("Backend:")
        self.backend_combo = self.create_combo_box()
        self.backend_combo.addItems(['auto', 'bleak', 'gatt', 'bgapi'])
        self.backend_combo.setCurrentText('auto')

        backend_layout.addWidget(self.backend_label)
        backend_layout.addWidget(self.backend_combo)
        backend_layout.addStretch()
        backend_group.setLayout(backend_layout)
        layout.addWidget(backend_group)

        # Device discovery section
        discovery_group = QGroupBox("Available Devices")
        discovery_layout = QVBoxLayout()

        # Search button
        button_layout = QHBoxLayout()
        self.search_btn = QPushButton("🔍 Search for Devices")
        self.search_btn.setProperty("class", "primary")
        self.search_btn.clicked.connect(self.start_discovery)
        button_layout.addWidget(self.search_btn)
        button_layout.addStretch()
        discovery_layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_bar.setVisible(False)
        discovery_layout.addWidget(self.progress_bar)

        # Device list
        self.device_list = QListWidget()
        self.device_list.setMinimumHeight(150)
        self.device_list.itemDoubleClicked.connect(self.on_device_double_clicked)
        discovery_layout.addWidget(self.device_list)

        # Status label
        self.status_label = QLabel("No devices found. Click 'Search' to discover Muse devices.")
        self.status_label.setProperty("class", "muted")
        self.status_label.setWordWrap(True)
        discovery_layout.addWidget(self.status_label)

        discovery_group.setLayout(discovery_layout)
        layout.addWidget(discovery_group)

        # Connection controls
        connection_group = QGroupBox("Connection")
        connection_layout = QVBoxLayout()

        # Connect button
        button_row = QHBoxLayout()
        self.connect_btn = QPushButton("⚡ Connect to Selected Device")
        self.connect_btn.setProperty("class", "success")
        self.connect_btn.setEnabled(False)
        self.connect_btn.clicked.connect(self.connect_device)
        button_row.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton("🔌 Disconnect")
        self.disconnect_btn.setProperty("class", "danger")
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        button_row.addWidget(self.disconnect_btn)

        connection_layout.addLayout(button_row)

        # Connection status
        status_row = QHBoxLayout()
        status_row.addWidget(QLabel("Status:"))
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setProperty("class", "status-disconnected")
        status_row.addWidget(self.connection_status)
        status_row.addStretch()
        connection_layout.addLayout(status_row)

        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)

        layout.addStretch()
        self.setLayout(layout)

    def create_combo_box(self):
        """Create styled combo box"""
        from PyQt6.QtWidgets import QComboBox
        combo = QComboBox()
        combo.setMinimumHeight(36)
        return combo

    def start_discovery(self):
        """Start device discovery"""
        if self.discovery_thread and self.discovery_thread.isRunning():
            logger.warning("Discovery already in progress")
            return

        # Clear previous results
        self.device_list.clear()
        self.status_label.setText("Searching for Muse devices...")
        self.progress_bar.setVisible(True)
        self.search_btn.setEnabled(False)

        # Start discovery thread
        backend = self.backend_combo.currentText()
        self.discovery_thread = DeviceDiscoveryThread(backend=backend)
        self.discovery_thread.devices_found.connect(self.on_devices_found)
        self.discovery_thread.discovery_complete.connect(self.on_discovery_complete)
        self.discovery_thread.error_occurred.connect(self.on_discovery_error)
        self.discovery_thread.start()

    def on_devices_found(self, devices):
        """Handle discovered devices"""
        self.device_list.clear()

        for device in devices:
            item = QListWidgetItem(f"{device['name']} ({device['address']})")
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.device_list.addItem(item)

        if devices:
            self.status_label.setText(f"Found {len(devices)} device(s). Double-click or select and click Connect.")
            self.connect_btn.setEnabled(True)
        else:
            self.status_label.setText("No devices found. Make sure your Muse is powered on and nearby.")

    def on_discovery_complete(self):
        """Handle discovery completion"""
        self.progress_bar.setVisible(False)
        self.search_btn.setEnabled(True)

    def on_discovery_error(self, error):
        """Handle discovery error"""
        self.status_label.setText(f"Error: {error}")
        self.status_label.setProperty("class", "status-error")
        QMessageBox.critical(self, "Discovery Error", f"Failed to discover devices:\n{error}")

    def on_device_double_clicked(self, item):
        """Handle device double-click"""
        self.connect_device()

    def connect_device(self):
        """Connect to selected device"""
        selected_items = self.device_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Device Selected", "Please select a device to connect.")
            return

        device = selected_items[0].data(Qt.ItemDataRole.UserRole)
        address = device['address']
        name = device['name']

        # Confirm connection
        reply = QMessageBox.question(
            self,
            "Connect to Device",
            f"Connect to {name}?\n\nThis will start streaming EEG, PPG, accelerometer, and gyroscope data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Start connection
        self.status_label.setText(f"Connecting to {name}...")
        self.connect_btn.setEnabled(False)

        backend = self.backend_combo.currentText()
        self.connection_thread = DeviceConnectionThread(address, backend=backend)
        self.connection_thread.connection_success.connect(lambda: self.on_connection_success(address, name))
        self.connection_thread.connection_failed.connect(self.on_connection_failed)
        self.connection_thread.progress_update.connect(self.status_label.setText)
        self.connection_thread.start()

    def on_connection_success(self, address, name):
        """Handle successful connection"""
        self.connected_device = {'address': address, 'name': name}
        self.connection_status.setText(f"Connected to {name}")
        self.connection_status.setProperty("class", "status-connected")
        self.connection_status.style().unpolish(self.connection_status)
        self.connection_status.style().polish(self.connection_status)

        self.disconnect_btn.setEnabled(True)
        self.connect_btn.setEnabled(False)
        self.search_btn.setEnabled(False)

        self.device_connected.emit(address, name)

        QMessageBox.information(
            self,
            "Connected",
            f"Successfully connected to {name}!\n\nLSL streams are now available."
        )

    def on_connection_failed(self, error):
        """Handle connection failure"""
        self.status_label.setText(f"Connection failed: {error}")
        self.connect_btn.setEnabled(True)

        QMessageBox.critical(
            self,
            "Connection Failed",
            f"Failed to connect to device:\n{error}\n\nPlease try again."
        )

    def disconnect_device(self):
        """Disconnect from device"""
        if self.connected_device:
            reply = QMessageBox.question(
                self,
                "Disconnect",
                f"Disconnect from {self.connected_device['name']}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                return

        # Stop streaming
        if self.connection_thread and hasattr(self.connection_thread, 'stream_process'):
            try:
                self.connection_thread.stream_process.terminate()
                self.connection_thread.stream_process.join(timeout=2)
            except:
                pass

        self.connected_device = None
        self.connection_status.setText("Disconnected")
        self.connection_status.setProperty("class", "status-disconnected")
        self.connection_status.style().unpolish(self.connection_status)
        self.connection_status.style().polish(self.connection_status)

        self.disconnect_btn.setEnabled(False)
        self.connect_btn.setEnabled(len(self.device_list.selectedItems()) > 0)
        self.search_btn.setEnabled(True)
        self.status_label.setText("Disconnected. Search for devices to reconnect.")

        self.device_disconnected.emit()

    def is_connected(self):
        """Check if device is connected"""
        return self.connected_device is not None
