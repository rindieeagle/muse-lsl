# MuseGUI - Retro Rainbow EEG Interface for Muse Headsets

<div align="center">

**A modern, user-friendly GUI application for Muse EEG streaming, recording, and analysis**

🧠 **LSL Streaming** • 📡 **UDP/MATLAB Integration** • 📊 **Real-Time Visualization** • 🧪 **Built-in Testing**

</div>

---

## ✨ Features

### 🎨 Beautiful Retro Rainbow Interface
- **Glassmorphism design** with custom retro rainbow color palette
- **Touch-friendly** spacing and responsive layout
- **Intuitive** tab-based navigation
- **Real-time** status indicators

### 📡 Dual Streaming Protocols
- **LSL (Lab Streaming Layer)** - Industry standard for neuroscience research
- **UDP Streaming** - Direct MATLAB integration for real-time analysis
- **Simultaneous** streaming on both protocols
- **Lab Recorder** integration for XDF recordings

### 🔌 Device Management
- **Auto-discovery** of Muse devices (Muse 2, Muse S)
- **Multiple Bluetooth backends** (bleak, gatt, bgapi)
- **Connection monitoring** with auto-reconnect
- **Sensor control** (EEG, PPG, accelerometer, gyroscope)

### 📊 Real-Time Visualization
- **Multi-channel** EEG plotting (5 channels)
- **PPG, accelerometer, and gyroscope** views
- **Customizable** time scales and auto-scaling
- **Smooth** 60 FPS rendering with PyQtGraph
- **Signal quality** indicators

### ⚙️ Advanced Configuration
- **Signal filtering**: Highpass, lowpass, notch (50/60 Hz)
- **Recording settings**: Auto-save, custom output paths
- **Lab Recorder** integration with custom paths
- **Settings persistence** across sessions

### 🧪 Testing & Diagnostics
- **Comprehensive system tests** (Python, dependencies, Bluetooth, LSL, UDP)
- **Real-time diagnostics log** with export
- **Troubleshooting guide** built-in
- **Connection validation** tools

### 🔬 MATLAB Toolbox
- **MuseUdp class** for real-time data reception
- **XDF import/export** utilities
- **Example scripts** for visualization and analysis
- **Complete API documentation**

---

## 🚀 Installation

### Prerequisites

- **Python 3.7+** (3.8 or newer recommended)
- **Muse headset** (Muse 2 or Muse S)
- **Bluetooth** adapter
- **Operating System**: Windows 10+, macOS 10.14+, or Linux

### Step 1: Install muse-lsl

```bash
# Clone the repository
git clone https://github.com/yourusername/muse-lsl.git
cd muse-lsl

# Install base muse-lsl
pip install -e .
```

### Step 2: Install GUI dependencies

```bash
# Install GUI requirements
pip install -r requirements-gui.txt
```

### Step 3: Install Lab Recorder (Optional)

Download Lab Recorder from:
- https://github.com/labstreaminglayer/App-LabRecorder/releases

Install according to your platform:
- **Windows**: Run installer
- **macOS**: Copy to Applications
- **Linux**: Extract and add to PATH

### Step 4: MATLAB Toolbox (Optional)

For MATLAB integration:

1. **Install XDF MATLAB library**:
   ```bash
   git clone https://github.com/xdf-modules/xdf-Matlab.git
   ```

2. **Add toolbox to MATLAB path**:
   ```matlab
   addpath('/path/to/muse-lsl/matlab_toolbox');
   addpath('/path/to/xdf-Matlab');
   savepath;
   ```

---

## 🎯 Quick Start

### Launch MuseGUI

```bash
# From the muse-lsl directory
python -m musegui.main
```

Or create a launcher script:

**launch_musegui.sh** (Linux/macOS):
```bash
#!/bin/bash
cd /path/to/muse-lsl
python -m musegui.main
```

**launch_musegui.bat** (Windows):
```batch
@echo off
cd C:\path\to\muse-lsl
python -m musegui.main
```

### Basic Workflow

1. **Connect Device**
   - Go to "Device" tab
   - Click "Search for Devices"
   - Select your Muse and click "Connect"

2. **Start Streaming**
   - Go to "Streaming" tab
   - Enable desired streams (EEG, PPG, ACC, GYRO)
   - Click "Start LSL Streaming"
   - Optionally start "UDP Streaming" for MATLAB

3. **Visualize Data**
   - Go to "Visualization" tab
   - Watch real-time EEG plots
   - Switch between EEG, PPG, ACC, GYRO views
   - Adjust time scale and auto-scaling

4. **Record Data**
   - Launch Lab Recorder (automatically or manually)
   - Select streams to record
   - Start recording in Lab Recorder
   - Data saved as XDF files

5. **Analyze in MATLAB**
   ```matlab
   % Real-time analysis
   mu = MuseUdp();
   [data, ts, ok] = mu.get_eeg_sample();

   % Or load XDF recording
   [eeg, ppg, acc, gyro, markers] = load_muse_xdf('recording.xdf');
   ```

---

## 📖 User Guide

### Device Tab

**Bluetooth Backend Selection**
- `auto`: Automatically select best backend (recommended)
- `bleak`: Cross-platform, modern (default)
- `gatt`: Linux-specific using hcitool
- `bgapi`: For BLED112 USB dongles

**Device Discovery**
- Ensure Muse is powered on and nearby
- Unpair from other devices (Muse app, etc.)
- Click "Search for Devices"
- Wait ~10 seconds for scan
- Double-click device or select and click "Connect"

**Connection Tips**
- Move Muse closer if not found
- Restart Muse if connection fails
- Try different backends on connection issues
- Check Bluetooth permissions on Linux

### Streaming Tab

**LSL Streaming**
- Streams to LSL network for Lab Recorder and other LSL apps
- Select which sensors to stream (EEG, PPG, ACC, GYRO)
- All streams synchronized with timestamps
- Compatible with all LSL tools

**UDP Streaming**
- Direct streaming to MATLAB or other UDP receivers
- Configure target IP and port (default: 127.0.0.1:5000)
- Packet format: [timestamp (4 bytes)] + [channel data (N×4 bytes)]
- See MATLAB toolbox for receiving code

**Statistics**
- Real-time packet counts per stream
- Error tracking
- Samples received counter
- UDP bytes sent

### Visualization Tab

**Display Controls**
- **View**: Select EEG, PPG, Accelerometer, Gyroscope, or All
- **Time Scale**: Adjust window size (1-10 seconds)
- **Auto-scale**: Automatically adjust Y-axis range
- **Clear**: Reset data buffers

**EEG Channels**
- TP9: Left temporal
- AF7: Left frontal
- AF8: Right frontal
- TP10: Right temporal
- Right AUX: Reference/auxiliary

**Performance**
- Smooth 60 FPS rendering
- Hardware-accelerated with OpenGL (PyQtGraph)
- Efficient ring buffers
- No data loss during visualization

### Settings Tab

**Signal Filters**
- **Highpass**: Remove slow drifts (recommended: 1 Hz)
- **Lowpass**: Remove high-frequency noise (recommended: 40 Hz)
- **Notch**: Remove power line noise (50 Hz or 60 Hz)
- **Note**: Filters for visualization only, raw data always saved

**Recording Settings**
- **Output Directory**: Where recordings are saved
- **Auto-save**: Continuously save during recording
- **Save Interval**: How often to save (default: 5 seconds)
- **Include Markers**: Save event markers in recordings

**Lab Recorder Integration**
- **Path**: Custom path to Lab Recorder executable (auto-detected if empty)
- **Auto-launch**: Automatically open Lab Recorder when streaming starts
- **Test**: Verify Lab Recorder installation

**Display Settings**
- **Update Rate**: Visualization FPS (default: 30)
- **Theme**: Retro Rainbow (more themes coming soon!)

### Testing Tab

**System Tests**
- **Python Version**: Verify Python 3.7+
- **Dependencies**: Check all required packages
- **Bluetooth**: Test Bluetooth adapter
- **LSL**: Verify LSL functionality
- **UDP Socket**: Test UDP communication
- **Device Detection**: Scan for Muse devices

**Diagnostics Log**
- Real-time log of all events
- Exportable to text file
- Timestamped entries
- Error tracking

**Troubleshooting**
- Built-in solutions for common issues
- Step-by-step guides
- Platform-specific tips

---

## 🔧 Advanced Usage

### Custom Filter Configuration

```python
# In settings_panel.py, you can add custom filters
from scipy import signal

# Example: Custom bandpass filter
def apply_custom_filter(data, fs=256):
    sos = signal.butter(4, [0.5, 50], 'bandpass', fs=fs, output='sos')
    filtered = signal.sosfilt(sos, data)
    return filtered
```

### Programmatic Control

```python
from musegui.backend import LSLManager, UDPStreamer

# Create managers
lsl = LSLManager()
udp = UDPStreamer(host='192.168.1.100', port=5000)

# Start streaming
lsl.discover_streams()
lsl.connect_stream('eeg')
lsl.start_receiving()

udp.start()

# Register callback
def my_callback(timestamp, data):
    print(f"EEG @ {timestamp}: {data}")
    udp.send_eeg_sample(timestamp, data)

lsl.register_callback('eeg', my_callback)

# ... do work ...

# Cleanup
lsl.stop_receiving()
udp.stop()
```

### Custom Recording Workflow

```python
from musegui.backend import RecordingSession

# Create session
session = RecordingSession(
    output_dir='/path/to/recordings',
    session_name='experiment_001'
)

# Set metadata
session.set_participant_id('P001')
session.add_note('Baseline recording')

# Start recording
session.start()

# ... record data ...

# Stop and save
session.stop()
print(f"Recording saved: {session.get_output_path()}")
```

---

## 🐍 MATLAB Integration

### Real-Time Streaming

```matlab
% Create UDP receiver
mu = MuseUdp('127.0.0.1', 5000);

% Real-time loop
for i = 1:1000
    [eeg_data, timestamp, success] = mu.get_eeg_sample();

    if success
        % Process data
        fprintf('Sample %d: %.3f\n', i, mean(eeg_data));
    end

    pause(0.001);
end

mu.close();
```

### Loading XDF Recordings

```matlab
% Load recording
[eeg, ppg, acc, gyro, markers] = load_muse_xdf('recording.xdf');

% Basic analysis
fprintf('Duration: %.1f seconds\n', eeg.timestamps(end) - eeg.timestamps(1));
fprintf('Mean EEG: %.2f µV\n', mean(eeg.data(:)));

% Plot
figure;
plot(eeg.timestamps, eeg.data(:, 2));  % AF7 channel
xlabel('Time (s)');
ylabel('EEG (µV)');
title('AF7 Channel');
```

See `matlab_toolbox/README.md` and `matlab_toolbox/examples/` for more examples.

---

## 🎨 Design System

### Retro Rainbow Palette

| Color         | Hex       | Usage                    |
|---------------|-----------|--------------------------|
| Deep Teal     | `#025c7f` | Primary, backgrounds     |
| Ocean Blue    | `#027b96` | Accents, gradients       |
| Aqua Teal     | `#069aa4` | Interactive elements     |
| Mint Green    | `#87d1ac` | Success, borders         |
| Cream Yellow  | `#fef8be` | Headers, highlights      |
| Peach         | `#ffe1a5` | Warnings                 |
| Coral         | `#ffc991` | Information              |
| Orange        | `#ffb085` | Active states            |
| Salmon        | `#fb9481` | Errors, stop actions     |
| Rose          | `#f37986` | Emphasis                 |

### Typography

- **Headers**: Cooper Black / New Kansas (thick retro fonts)
- **Body**: Nunito (clean, readable)
- **Spacing**: 4px base unit (4, 8, 16, 24, 32, 48)

### Breakpoints

- **Mobile**: 0-767px
- **Tablet**: 768-1024px
- **Desktop**: 1025-1440px
- **Large Desktop**: 1441px+

---

## 🐛 Troubleshooting

### Device Not Found

**Symptoms**: No devices appear after search

**Solutions**:
1. Ensure Muse is powered on (LED blinking)
2. Move Muse closer to computer
3. Disconnect from Muse app or other devices
4. Try different Bluetooth backend (`auto` → `bleak` → `gatt`)
5. On Linux: Check Bluetooth permissions
   ```bash
   sudo usermod -a -G bluetooth $USER
   sudo systemctl restart bluetooth
   ```

### Connection Fails

**Symptoms**: "Connection failed" error

**Solutions**:
1. Restart Muse headset (power off/on)
2. Restart Bluetooth adapter
3. Update Bluetooth drivers
4. On Windows: Unpair device in Bluetooth settings first
5. Try `bleak` backend specifically

### No LSL Streams

**Symptoms**: LSL streams not appearing in Lab Recorder

**Solutions**:
1. Ensure device is connected first
2. Verify LSL streaming is started (green status)
3. Check firewall allows LSL traffic
4. Restart Lab Recorder
5. Try `resolve_streams()` in Python:
   ```python
   from pylsl import resolve_streams
   streams = resolve_streams(timeout=5.0)
   print(len(streams), "streams found")
   ```

### UDP Not Receiving in MATLAB

**Symptoms**: No data in MATLAB UDP receiver

**Solutions**:
1. Verify IP address and port match (default: 127.0.0.1:5000)
2. Check firewall allows UDP on port 5000
3. Increase MATLAB UDP buffer:
   ```matlab
   mu.set_udp_buffer_size(4096);
   ```
4. Test with Python first:
   ```python
   import socket
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.bind(('127.0.0.1', 5000))
   data, addr = sock.recvfrom(1024)
   print(len(data), "bytes received")
   ```

### Visualization Lag

**Symptoms**: Choppy or slow visualization

**Solutions**:
1. Reduce update rate in Settings
2. Decrease time window (1-3 seconds)
3. Disable auto-scale
4. Close other heavy applications
5. Update graphics drivers

### XDF File Won't Load

**Symptoms**: Error loading XDF in MATLAB

**Solutions**:
1. Verify XDF MATLAB library is installed
2. Check file integrity (not corrupted)
3. Ensure file is complete (recording stopped properly)
4. Try loading in Python first:
   ```python
   import pyxdf
   streams, header = pyxdf.load_xdf('recording.xdf')
   print(len(streams), "streams loaded")
   ```

---

## 🔬 Technical Details

### Architecture

```
MuseGUI
├── musegui/
│   ├── ui/                  # Qt6 GUI components
│   │   ├── main_window.py   # Main application window
│   │   ├── device_panel.py  # Device connection UI
│   │   ├── streaming_panel.py  # Streaming controls
│   │   ├── visualization.py    # Real-time plots
│   │   ├── settings_panel.py   # Configuration UI
│   │   └── testing_panel.py    # Diagnostics UI
│   ├── backend/            # Core functionality
│   │   ├── lsl_manager.py  # LSL stream handling
│   │   ├── udp_streamer.py # UDP protocol implementation
│   │   └── recorder.py     # Lab Recorder integration
│   ├── resources/          # UI resources
│   │   └── palette.py      # Color scheme
│   └── main.py             # Entry point
└── matlab_toolbox/         # MATLAB integration
    ├── MuseUdp.m           # UDP receiver class
    ├── load_muse_xdf.m     # XDF import
    └── examples/           # Usage examples
```

### Data Flow

```
Muse Headset (BLE)
    ↓
muselsl.stream (Python process)
    ↓
LSL Network ←→ MuseGUI ←→ UDP Socket
    ↓              ↓          ↓
Lab Recorder   Visualization  MATLAB
    ↓
XDF File ←→ MATLAB Analysis
```

### Packet Formats

**EEG (24 bytes)**:
```
[timestamp: float32 (4 bytes)]
[TP9: float32 (4 bytes)]
[AF7: float32 (4 bytes)]
[AF8: float32 (4 bytes)]
[TP10: float32 (4 bytes)]
[Right AUX: float32 (4 bytes)]
```

**PPG/ACC/GYRO (16 bytes)**:
```
[timestamp: float32 (4 bytes)]
[CH1: float32 (4 bytes)]
[CH2: float32 (4 bytes)]
[CH3: float32 (4 bytes)]
```

### Sampling Rates

- **EEG**: 256 Hz (5 channels)
- **PPG**: 64 Hz (3 channels, Muse 2/S only)
- **Accelerometer**: 52 Hz (3 axes)
- **Gyroscope**: 52 Hz (3 axes)

---

## 📝 FAQ

**Q: What Muse models are supported?**
A: Muse 2 and Muse S are fully supported. Original Muse (2014) has limited support (EEG only).

**Q: Can I use this on a Raspberry Pi?**
A: Yes! Works on Raspberry Pi 4 with Raspberry Pi OS. May need to install system dependencies:
```bash
sudo apt-get install python3-pyqt6 bluetooth bluez
```

**Q: Does this work with multiple Muses simultaneously?**
A: Current version supports one Muse at a time. Multi-device support is planned.

**Q: Can I export data to formats other than XDF?**
A: XDF is the primary format. You can convert to CSV, MAT, or other formats in MATLAB/Python after loading the XDF.

**Q: Is real-time neurofeedback possible?**
A: Yes! Use the UDP streaming to MATLAB or Python and implement your neurofeedback logic. See examples for band power calculation.

**Q: What's the latency?**
A: Typical end-to-end latency (Muse → MuseGUI → MATLAB) is ~50-100ms, suitable for most applications.

**Q: Can I use this for research/publications?**
A: Yes! MuseGUI is built on muse-lsl, which is widely used in research. Cite appropriately and validate for your specific use case.

---

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- [ ] Multi-device support
- [ ] Additional themes
- [ ] More filter presets
- [ ] Python API for custom plugins
- [ ] Cloud recording integration
- [ ] Mobile companion app

See `CONTRIBUTING.md` for guidelines.

---

## 📄 License

MIT License - see `LICENSE` file

---

## 🙏 Acknowledgments

- **muse-lsl** - Original LSL streaming implementation
- **Lab Streaming Layer** - Real-time data synchronization
- **PyQt6** - Modern GUI framework
- **PyQtGraph** - High-performance plotting
- **Interaxon Muse** - EEG hardware

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/muse-lsl/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/muse-lsl/discussions)
- **Email**: support@musegui.example.com

---

<div align="center">

**Made with 🧠 and ❤️ for neuroscience research**

</div>
