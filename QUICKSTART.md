# MuseGUI Quick Start Guide

Get up and running with MuseGUI in 5 minutes!

## 🚀 Installation (5 steps)

### 1. Install Python 3.7+
```bash
python --version  # Should be 3.7 or higher
```

### 2. Clone Repository
```bash
git clone https://github.com/yourusername/muse-lsl.git
cd muse-lsl
```

### 3. Install muse-lsl with GUI
```bash
# Install with GUI support
pip install -e ".[GUI]"
```

### 4. Launch MuseGUI
```bash
python -m musegui.main
```

### 5. Connect Your Muse
1. Power on your Muse headset
2. In MuseGUI, go to "Device" tab
3. Click "Search for Devices"
4. Select your Muse and click "Connect"

## ✅ First Recording

### Start Streaming
1. Go to "Streaming" tab
2. Select streams: ✓ EEG, ✓ PPG, ✓ ACC, ✓ GYRO
3. Click "▶ Start LSL Streaming"
4. Watch real-time data in "Visualization" tab!

### Record with Lab Recorder
1. **Install Lab Recorder** (one-time):
   - Download: https://github.com/labstreaminglayer/App-LabRecorder/releases
   - Install for your platform

2. **Start Recording**:
   - Launch Lab Recorder
   - Select Muse streams
   - Choose save location
   - Click "Start" in Lab Recorder

3. **Stop Recording**:
   - Click "Stop" in Lab Recorder
   - XDF file saved automatically

## 📊 Analyze in MATLAB

### Setup (one-time)
```bash
# Install XDF MATLAB library
git clone https://github.com/xdf-modules/xdf-Matlab.git
```

```matlab
% Add to MATLAB path
addpath('/path/to/muse-lsl/matlab_toolbox');
addpath('/path/to/xdf-Matlab');
savepath;
```

### Real-Time Analysis
```matlab
% Create receiver
mu = MuseUdp();

% Get EEG data
[eeg_data, timestamp, success] = mu.get_eeg_sample();
disp(eeg_data);  % [TP9, AF7, AF8, TP10, AUX]

mu.close();
```

### Load Recording
```matlab
% Load XDF file
[eeg, ppg, acc, gyro, markers] = load_muse_xdf('recording.xdf');

% Plot AF7 channel
plot(eeg.timestamps, eeg.data(:, 2));
xlabel('Time (s)');
ylabel('EEG (µV)');
title('AF7 Channel');
```

## 🎯 Example Workflow

### Neurofeedback Experiment
```matlab
% 1. Start MuseGUI with UDP streaming
% 2. In MATLAB:

mu = MuseUdp();

% Design alpha band filter (8-13 Hz)
fs = 256;
alpha_filt = designfilt('bandpassfir', ...
    'FilterOrder', 128, ...
    'CutoffFrequency1', 8, ...
    'CutoffFrequency2', 13, ...
    'SampleRate', fs);

% Real-time loop
for trial = 1:100
    % Collect 2 seconds
    chunk = mu.get_eeg_chunk(fs * 2);

    % Extract frontal channels (AF7, AF8)
    af7 = chunk(:, 3);
    af8 = chunk(:, 4);

    % Filter and compute alpha power
    af7_alpha = filtfilt(alpha_filt, af7);
    alpha_power = mean(af7_alpha.^2);

    % Provide feedback
    fprintf('Trial %d: Alpha power = %.2f µV²\n', trial, alpha_power);

    if alpha_power > threshold
        % Reward!
        fprintf('  ✓ Good alpha!\n');
    end

    pause(0.5);
end

mu.close();
```

## 🧪 Test Your Setup

### Run System Tests
1. Go to "Testing" tab in MuseGUI
2. Click "🧪 Run All Tests"
3. All tests should pass ✓

### Common Issues

**Device not found?**
```bash
# Linux: Check Bluetooth permissions
sudo usermod -a -G bluetooth $USER
# Logout and login again
```

**Connection fails?**
- Restart Muse headset
- Move closer to computer
- Try different backend (Device tab → Backend: bleak/gatt/auto)

**No LSL streams?**
- Ensure device is connected first
- Check firewall allows LSL
- Restart MuseGUI

**UDP not working in MATLAB?**
```matlab
% Test UDP connection
mu = MuseUdp();
mu.is_connected()  % Should return 1 (true)

% Increase buffer if needed
mu.set_udp_buffer_size(4096);
```

## 📚 Next Steps

- **Full Documentation**: See `MUSEGUI_README.md`
- **MATLAB Examples**: See `matlab_toolbox/examples/`
- **API Reference**: See `matlab_toolbox/README.md`
- **Troubleshooting**: See "Testing" tab in MuseGUI

## 💡 Pro Tips

1. **Always test before experiments**
   - Run system tests
   - Do a short test recording
   - Verify data quality

2. **Use Lab Recorder for research**
   - XDF format is standard
   - Includes all metadata
   - Supports multiple streams

3. **MATLAB for analysis**
   - Real-time: UDP streaming
   - Offline: XDF import
   - Use Signal Processing Toolbox

4. **Check signal quality**
   - Visualization tab shows real-time data
   - Look for clean, artifact-free signals
   - Adjust headset if noisy

5. **Save settings**
   - Settings tab → "💾 Save Settings"
   - Auto-loads on next launch

## 🎉 You're Ready!

You now have:
- ✅ MuseGUI running
- ✅ Muse connected
- ✅ LSL streaming
- ✅ MATLAB integration
- ✅ Recording capability

**Happy brain hacking!** 🧠✨

---

**Need Help?**
- GitHub Issues: https://github.com/yourusername/muse-lsl/issues
- Testing Tab: Built-in diagnostics
- README: `MUSEGUI_README.md`
