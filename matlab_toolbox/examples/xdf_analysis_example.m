% XDF_ANALYSIS_EXAMPLE Example of loading and analyzing Muse XDF recordings
%
% This example demonstrates how to load Muse data from an XDF file
% recorded with Lab Recorder or MuseGUI, and perform basic analysis.
%
% Requirements:
%   - XDF MATLAB library (https://github.com/xdf-modules/xdf-Matlab)
%   - Signal Processing Toolbox (for filtering and spectral analysis)
%
% Author: MuseGUI Development Team

%% Load XDF file
clear; close all; clc;

fprintf('=== Muse XDF Analysis Example ===\n\n');

% Select XDF file
[filename, pathname] = uigetfile('*.xdf', 'Select Muse XDF recording');

if filename == 0
    fprintf('No file selected. Exiting.\n');
    return;
end

filepath = fullfile(pathname, filename);

% Load data
fprintf('Loading XDF file...\n');
[eeg, ppg, acc, gyro, markers] = load_muse_xdf(filepath);

fprintf('\nData loaded successfully!\n\n');

%% EEG Analysis

if isempty(eeg.data)
    fprintf('No EEG data found in file.\n');
    return;
end

fprintf('=== EEG Analysis ===\n');
fprintf('Duration: %.2f seconds\n', eeg.timestamps(end) - eeg.timestamps(1));
fprintf('Samples: %d\n', length(eeg.timestamps));
fprintf('Sample rate: %.2f Hz\n', eeg.srate);
fprintf('Channels: %s\n\n', strjoin(eeg.channels, ', '));

%% Plot raw EEG

figure('Name', 'Raw EEG Data', 'NumberTitle', 'off', 'Position', [50, 50, 1400, 800]);

for ch = 1:5
    subplot(5, 1, ch);
    plot(eeg.timestamps, eeg.data(:, ch), 'LineWidth', 1);
    ylabel(sprintf('%s (µV)', eeg.channels{ch}), 'FontWeight', 'bold');
    grid on;
    xlim([eeg.timestamps(1), eeg.timestamps(end)]);

    if ch == 1
        title('Raw EEG Signals', 'FontSize', 14, 'FontWeight', 'bold');
    end

    if ch == 5
        xlabel('Time (seconds)', 'FontWeight', 'bold');
    else
        set(gca, 'XTickLabel', []);
    end
end

%% Filter EEG (1-40 Hz bandpass)

fprintf('Applying bandpass filter (1-40 Hz)...\n');

% Design filter
fs = eeg.srate;
fir_order = 3 * fix(fs / 0.5);
fir_order = fir_order + mod(fir_order + 1, 2);  % Ensure odd order

% Bandpass filter
bp_filt = designfilt('bandpassfir', 'FilterOrder', fir_order, ...
    'CutoffFrequency1', 1, 'CutoffFrequency2', 40, ...
    'SampleRate', fs);

% Apply filter to each channel
eeg_filtered = zeros(size(eeg.data));
for ch = 1:5
    eeg_filtered(:, ch) = filtfilt(bp_filt, eeg.data(:, ch));
end

% Notch filter for 60 Hz (power line noise)
fprintf('Applying notch filter (60 Hz)...\n');
notch_filt = designfilt('bandstopiir', 'FilterOrder', 2, ...
    'HalfPowerFrequency1', 58, 'HalfPowerFrequency2', 62, ...
    'SampleRate', fs);

for ch = 1:5
    eeg_filtered(:, ch) = filtfilt(notch_filt, eeg_filtered(:, ch));
end

%% Plot filtered EEG

figure('Name', 'Filtered EEG Data', 'NumberTitle', 'off', 'Position', [100, 100, 1400, 800]);

for ch = 1:5
    subplot(5, 1, ch);
    plot(eeg.timestamps, eeg_filtered(:, ch), 'LineWidth', 1);
    ylabel(sprintf('%s (µV)', eeg.channels{ch}), 'FontWeight', 'bold');
    grid on;
    xlim([eeg.timestamps(1), eeg.timestamps(end)]);

    if ch == 1
        title('Filtered EEG Signals (1-40 Hz + Notch 60 Hz)', 'FontSize', 14, 'FontWeight', 'bold');
    end

    if ch == 5
        xlabel('Time (seconds)', 'FontWeight', 'bold');
    else
        set(gca, 'XTickLabel', []);
    end
end

%% Power Spectral Density

fprintf('Computing power spectral density...\n');

figure('Name', 'EEG Power Spectral Density', 'NumberTitle', 'off', 'Position', [150, 150, 1200, 600]);

% Frequency bands
bands = struct(...
    'delta', [0.5, 4], ...
    'theta', [4, 8], ...
    'alpha', [8, 13], ...
    'beta', [13, 30], ...
    'gamma', [30, 50]);

band_names = fieldnames(bands);
band_colors = [0.8, 0.2, 0.2; 0.2, 0.6, 0.8; 0.2, 0.8, 0.2; 0.8, 0.6, 0.2; 0.6, 0.2, 0.8];

for ch = 1:5
    subplot(2, 3, ch);

    % Compute PSD using Welch's method
    [pxx, f] = pwelch(eeg_filtered(:, ch), hanning(fs*2), fs, fs*2, fs);

    % Plot PSD
    plot(f, 10*log10(pxx), 'k', 'LineWidth', 1.5);
    hold on;

    % Highlight frequency bands
    y_lim = ylim;
    for b = 1:length(band_names)
        band_range = bands.(band_names{b});
        patch([band_range(1), band_range(2), band_range(2), band_range(1)], ...
              [y_lim(1), y_lim(1), y_lim(2), y_lim(2)], ...
              band_colors(b, :), 'FaceAlpha', 0.2, 'EdgeColor', 'none');
    end

    xlim([0, 50]);
    xlabel('Frequency (Hz)', 'FontWeight', 'bold');
    ylabel('Power/Frequency (dB/Hz)', 'FontWeight', 'bold');
    title(eeg.channels{ch}, 'FontWeight', 'bold');
    grid on;
    hold off;
end

% Add legend
subplot(2, 3, 6);
axis off;
hold on;
for b = 1:length(band_names)
    patch([0, 1, 1, 0], [b, b, b+0.8, b+0.8], ...
          band_colors(b, :), 'FaceAlpha', 0.5, 'EdgeColor', 'k');
    text(1.2, b+0.4, sprintf('%s (%.1f-%.1f Hz)', ...
         upper(band_names{b}), bands.(band_names{b})(1), bands.(band_names{b})(2)), ...
         'FontSize', 12, 'FontWeight', 'bold');
end
xlim([0, 8]);
ylim([0, length(band_names)+1]);
title('Frequency Bands', 'FontSize', 14, 'FontWeight', 'bold');

sgtitle('EEG Power Spectral Density Analysis', 'FontSize', 16, 'FontWeight', 'bold');

%% Band Power Analysis

fprintf('Computing band powers...\n\n');

% Compute average band power for each channel
band_powers = zeros(5, length(band_names));

for ch = 1:5
    [pxx, f] = pwelch(eeg_filtered(:, ch), hanning(fs*2), fs, fs*2, fs);

    for b = 1:length(band_names)
        band_range = bands.(band_names{b});
        freq_idx = f >= band_range(1) & f <= band_range(2);
        band_powers(ch, b) = mean(pxx(freq_idx));
    end
end

% Display results
fprintf('Average Band Powers (µV²/Hz):\n');
fprintf('%-15s', 'Channel');
for b = 1:length(band_names)
    fprintf('%-12s', upper(band_names{b}));
end
fprintf('\n');
fprintf('%s\n', repmat('-', 1, 75));

for ch = 1:5
    fprintf('%-15s', eeg.channels{ch});
    for b = 1:length(band_names)
        fprintf('%-12.2f', band_powers(ch, b));
    end
    fprintf('\n');
end

%% Plot band power heatmap

figure('Name', 'Band Power Heatmap', 'NumberTitle', 'off', 'Position', [200, 200, 800, 500]);

imagesc(band_powers);
colorbar;
colormap('hot');

set(gca, 'XTick', 1:length(band_names));
set(gca, 'XTickLabel', upper(band_names));
set(gca, 'YTick', 1:5);
set(gca, 'YTickLabel', eeg.channels);

xlabel('Frequency Band', 'FontWeight', 'bold', 'FontSize', 12);
ylabel('Channel', 'FontWeight', 'bold', 'FontSize', 12);
title('EEG Band Power Heatmap', 'FontSize', 14, 'FontWeight', 'bold');

%% Statistical summary

fprintf('\n=== Statistical Summary ===\n');
fprintf('Mean EEG amplitude: %.2f µV\n', mean(eeg.data(:)));
fprintf('Std EEG amplitude: %.2f µV\n', std(eeg.data(:)));
fprintf('Max EEG amplitude: %.2f µV\n', max(eeg.data(:)));
fprintf('Min EEG amplitude: %.2f µV\n', min(eeg.data(:)));

fprintf('\n Analysis complete!\n');
