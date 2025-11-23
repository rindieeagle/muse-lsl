"""
Event Markers Panel
UI for managing event markers during recording
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QListWidgetItem, QGroupBox,
                             QLineEdit, QTextEdit, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QColor
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MarkersPanel(QWidget):
    """
    Event Markers Management Panel

    Provides UI for adding, viewing, and exporting event markers
    """

    marker_added = pyqtSignal(str, str)  # label, description

    def __init__(self, marker_manager):
        super().__init__()
        self.marker_manager = marker_manager
        self.keyboard_handler = None

        # Track if shortcuts are active
        self.shortcuts_active = False
        self.shortcuts = []

        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Header
        header = QLabel("Event Markers")
        header.setProperty("class", "h2")
        layout.addWidget(header)

        # Quick marker buttons
        quick_buttons_group = QGroupBox("Quick Markers")
        quick_layout = QVBoxLayout()

        # First row
        row1 = QHBoxLayout()
        self.marker_btn = QPushButton("➕ Marker")
        self.marker_btn.setProperty("class", "primary")
        self.marker_btn.clicked.connect(lambda: self.add_quick_marker("Marker"))
        row1.addWidget(self.marker_btn)

        self.stimulus_btn = QPushButton("🎯 Stimulus")
        self.stimulus_btn.clicked.connect(lambda: self.add_quick_marker("Stimulus"))
        row1.addWidget(self.stimulus_btn)

        self.response_btn = QPushButton("✓ Response")
        self.response_btn.clicked.connect(lambda: self.add_quick_marker("Response"))
        row1.addWidget(self.response_btn)

        self.event_btn = QPushButton("⚡ Event")
        self.event_btn.clicked.connect(lambda: self.add_quick_marker("Event"))
        row1.addWidget(self.event_btn)

        quick_layout.addLayout(row1)

        # Second row - numbered markers
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Numbered:"))
        for i in range(1, 6):
            btn = QPushButton(f"{i}")
            btn.clicked.connect(lambda checked, num=i: self.add_quick_marker(f"Marker_{num}"))
            row2.addWidget(btn)
        row2.addStretch()
        quick_layout.addLayout(row2)

        quick_buttons_group.setLayout(quick_layout)
        layout.addWidget(quick_buttons_group)

        # Custom marker section
        custom_group = QGroupBox("Custom Marker")
        custom_layout = QVBoxLayout()

        # Label input
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("Label:"))
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("e.g., Eyes_Closed")
        label_layout.addWidget(self.label_input)
        custom_layout.addLayout(label_layout)

        # Description input
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Optional description")
        desc_layout.addWidget(self.desc_input)
        custom_layout.addLayout(desc_layout)

        # Add button
        self.add_custom_btn = QPushButton("➕ Add Custom Marker")
        self.add_custom_btn.setProperty("class", "success")
        self.add_custom_btn.clicked.connect(self.add_custom_marker)
        custom_layout.addWidget(self.add_custom_btn)

        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)

        # Keyboard shortcuts info
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout()

        self.shortcuts_enabled_check = QPushButton("⌨️ Enable Keyboard Shortcuts")
        self.shortcuts_enabled_check.setCheckable(True)
        self.shortcuts_enabled_check.clicked.connect(self.toggle_shortcuts)
        shortcuts_layout.addWidget(self.shortcuts_enabled_check)

        shortcuts_info = QLabel(
            "<b>Shortcuts (when enabled):</b><br>"
            "Space - Generic Marker<br>"
            "1-9 - Numbered Markers (Marker_1, Marker_2, etc.)<br>"
            "S - Stimulus<br>"
            "R - Response<br>"
            "E - Event<br>"
            "T - Timestamp"
        )
        shortcuts_info.setWordWrap(True)
        shortcuts_info.setProperty("class", "muted")
        shortcuts_layout.addWidget(shortcuts_info)

        shortcuts_group.setLayout(shortcuts_layout)
        layout.addWidget(shortcuts_group)

        # Marker list
        list_group = QGroupBox("Recorded Markers")
        list_layout = QVBoxLayout()

        self.marker_list = QListWidget()
        self.marker_list.setMinimumHeight(200)
        list_layout.addWidget(self.marker_list)

        # List controls
        list_controls = QHBoxLayout()

        self.clear_btn = QPushButton("🗑 Clear All")
        self.clear_btn.setProperty("class", "danger")
        self.clear_btn.clicked.connect(self.clear_markers)
        list_controls.addWidget(self.clear_btn)

        self.export_csv_btn = QPushButton("💾 Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)
        list_controls.addWidget(self.export_csv_btn)

        self.export_json_btn = QPushButton("💾 Export JSON")
        self.export_json_btn.clicked.connect(self.export_json)
        list_controls.addWidget(self.export_json_btn)

        list_controls.addStretch()
        list_layout.addLayout(list_controls)

        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # Status
        self.status_label = QLabel("Ready to add markers")
        self.status_label.setProperty("class", "muted")
        layout.addWidget(self.status_label)

        # Stats
        self.stats_label = QLabel("Markers: 0")
        layout.addWidget(self.stats_label)

        layout.addStretch()
        self.setLayout(layout)

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_marker_list)
        self.update_timer.setInterval(1000)  # Update every second
        self.update_timer.start()

    def toggle_shortcuts(self, enabled):
        """Toggle keyboard shortcuts"""
        self.shortcuts_active = enabled

        if enabled:
            self.setup_shortcuts()
            self.status_label.setText("⌨️ Keyboard shortcuts ACTIVE - Press Space, 1-9, S, R, E, T")
            self.status_label.setProperty("class", "status-connected")
            logger.info("Keyboard shortcuts enabled")
        else:
            self.remove_shortcuts()
            self.status_label.setText("Keyboard shortcuts disabled")
            self.status_label.setProperty("class", "muted")
            logger.info("Keyboard shortcuts disabled")

        # Force style update
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        from ..backend.event_markers import KeyboardMarkerHandler

        # Create handler if not exists
        if self.keyboard_handler is None:
            self.keyboard_handler = KeyboardMarkerHandler(self.marker_manager)

        # Clear existing shortcuts
        self.remove_shortcuts()

        # Create shortcuts
        shortcut_keys = {
            'Space': 'Marker',
            '1': 'Marker_1', '2': 'Marker_2', '3': 'Marker_3',
            '4': 'Marker_4', '5': 'Marker_5', '6': 'Marker_6',
            '7': 'Marker_7', '8': 'Marker_8', '9': 'Marker_9',
            'S': 'Stimulus',
            'R': 'Response',
            'E': 'Event',
            'T': 'Timestamp'
        }

        for key, label in shortcut_keys.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(lambda l=label: self.add_quick_marker(l))
            self.shortcuts.append(shortcut)

    def remove_shortcuts(self):
        """Remove all keyboard shortcuts"""
        for shortcut in self.shortcuts:
            shortcut.setEnabled(False)
            shortcut.deleteLater()
        self.shortcuts.clear()

    def add_quick_marker(self, label: str):
        """
        Add a quick marker

        Args:
            label: Marker label
        """
        try:
            marker = self.marker_manager.add_marker_now(label)
            self.status_label.setText(f"✓ Marker added: {label} @ {marker.timestamp:.2f}s")
            self.update_marker_list()
            self.marker_added.emit(label, "")
            logger.info(f"Quick marker added: {label}")

            # Flash the status
            QTimer.singleShot(2000, lambda: self.status_label.setText("Ready to add markers"))

        except Exception as e:
            logger.error(f"Failed to add marker: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add marker:\n{str(e)}")

    def add_custom_marker(self):
        """Add a custom marker with label and description"""
        label = self.label_input.text().strip()
        description = self.desc_input.text().strip()

        if not label:
            QMessageBox.warning(self, "Invalid Input", "Please enter a marker label.")
            return

        try:
            marker = self.marker_manager.add_marker_now(label, description)
            self.status_label.setText(f"✓ Custom marker added: {label}")
            self.update_marker_list()
            self.marker_added.emit(label, description)

            # Clear inputs
            self.label_input.clear()
            self.desc_input.clear()

            logger.info(f"Custom marker added: {label}")

            # Flash the status
            QTimer.singleShot(2000, lambda: self.status_label.setText("Ready to add markers"))

        except Exception as e:
            logger.error(f"Failed to add custom marker: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add marker:\n{str(e)}")

    def update_marker_list(self):
        """Update the marker list display"""
        try:
            # Get current markers
            markers = self.marker_manager.get_markers()

            # Update stats
            self.stats_label.setText(f"Markers: {len(markers)}")

            # Update list (only if changed)
            if len(markers) != self.marker_list.count():
                self.marker_list.clear()

                for marker in markers:
                    # Format: [HH:MM:SS] Label - Description
                    time_str = marker.local_time.strftime("%H:%M:%S")
                    text = f"[{time_str}] {marker.label}"
                    if marker.description:
                        text += f" - {marker.description}"

                    item = QListWidgetItem(text)
                    self.marker_list.addItem(item)

                # Scroll to bottom
                self.marker_list.scrollToBottom()

        except Exception as e:
            logger.error(f"Error updating marker list: {e}")

    def clear_markers(self):
        """Clear all markers"""
        reply = QMessageBox.question(
            self,
            "Clear Markers",
            "Clear all recorded markers?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.marker_manager.clear_markers()
            self.marker_list.clear()
            self.stats_label.setText("Markers: 0")
            self.status_label.setText("All markers cleared")
            logger.info("All markers cleared")

    def export_csv(self):
        """Export markers to CSV"""
        if self.marker_manager.get_marker_count() == 0:
            QMessageBox.information(self, "No Markers", "No markers to export.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Markers to CSV",
            f"markers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )

        if filename:
            try:
                self.marker_manager.export_to_csv(filename)
                self.status_label.setText(f"✓ Exported to {filename}")
                QMessageBox.information(self, "Export Successful", f"Markers exported to:\n{filename}")
            except Exception as e:
                logger.error(f"Failed to export CSV: {e}")
                QMessageBox.critical(self, "Export Failed", f"Failed to export:\n{str(e)}")

    def export_json(self):
        """Export markers to JSON"""
        if self.marker_manager.get_marker_count() == 0:
            QMessageBox.information(self, "No Markers", "No markers to export.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Markers to JSON",
            f"markers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )

        if filename:
            try:
                self.marker_manager.export_to_json(filename)
                self.status_label.setText(f"✓ Exported to {filename}")
                QMessageBox.information(self, "Export Successful", f"Markers exported to:\n{filename}")
            except Exception as e:
                logger.error(f"Failed to export JSON: {e}")
                QMessageBox.critical(self, "Export Failed", f"Failed to export:\n{str(e)}")

    def start_recording(self):
        """Start marker recording (start LSL stream)"""
        try:
            self.marker_manager.start_streaming()
            self.status_label.setText("✓ Marker stream started (LSL)")
            logger.info("Marker stream started")
        except Exception as e:
            logger.error(f"Failed to start marker stream: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start marker stream:\n{str(e)}")

    def stop_recording(self):
        """Stop marker recording"""
        self.marker_manager.stop_streaming()
        self.status_label.setText("Marker stream stopped")
        logger.info("Marker stream stopped")
