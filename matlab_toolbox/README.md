# MuseGUI MATLAB Toolbox

MATLAB toolbox for receiving real-time Muse EEG data via UDP and loading XDF recordings.

## Features

- **Real-time UDP streaming** from MuseGUI
- **XDF file import** for offline analysis
- **Multi-sensor support**: EEG, PPG, accelerometer, gyroscope
- **Easy-to-use API** with comprehensive examples
- **Compatible** with MATLAB R2020b and newer

## Installation

1. **Download the toolbox:**
   ```bash
   # Add this directory to your MATLAB path
   addpath('/path/to/muse-lsl/matlab_toolbox');
   savepath;
   ```

2. **Install XDF library** (for loading XDF files):
   ```bash
   # Clone the XDF MATLAB library
   git clone https://github.com/xdf-modules/xdf-Matlab.git
   ```

   Then add it to your MATLAB path:
   ```matlab
   addpath('/path/to/xdf-Matlab');
   savepath;
   ```

3. **Verify installation:**
   ```matlab
   mu = MuseUdp();
   methods(mu)
   mu.close();
   ```

## Requirements

- **MATLAB** R2020b or newer
- **Instrument Control Toolbox** (for UDP communication)
- **Signal Processing Toolbox** (optional, for analysis examples)
- **XDF MATLAB library** (for loading XDF files)

## Quick Start

### Real-Time UDP Streaming

```matlab
% Create UDP receiver
mu = MuseUdp('127.0.0.1', 5000);

% Get single EEG sample
[data, timestamp, success] = mu.get_eeg_sample();
% data: 1×5 array [TP9, AF7, AF8, TP10, Right AUX]

% Get multiple samples
eeg_chunk = mu.get_eeg_chunk(50);  % 50 samples
% Returns: 50×6 matrix [timestamp, ch1, ch2, ch3, ch4, ch5]

% Other sensor types
[ppg_data, ts, ok] = mu.get_ppg_sample();     % PPG
[acc_data, ts, ok] = mu.get_acc_sample();     % Accelerometer
[gyro_data, ts, ok] = mu.get_gyro_sample();   % Gyroscope

% Close connection
mu.close();
```

### Loading XDF Recordings

```matlab
% Load XDF file
[eeg, ppg, acc, gyro, markers] = load_muse_xdf('recording.xdf');

% Access EEG data
plot(eeg.timestamps, eeg.data(:, 2));  % Plot AF7 channel
xlabel('Time (s)');
ylabel('EEG (µV)');
title('AF7 Channel');

% Get sampling info
fprintf('Sample rate: %.1f Hz\n', eeg.srate);
fprintf('Duration: %.1f seconds\n', eeg.timestamps(end) - eeg.timestamps(1));
fprintf('Channels: %s\n', strjoin(eeg.channels, ', '));
```

## API Reference

### MuseUdp Class

#### Constructor
```matlab
mu = MuseUdp()                          % Default: localhost:5000
mu = MuseUdp(host)                      % Custom host
mu = MuseUdp(host, port)                % Custom host and port
mu = MuseUdp(host, port, buffer_size)   % Full custom
```

#### Methods

**Get single samples:**
- `[data, timestamp, success] = get_eeg_sample()` - Get EEG sample (1×5)
- `[data, timestamp, success] = get_ppg_sample()` - Get PPG sample (1×3)
- `[data, timestamp, success] = get_acc_sample()` - Get ACC sample (1×3)
- `[data, timestamp, success] = get_gyro_sample()` - Get GYRO sample (1×3)

**Get multiple samples:**
- `chunk = get_eeg_chunk(n)` - Get n EEG samples (n×6)
- `chunk = get_ppg_chunk(n)` - Get n PPG samples (n×4)
- `chunk = get_acc_chunk(n)` - Get n ACC samples (n×4)
- `chunk = get_gyro_chunk(n)` - Get n GYRO samples (n×4)

**Configuration:**
- `set_udp_buffer_size(size)` - Change buffer size (bytes)
- `status = is_connected()` - Check connection status
- `available = bytes_available()` - Get available bytes
- `close()` - Close UDP connection

### load_muse_xdf Function

```matlab
[eeg, ppg, acc, gyro, markers] = load_muse_xdf(filepath)
```

**Outputs:**
- `eeg` - Structure with EEG data
  - `.data` - n_samples × 5 matrix
  - `.timestamps` - n_samples × 1 vector
  - `.srate` - Sampling rate (Hz)
  - `.channels` - Cell array of channel names
- `ppg`, `acc`, `gyro` - Same structure as EEG
- `markers` - Structure with event markers
  - `.timestamps` - n_markers × 1 vector
  - `.labels` - Cell array of marker labels

## Examples

### Example 1: Real-Time Visualization

See `examples/realtime_example.m` for a complete real-time EEG visualization script with:
- Real-time plotting of all 5 EEG channels
- Scrolling time window
- Circular data buffer

```matlab
run('examples/realtime_example.m');
```

### Example 2: XDF Analysis

See `examples/xdf_analysis_example.m` for comprehensive offline analysis including:
- Loading and plotting raw EEG
- Bandpass filtering (1-40 Hz)
- Notch filtering (60 Hz)
- Power spectral density analysis
- Frequency band power computation
- Statistical summaries

```matlab
run('examples/xdf_analysis_example.m');
```

### Example 3: Custom Real-Time Processing

```matlab
% Setup
mu = MuseUdp();
fs = 256;  % EEG sample rate

% Parameters for alpha band (8-13 Hz)
alpha_band = [8, 13];

% Design bandpass filter
bp_filt = designfilt('bandpassfir', ...
    'FilterOrder', 128, ...
    'CutoffFrequency1', alpha_band(1), ...
    'CutoffFrequency2', alpha_band(2), ...
    'SampleRate', fs);

% Collect 5 seconds of data
fprintf('Collecting data...\n');
data = mu.get_eeg_chunk(fs * 5);

% Extract AF7 and AF8 (frontal channels)
af7 = data(:, 3);  % Column 3 (after timestamp)
af8 = data(:, 4);  % Column 4

% Filter
af7_alpha = filtfilt(bp_filt, af7);
af8_alpha = filtfilt(bp_filt, af8);

% Compute alpha power
alpha_power_af7 = mean(af7_alpha.^2);
alpha_power_af8 = mean(af8_alpha.^2);

fprintf('Alpha power AF7: %.2f µV²\n', alpha_power_af7);
fprintf('Alpha power AF8: %.2f µV²\n', alpha_power_af8);

% Cleanup
mu.close();
```

## UDP Packet Format

### EEG Packets (24 bytes)
```
[timestamp: 4 bytes (float32)] + [5 channels × 4 bytes (float32)] = 24 bytes
Channels: TP9, AF7, AF8, TP10, Right AUX
```

### PPG/ACC/GYRO Packets (16 bytes)
```
[timestamp: 4 bytes (float32)] + [3 channels × 4 bytes (float32)] = 16 bytes
```

## Troubleshooting

### "No data received"
1. Ensure MuseGUI is running and UDP streaming is started
2. Check IP address and port match (default: 127.0.0.1:5000)
3. Verify firewall allows UDP traffic
4. Increase UDP buffer size: `mu.set_udp_buffer_size(4096);`

### "XDF library not found"
1. Install XDF MATLAB library from: https://github.com/xdf-modules/xdf-Matlab
2. Add to MATLAB path: `addpath('/path/to/xdf-Matlab');`

### "Packet size mismatch"
- Ensure MuseGUI and MATLAB toolbox versions match
- Check for data corruption (restart MuseGUI)

### Performance issues
- Reduce visualization update rate
- Increase UDP buffer size
- Use chunk retrieval instead of individual samples

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/yourusername/muse-lsl/issues
- Documentation: See main MuseGUI README

## License

Same license as muse-lsl (MIT)

## Authors

MuseGUI Development Team

---

**Happy EEG analysis!** 🧠✨
