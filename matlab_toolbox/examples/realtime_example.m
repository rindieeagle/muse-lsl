% REALTIME_EXAMPLE Real-time Muse data visualization example
%
% This example demonstrates how to receive and visualize Muse EEG data
% in real-time using the MuseUdp class.
%
% Requirements:
%   - MuseGUI running with UDP streaming enabled
%   - Instrument Control Toolbox (for UDP communication)
%
% Author: MuseGUI Development Team

%% Setup
clear; close all; clc;

fprintf('=== Real-Time Muse EEG Visualization ===\n\n');

% Create UDP receiver
fprintf('Creating UDP receiver...\n');
mu = MuseUdp('127.0.0.1', 5000);

% Channel names
channels = {'TP9', 'AF7', 'AF8', 'TP10', 'Right AUX'};

% Buffer settings
buffer_duration = 5;  % seconds
sample_rate = 256;    % Hz (EEG)
buffer_size = buffer_duration * sample_rate;

% Initialize data buffers
time_buffer = zeros(buffer_size, 1);
eeg_buffer = zeros(buffer_size, 5);
buffer_idx = 1;

% Create figure
fig = figure('Name', 'Real-Time Muse EEG', 'NumberTitle', 'off');
fig.Position = [100, 100, 1200, 800];

% Create subplots for each channel
plots = cell(5, 1);
lines = cell(5, 1);

for ch = 1:5
    plots{ch} = subplot(5, 1, ch);
    lines{ch} = line(plots{ch}, 'XData', [], 'YData', [], 'Color', [0 0.6 0.8], 'LineWidth', 1.5);
    ylabel(channels{ch}, 'FontWeight', 'bold');
    ylim([-200, 200]);
    xlim([0, buffer_duration]);
    grid on;

    if ch == 5
        xlabel('Time (seconds)');
    else
        set(gca, 'XTickLabel', []);
    end
end

sgtitle('Real-Time EEG from Muse', 'FontSize', 16, 'FontWeight', 'bold');

fprintf('Visualization started. Press Ctrl+C to stop.\n\n');

%% Real-time loop
start_time = [];

try
    while ishandle(fig)
        % Get EEG sample
        [data, timestamp, success] = mu.get_eeg_sample();

        if success
            % Initialize start time
            if isempty(start_time)
                start_time = timestamp;
                fprintf('First sample received at t=%.3f\n', timestamp);
            end

            % Calculate relative time
            rel_time = timestamp - start_time;

            % Add to circular buffer
            time_buffer(buffer_idx) = rel_time;
            eeg_buffer(buffer_idx, :) = data;

            % Update buffer index
            buffer_idx = buffer_idx + 1;
            if buffer_idx > buffer_size
                buffer_idx = 1;
            end

            % Update plots every 10 samples
            if mod(buffer_idx, 10) == 0
                % Rearrange data to be chronological
                if buffer_idx == buffer_size
                    t_plot = time_buffer;
                    eeg_plot = eeg_buffer;
                else
                    t_plot = [time_buffer(buffer_idx:end); time_buffer(1:buffer_idx-1)];
                    eeg_plot = [eeg_buffer(buffer_idx:end, :); eeg_buffer(1:buffer_idx-1, :)];
                end

                % Remove zeros (empty buffer slots)
                valid = t_plot > 0;
                t_plot = t_plot(valid);
                eeg_plot = eeg_plot(valid, :);

                % Update each channel
                for ch = 1:5
                    set(lines{ch}, 'XData', t_plot, 'YData', eeg_plot(:, ch));

                    % Auto-scroll x-axis
                    if ~isempty(t_plot) && max(t_plot) > buffer_duration
                        xlim(plots{ch}, [max(t_plot) - buffer_duration, max(t_plot)]);
                    end
                end

                drawnow;
            end
        else
            pause(0.001);  % Small pause to avoid overwhelming CPU
        end
    end
catch ME
    fprintf('\nVisualization stopped: %s\n', ME.message);
end

%% Cleanup
fprintf('\nClosing UDP receiver...\n');
mu.close();
fprintf('Done!\n');
