# MuseGUI New Features Guide

Three powerful new features have been added to MuseGUI to enhance your EEG recording and analysis workflow!

---

## 🧠 Feature 1: Real-Time Frequency Band Power Display

### Overview
Monitor EEG frequency bands in real-time with beautiful visual progress bars. No MATLAB needed!

### Location
**Tab**: 🧠 Band Power

### Frequency Bands Monitored

| Band | Frequency Range | Color | Associated With |
|------|----------------|-------|-----------------|
| **Delta** | 0.5-4 Hz | Salmon | Deep sleep, unconscious |
| **Theta** | 4-8 Hz | Coral | Meditation, creativity, drowsiness |
| **Alpha** | 8-13 Hz | Mint Green | Relaxation, closed eyes |
| **Beta** | 13-30 Hz | Aqua Teal | Alert, focused, active thinking |
| **Gamma** | 30-50 Hz | Rose | High-level cognition, perception |

### Features

#### 1. Channel Selection
Choose which EEG electrode to monitor:
- **TP9**: Left temporal (behind left ear)
- **AF7**: Left frontal (left forehead)
- **AF8**: Right frontal (right forehead)
- **TP10**: Right temporal (behind right ear)
- **Right AUX**: Reference electrode
- **Average**: Average across all channels

**Tip**: AF7 and AF8 (frontal) are good for general meditation/focus monitoring.

#### 2. Baseline Calibration
1. Record 30-60 seconds of baseline (relaxed, eyes open)
2. Click **"📍 Set Baseline"**
3. Enable **"Normalize to Baseline"** checkbox
4. Powers now show as % relative to your personal baseline

**Use Case**: Track if your alpha power increases during meditation compared to baseline.

#### 3. Band Power Bars
- **Real-time visualization** of power in each band
- **Values in µV²** shown next to each bar
- **Auto-scaling** or fixed scale options
- **Updates every 500ms**

#### 4. Band Ratios
Automatically calculated ratios useful for neurofeedback:

- **Theta/Alpha**: Relaxation indicator
  - Higher = More relaxed/drowsy
  - Lower = More alert

- **Beta/Alpha**: Alertness indicator
  - Higher = More focused/alert
  - Lower = More relaxed

- **Alpha/Delta**: Arousal level
  - Higher = More awake/aroused
  - Lower = Sleepier

### Example Workflow: Meditation Monitoring

```
1. Start Muse → Connect Device
2. Go to Band Power tab
3. Select "AF7" or "Average" channel
4. Start LSL Streaming
5. Record 1 minute of baseline (relaxed, eyes open)
6. Click "Set Baseline"
7. Enable "Normalize to Baseline"
8. Begin meditation
9. Watch Alpha power (should increase 20-50% during meditation)
10. Monitor Theta/Alpha ratio (should increase when deeply relaxed)
```

### Tips
- **Alpha power increases** with eyes closed or during relaxation
- **Beta power increases** during focused mental tasks
- **Theta power** often accompanies creative states
- **High Beta + Low Alpha** = Mental stress
- **High Alpha + Low Beta** = Relaxation

---

## 📍 Feature 2: Event Markers & Session Notes

### Overview
Add timestamped markers during recording for experiments, noting events, or tracking states.

### Location
**Tab**: 📍 Markers

### Quick Marker Buttons

Pre-configured buttons for common markers:
- **➕ Marker** - Generic marker
- **🎯 Stimulus** - Mark stimulus presentation
- **✓ Response** - Mark participant response
- **⚡ Event** - Mark any event

**Numbered Markers**: Buttons 1-5 for quick sequential marking

### Custom Markers

Add custom markers with:
1. **Label**: Short identifier (e.g., "Eyes_Closed", "Task_Start")
2. **Description**: Optional longer description
3. Click **"➕ Add Custom Marker"**

### Keyboard Shortcuts

**Enable with**: Click **"⌨️ Enable Keyboard Shortcuts"** button

| Key | Marker |
|-----|--------|
| **Space** | Generic Marker |
| **1-9** | Marker_1 through Marker_9 |
| **S** | Stimulus |
| **R** | Response |
| **E** | Event |
| **T** | Timestamp |

**Pro Tip**: Keep shortcuts enabled during experiments for hands-free marking!

### LSL Integration

All markers are automatically sent to the **LSL Markers stream**, which means:
- ✅ Lab Recorder will record them in your XDF file
- ✅ Perfect timestamp synchronization with EEG data
- ✅ Can be loaded in MATLAB with the XDF file

### Export Markers

Export your markers separately:
- **💾 Export CSV** - Spreadsheet format
- **💾 Export JSON** - Structured data format

CSV format:
```csv
Timestamp,Label,Description,Local Time
1234.567,Stimulus,First stimulus,2025-11-22T14:30:45
1245.678,Response,Button press,2025-11-22T14:30:56
```

### Example Workflow: Experiment with Stimuli

```
1. Connect Muse and start streaming
2. Go to Markers tab
3. Enable keyboard shortcuts
4. Present stimulus → Press 'S' (Stimulus marker)
5. Participant responds → Press 'R' (Response marker)
6. Repeat for all trials
7. Export markers to CSV for analysis
8. In XDF file, markers are time-synced with EEG
```

### MATLAB Analysis with Markers

```matlab
% Load recording
[eeg, ppg, acc, gyro, markers] = load_muse_xdf('experiment.xdf');

% Find stimulus markers
stimulus_idx = find(contains(markers.labels, 'Stimulus'));
stimulus_times = markers.timestamps(stimulus_idx);

% Extract EEG epochs around each stimulus
for i = 1:length(stimulus_times)
    % Get 2 seconds after stimulus
    epoch_start = stimulus_times(i);
    epoch_end = epoch_start + 2.0;

    % Find EEG samples in this window
    idx = eeg.timestamps >= epoch_start & eeg.timestamps <= epoch_end;
    eeg_epoch = eeg.data(idx, :);

    % Analyze this epoch...
    % (e.g., compute ERP, power changes, etc.)
end
```

### Tips
- **Label consistently** - Use same labels across sessions
- **Mark everything** - Stimulus start/end, responses, breaks, notes
- **Use shortcuts** during time-critical experiments
- **Export markers** even if using XDF (backup!)
- **Test keyboard shortcuts** before real experiments

---

## ⚠️ Feature 3: Automatic Artifact Detection

### Overview
Real-time detection of common EEG artifacts with visual warnings. Improve data quality!

### Location
Runs automatically in background. Warnings appear in **🧪 Testing** tab diagnostic log.

### Detected Artifacts

#### 1. **Eye Blinks** 👁️
- **Detection**: Large amplitude spikes (>150 µV) in frontal channels (AF7/AF8)
- **Cause**: Eye movement or blinking
- **Warning**: "Eye blink detected on AF7 (234.5 µV)"
- **Fix**: Ask participant to minimize blinking or remove affected epochs in analysis

#### 2. **Jaw Clenching** 💪
- **Detection**: High beta/gamma ratio (>2.0) in temporal channels (TP9/TP10)
- **Cause**: Jaw muscle tension
- **Warning**: "Jaw clenching on TP9 (β/α ratio: 3.2)"
- **Fix**: Relax jaw, check headband isn't too tight

#### 3. **Movement Artifacts** 🏃
- **Detection**: Large accelerometer values (>1.5 g)
- **Cause**: Head movement
- **Warning**: "Movement detected (acceleration: 2.3 g)"
- **Fix**: Stay still, ensure comfortable position

#### 4. **Electrode Disconnection** 🔌
- **Detection**: Near-zero variance (<0.1 µV²)
- **Cause**: Poor electrode contact
- **Warning**: "Possible disconnection on TP10 (variance: 0.03)"
- **Fix**: Adjust headband, moisten electrodes

#### 5. **High-Frequency Noise** 📡
- **Detection**: Excessive standard deviation (>100 µV)
- **Cause**: Environmental interference, poor contact
- **Warning**: "Noisy signal on AF8 (σ: 145 µV)"
- **Fix**: Check connections, remove electronic interference sources

#### 6. **Signal Saturation** 📊
- **Detection**: Values near ADC limits (>1800 µV)
- **Cause**: Extreme artifacts, electrode issues
- **Warning**: "Saturation on TP9 (1950 µV)"
- **Fix**: Severe issue, check electrode placement

### Signal Quality Score

**Location**: Calculated every 2 seconds, logged when <70/100

- **100-90**: Excellent data quality ✅
- **89-70**: Good data quality ✓
- **69-50**: Fair data, some artifacts ⚠️
- **<50**: Poor data quality, investigate! ❌

**Score calculation**: Based on artifact frequency and severity over last 30 detections.

### Artifact Warnings in Diagnostics Log

Example log output:
```
[14:30:45] LSL streaming started
[14:30:47] ⚠ Artifact: Eye blink detected on AF7 (187.3 µV)
[14:30:52] ⚠ Artifact: Movement detected (acceleration: 1.8 g)
[14:31:15] ⚠ Signal quality: 65/100
[14:31:30] ⚠ Artifact: Jaw clenching on TP9 (β/α ratio: 2.4)
```

### Customizing Detection

Thresholds are configurable in the code (`artifact_detection.py`):

```python
self.thresholds = {
    'eye_blink_amplitude': 150,      # µV
    'jaw_clench_beta_ratio': 2.0,    # Ratio
    'movement_acc_threshold': 1.5,   # g
    'flatline_variance': 0.1,        # µV²
    'saturation_level': 1800,        # µV
    'noise_std': 100,                # µV
}
```

### Example Workflow: Quality-Controlled Recording

```
1. Connect Muse and start streaming
2. Go to Testing tab to monitor diagnostics
3. Adjust headband based on warnings:
   - Disconnection warnings → Reposition headband
   - Eye blink warnings → Relax, minimize blinking
   - Movement warnings → Stay still
   - Jaw clench → Relax facial muscles
4. Wait until warnings stop
5. Begin actual recording when signal quality >80
6. Monitor log during recording
7. Mark sections with artifacts for later removal
```

### Tips for Clean Data

**Before Recording**:
- ✓ Clean forehead/behind ears with alcohol wipe
- ✓ Moisten electrode sensors slightly
- ✓ Ensure snug but comfortable fit
- ✓ Minimize environmental electronic interference
- ✓ Find comfortable sitting position

**During Recording**:
- ✓ Relax jaw and facial muscles
- ✓ Minimize eye movements/blinking when possible
- ✓ Stay still (movement artifacts are worst!)
- ✓ Monitor diagnostics log
- ✓ Add markers when artifacts occur for later removal

**After Recording**:
- ✓ Review artifact log
- ✓ Note any periods with many artifacts
- ✓ Consider removing bad sections in MATLAB analysis
- ✓ Calculate artifact percentage for quality metrics

### MATLAB: Removing Artifact-Marked Sections

```matlab
% Load data
[eeg, ~, ~, ~, markers] = load_muse_xdf('recording.xdf');

% Identify clean sections (no artifact markers nearby)
clean_mask = true(size(eeg.timestamps));

for i = 1:length(markers.timestamps)
    if contains(markers.labels{i}, 'Artifact', 'IgnoreCase', true)
        % Mark ±2 seconds around artifact
        artifact_time = markers.timestamps(i);
        bad_idx = abs(eeg.timestamps - artifact_time) < 2.0;
        clean_mask(bad_idx) = false;
    end
end

% Extract only clean data
clean_eeg = eeg.data(clean_mask, :);
clean_times = eeg.timestamps(clean_mask);

fprintf('Kept %.1f%% of data after artifact removal\n', ...
        100 * sum(clean_mask) / length(clean_mask));
```

---

## 🎯 Putting It All Together

### Complete Research Workflow

Here's how to use all three features together:

#### Setup (5 minutes)
1. **Connect** Muse headset
2. **Testing** tab → Run system tests
3. **Device** tab → Search and connect
4. **Settings** tab → Configure filters, recording path

#### Baseline Recording (2 minutes)
1. **Markers** tab → Enable keyboard shortcuts
2. **Band Power** tab → Select channel (AF7 or Average)
3. **Streaming** tab → Start LSL + UDP
4. **Testing** tab → Monitor signal quality
5. Adjust headband until quality >80
6. Record 1-2 minutes of relaxed baseline
7. **Band Power** tab → Set Baseline

#### Experiment (varies)
1. **Markers** tab → Press Space to mark experiment start
2. Present stimulus → Press **S**
3. Wait for response → Press **R**
4. Repeat for all trials
5. **Visualization** → Monitor real-time EEG
6. **Band Power** → Watch cognitive state changes
7. **Testing** → Monitor artifacts
8. Add custom markers for important events

#### Analysis (MATLAB)
```matlab
% Load everything
[eeg, ppg, acc, gyro, markers] = load_muse_xdf('session.xdf');

% Check markers
fprintf('Recorded %d markers:\n', length(markers.labels));
unique_markers = unique(markers.labels);
for i = 1:length(unique_markers)
    count = sum(strcmp(markers.labels, unique_markers{i}));
    fprintf('  %s: %d times\n', unique_markers{i}, count);
end

% Extract stimulus-locked epochs
stimulus_times = markers.timestamps(strcmp(markers.labels, 'Stimulus'));
epochs = cell(length(stimulus_times), 1);

for i = 1:length(stimulus_times)
    t_start = stimulus_times(i);
    t_end = t_start + 2.0;  % 2 seconds post-stimulus

    idx = eeg.timestamps >= t_start & eeg.timestamps <= t_end;
    epochs{i} = eeg.data(idx, :);
end

% Compute band powers per epoch
for i = 1:length(epochs)
    % Apply bandpass filter (8-13 Hz for alpha)
    alpha_data = bandpass(epochs{i}(:, 2), [8 13], 256);  % AF7
    alpha_power(i) = mean(alpha_data .^ 2);
end

% Plot results
plot(alpha_power);
xlabel('Trial Number');
ylabel('Alpha Power (µV²)');
title('Alpha Power Across Trials');
```

---

## 📊 Feature Comparison

| Feature | Band Power | Markers | Artifacts |
|---------|------------|---------|-----------|
| **Purpose** | Monitor cognitive states | Track events/timing | Ensure data quality |
| **Real-time** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Requires MATLAB** | ❌ No | ❌ No | ❌ No |
| **LSL Integration** | Uses LSL data | Sends to LSL | Uses LSL data |
| **Lab Recorder** | N/A | ✅ Recorded | ⚠️ Logged only |
| **Exportable** | ❌ No | ✅ CSV/JSON | 📋 In diagnostics |
| **Customizable** | ✓ Channels | ✓ Labels | ✓ Thresholds |

---

## 🎓 Learning Resources

### Tutorial Videos (Coming Soon)
- Band Power: Neurofeedback basics
- Markers: Designing experiments
- Artifacts: Ensuring data quality

### Example Use Cases

**Meditation Monitoring**
- Use: Band Power (Alpha increase)
- Markers: Session start/end, distractions
- Artifacts: Minimize for clean measurement

**Cognitive Task Experiments**
- Use: Markers (trial timing)
- Band Power: Cognitive load (Beta)
- Artifacts: Quality control

**Neurofeedback Training**
- Use: Band Power (target band)
- Markers: Feedback events
- Artifacts: Real-time quality

### Additional Documentation
- **MUSEGUI_README.md** - Complete GUI guide
- **QUICKSTART.md** - 5-minute setup
- **MATLAB_README.md** - MATLAB analysis examples

---

## 🐛 Troubleshooting

### Band Power Issues

**Problem**: Band power bars not updating
- **Fix**: Ensure LSL streaming is active
- **Fix**: Wait for 256+ samples (2 seconds)

**Problem**: Weird values (all zeros or very high)
- **Fix**: Check EEG signal quality
- **Fix**: Try different channel

### Marker Issues

**Problem**: Keyboard shortcuts not working
- **Fix**: Click "Enable Keyboard Shortcuts"
- **Fix**: Ensure Markers tab has focus

**Problem**: Markers not in XDF file
- **Fix**: Start markers BEFORE Lab Recorder recording
- **Fix**: Check Lab Recorder selected marker stream

### Artifact Detection Issues

**Problem**: Too many artifact warnings
- **Fix**: Adjust headband fit
- **Fix**: Check electrode contact
- **Fix**: Minimize movement/blinking

**Problem**: No artifact detection
- **Fix**: Ensure LSL streaming active
- **Fix**: Check Testing tab for warnings

---

## 💡 Pro Tips

1. **Always set baseline** before neurofeedback sessions
2. **Enable keyboard shortcuts** before experiments start
3. **Monitor artifacts** before starting actual recording
4. **Use consistent marker labels** across sessions
5. **Export markers** as backup even when using XDF
6. **Check signal quality** >80 before important recordings
7. **Record baseline** at same time of day for consistency
8. **Label artifact periods** with markers for later removal
9. **Use averaged channels** for general band power monitoring
10. **Combine all three** features for professional-quality research!

---

## 📝 Quick Reference

### Keyboard Shortcuts (when enabled)
```
Space - Marker
1-9   - Marker_1 through Marker_9
S     - Stimulus
R     - Response
E     - Event
T     - Timestamp
```

### Frequency Bands
```
Delta: 0.5-4 Hz   (Deep sleep)
Theta: 4-8 Hz     (Meditation)
Alpha: 8-13 Hz    (Relaxation)
Beta:  13-30 Hz   (Focus)
Gamma: 30-50 Hz   (Cognition)
```

### Signal Quality Scores
```
100-90: Excellent ✅
89-70:  Good ✓
69-50:  Fair ⚠️
<50:    Poor ❌
```

---

**Enjoy your enhanced MuseGUI experience!** 🧠✨

For questions or feedback, see the GitHub repository or MUSEGUI_README.md.
