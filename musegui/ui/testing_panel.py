"""
Testing and Diagnostics Panel
Provides built-in testing and troubleshooting tools
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGroupBox, QTextEdit, QProgressBar,
                             QListWidget, QListWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor
import logging
import platform
import sys
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemTestThread(QThread):
    """Thread for running system tests"""

    test_started = pyqtSignal(str)
    test_completed = pyqtSignal(str, bool, str)
    all_tests_complete = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.results = {}

    def run(self):
        """Run all system tests"""
        tests = [
            ('Python Version', self.test_python_version),
            ('Dependencies', self.test_dependencies),
            ('Bluetooth', self.test_bluetooth),
            ('LSL', self.test_lsl),
            ('UDP Socket', self.test_udp),
            ('Muse Device Detection', self.test_device_detection),
        ]

        for test_name, test_func in tests:
            self.test_started.emit(test_name)

            try:
                success, message = test_func()
                self.results[test_name] = {'success': success, 'message': message}
                self.test_completed.emit(test_name, success, message)
            except Exception as e:
                self.results[test_name] = {'success': False, 'message': str(e)}
                self.test_completed.emit(test_name, False, str(e))

        self.all_tests_complete.emit(self.results)

    def test_python_version(self):
        """Test Python version"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 7:
            return True, f"Python {version.major}.{version.minor}.{version.micro}"
        else:
            return False, f"Python {version.major}.{version.minor} (3.7+ required)"

    def test_dependencies(self):
        """Test required dependencies"""
        required = ['pylsl', 'numpy', 'PyQt6', 'pyqtgraph', 'bleak']
        missing = []

        for module in required:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)

        if not missing:
            return True, f"All dependencies installed ({len(required)} checked)"
        else:
            return False, f"Missing: {', '.join(missing)}"

    def test_bluetooth(self):
        """Test Bluetooth availability"""
        try:
            system = platform.system()

            if system == 'Linux':
                import subprocess
                result = subprocess.run(['hciconfig'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'hci0' in result.stdout:
                    return True, "Bluetooth adapter detected"
                else:
                    return False, "No Bluetooth adapter found"

            elif system == 'Windows':
                # On Windows, check if bleak can initialize
                import bleak
                return True, "Bluetooth support available (bleak)"

            elif system == 'Darwin':
                # macOS has built-in Bluetooth
                return True, "Bluetooth support available (macOS)"

            else:
                return False, f"Unsupported platform: {system}"

        except Exception as e:
            return False, f"Bluetooth test failed: {str(e)}"

    def test_lsl(self):
        """Test LSL functionality"""
        try:
            from pylsl import StreamInfo, StreamOutlet, resolve_streams, local_clock

            # Create a test stream
            info = StreamInfo('TestStream', 'EEG', 1, 100, 'float32', 'test123')
            outlet = StreamOutlet(info)

            # Try to resolve it
            streams = resolve_streams(1.0)

            # Clean up
            del outlet

            return True, f"LSL working (found {len(streams)} stream(s))"

        except Exception as e:
            return False, f"LSL test failed: {str(e)}"

    def test_udp(self):
        """Test UDP socket functionality"""
        try:
            import socket

            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('127.0.0.1', 0))  # Bind to any available port

            # Get port
            port = sock.getsockname()[1]

            # Clean up
            sock.close()

            return True, f"UDP socket test passed (port {port})"

        except Exception as e:
            return False, f"UDP test failed: {str(e)}"

    def test_device_detection(self):
        """Test Muse device detection"""
        try:
            from muselsl import list_muses

            devices = list_muses(backend='auto', timeout=5.0)

            if devices:
                return True, f"Found {len(devices)} Muse device(s)"
            else:
                return True, "No devices found (test passed, but no devices nearby)"

        except Exception as e:
            return False, f"Device detection failed: {str(e)}"


class TestingPanel(QWidget):
    """
    Testing and Diagnostics Panel

    Provides system tests and troubleshooting tools
    """

    def __init__(self):
        super().__init__()
        self.test_thread = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Header
        header = QLabel("Testing & Diagnostics")
        header.setProperty("class", "h2")
        layout.addWidget(header)

        # System Tests Section
        tests_group = QGroupBox("System Tests")
        tests_layout = QVBoxLayout()

        # Description
        desc_label = QLabel(
            "Run comprehensive system tests to verify that all components "
            "are working correctly. This will check Python, dependencies, "
            "Bluetooth, LSL, UDP, and device detection."
        )
        desc_label.setWordWrap(True)
        desc_label.setProperty("class", "muted")
        tests_layout.addWidget(desc_label)

        # Run tests button
        run_tests_layout = QHBoxLayout()
        self.run_tests_btn = QPushButton("🧪 Run All Tests")
        self.run_tests_btn.setProperty("class", "primary")
        self.run_tests_btn.clicked.connect(self.run_tests)
        run_tests_layout.addWidget(self.run_tests_btn)
        run_tests_layout.addStretch()
        tests_layout.addLayout(run_tests_layout)

        # Progress bar
        self.test_progress = QProgressBar()
        self.test_progress.setTextVisible(False)
        self.test_progress.setMaximum(0)
        self.test_progress.setVisible(False)
        tests_layout.addWidget(self.test_progress)

        # Results list
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(200)
        tests_layout.addWidget(self.results_list)

        tests_group.setLayout(tests_layout)
        layout.addWidget(tests_group)

        # Diagnostics Section
        diagnostics_group = QGroupBox("Diagnostics Log")
        diagnostics_layout = QVBoxLayout()

        # Log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setMinimumHeight(150)
        self.log_viewer.setPlaceholderText("Diagnostic messages will appear here...")
        diagnostics_layout.addWidget(self.log_viewer)

        # Log controls
        log_controls = QHBoxLayout()

        self.clear_log_btn = QPushButton("🗑 Clear Log")
        self.clear_log_btn.clicked.connect(self.clear_log)
        log_controls.addWidget(self.clear_log_btn)

        self.export_log_btn = QPushButton("💾 Export Log")
        self.export_log_btn.clicked.connect(self.export_log)
        log_controls.addWidget(self.export_log_btn)

        log_controls.addStretch()
        diagnostics_layout.addLayout(log_controls)

        diagnostics_group.setLayout(diagnostics_layout)
        layout.addWidget(diagnostics_group)

        # Troubleshooting Section
        troubleshooting_group = QGroupBox("Troubleshooting")
        troubleshooting_layout = QVBoxLayout()

        troubleshooting_text = QLabel(
            "<b>Common Issues:</b><br><br>"
            "<b>No devices found:</b><br>"
            "• Make sure your Muse is powered on and nearby<br>"
            "• Check that Bluetooth is enabled on your computer<br>"
            "• Try different Bluetooth backends (auto, bleak, gatt)<br>"
            "• On Linux, ensure you have permissions for Bluetooth<br><br>"
            "<b>Connection fails:</b><br>"
            "• Restart your Muse device<br>"
            "• Disconnect from other apps (e.g., Muse app)<br>"
            "• Move closer to the computer<br>"
            "• Try restarting Bluetooth<br><br>"
            "<b>No LSL streams:</b><br>"
            "• Ensure device is connected first<br>"
            "• Check firewall settings<br>"
            "• Verify pylsl is installed correctly<br><br>"
            "<b>UDP not receiving in MATLAB:</b><br>"
            "• Check IP address and port settings<br>"
            "• Ensure MATLAB UDP buffer is configured<br>"
            "• Verify firewall allows UDP traffic<br>"
            "• Try increasing UDP buffer size in MATLAB"
        )
        troubleshooting_text.setWordWrap(True)
        troubleshooting_text.setTextFormat(Qt.TextFormat.RichText)
        troubleshooting_layout.addWidget(troubleshooting_text)

        troubleshooting_group.setLayout(troubleshooting_layout)
        layout.addWidget(troubleshooting_group)

        layout.addStretch()
        self.setLayout(layout)

        # Add initial log message
        self.add_log("Testing panel initialized")

    def run_tests(self):
        """Run all system tests"""
        if self.test_thread and self.test_thread.isRunning():
            logger.warning("Tests already running")
            return

        # Clear previous results
        self.results_list.clear()
        self.test_progress.setVisible(True)
        self.run_tests_btn.setEnabled(False)

        self.add_log("=== Starting System Tests ===")

        # Start test thread
        self.test_thread = SystemTestThread()
        self.test_thread.test_started.connect(self.on_test_started)
        self.test_thread.test_completed.connect(self.on_test_completed)
        self.test_thread.all_tests_complete.connect(self.on_all_tests_complete)
        self.test_thread.start()

    def on_test_started(self, test_name):
        """Handle test start"""
        self.add_log(f"Running test: {test_name}...")

    def on_test_completed(self, test_name, success, message):
        """Handle test completion"""
        # Add to results list
        status = "✓ PASS" if success else "✗ FAIL"
        item = QListWidgetItem(f"{status} - {test_name}: {message}")

        if success:
            item.setForeground(QColor('#87d1ac'))  # Mint Green
        else:
            item.setForeground(QColor('#fb9481'))  # Salmon

        self.results_list.addItem(item)

        # Add to log
        self.add_log(f"{status} {test_name}: {message}")

    def on_all_tests_complete(self, results):
        """Handle all tests completion"""
        self.test_progress.setVisible(False)
        self.run_tests_btn.setEnabled(True)

        # Calculate summary
        total = len(results)
        passed = sum(1 for r in results.values() if r['success'])

        self.add_log(f"=== Tests Complete: {passed}/{total} passed ===")

        # Show summary message
        if passed == total:
            QMessageBox.information(
                self,
                "All Tests Passed",
                f"All {total} system tests passed successfully!\n\n"
                "Your system is ready for Muse EEG recording."
            )
        else:
            failed = total - passed
            QMessageBox.warning(
                self,
                "Some Tests Failed",
                f"{failed} out of {total} tests failed.\n\n"
                "Please check the results and troubleshooting guide."
            )

    def add_log(self, message):
        """Add message to diagnostic log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_viewer.append(f"[{timestamp}] {message}")
        logger.debug(f"Diagnostic log: {message}")

    def clear_log(self):
        """Clear diagnostic log"""
        self.log_viewer.clear()
        self.add_log("Log cleared")

    def export_log(self):
        """Export diagnostic log to file"""
        from PyQt6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Diagnostic Log",
            f"musegui_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_viewer.toPlainText())

                self.add_log(f"Log exported to: {filename}")
                QMessageBox.information(self, "Export Successful", f"Log exported to:\n{filename}")

            except Exception as e:
                self.add_log(f"Export failed: {str(e)}")
                QMessageBox.critical(self, "Export Failed", f"Failed to export log:\n{str(e)}")
