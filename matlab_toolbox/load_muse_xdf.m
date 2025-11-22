function [eeg, ppg, acc, gyro, markers] = load_muse_xdf(filepath)
% LOAD_MUSE_XDF Load Muse data from XDF file
%
% This function loads Muse sensor data from an XDF file recorded with
% Lab Recorder or MuseGUI. It automatically identifies and separates
% different data streams (EEG, PPG, accelerometer, gyroscope, markers).
%
% Syntax:
%   [eeg, ppg, acc, gyro, markers] = load_muse_xdf(filepath)
%
% Inputs:
%   filepath - Path to XDF file
%
% Outputs:
%   eeg - Structure with EEG data
%     .data - n_samples × 5 matrix (TP9, AF7, AF8, TP10, Right AUX)
%     .timestamps - n_samples × 1 vector
%     .srate - Sampling rate (Hz)
%     .channels - Cell array of channel names
%   ppg - Structure with PPG data (same format as EEG)
%   acc - Structure with accelerometer data (same format)
%   gyro - Structure with gyroscope data (same format)
%   markers - Structure with event markers
%     .timestamps - n_markers × 1 vector
%     .labels - Cell array of marker labels
%
% Example:
%   [eeg, ppg, acc, gyro, markers] = load_muse_xdf('recording.xdf');
%   plot(eeg.timestamps, eeg.data(:, 2)); % Plot AF7 channel
%
% Requires:
%   xdf MATLAB library (https://github.com/xdf-modules/xdf-Matlab)
%
% Author: MuseGUI Development Team
% Version: 1.0.0

    % Check if xdf is available
    if ~exist('load_xdf', 'file')
        error('XDF library not found. Install from: https://github.com/xdf-modules/xdf-Matlab');
    end

    % Check file exists
    if ~exist(filepath, 'file')
        error('File not found: %s', filepath);
    end

    fprintf('Loading XDF file: %s\n', filepath);

    % Load XDF file
    try
        streams = load_xdf(filepath);
    catch ME
        error('Failed to load XDF file: %s', ME.message);
    end

    fprintf('Found %d stream(s)\n', length(streams));

    % Initialize output structures
    eeg = struct('data', [], 'timestamps', [], 'srate', 0, 'channels', {{}});
    ppg = struct('data', [], 'timestamps', [], 'srate', 0, 'channels', {{}});
    acc = struct('data', [], 'timestamps', [], 'srate', 0, 'channels', {{}});
    gyro = struct('data', [], 'timestamps', [], 'srate', 0, 'channels', {{}});
    markers = struct('timestamps', [], 'labels', {{}});

    % Parse streams
    for i = 1:length(streams)
        stream = streams{i};
        stream_info = stream.info;

        % Get stream type
        if isfield(stream_info, 'type')
            stream_type = stream_info.type;
        else
            continue;
        end

        fprintf('  Stream %d: %s (%s)\n', i, stream_info.name, stream_type);

        % Extract data based on type
        switch stream_type
            case 'EEG'
                eeg = parse_stream(stream, 'EEG');

            case 'PPG'
                ppg = parse_stream(stream, 'PPG');

            case 'Accelerometer'
                acc = parse_stream(stream, 'Accelerometer');

            case 'Gyroscope'
                gyro = parse_stream(stream, 'Gyroscope');

            case 'Markers'
                markers = parse_markers(stream);

            otherwise
                fprintf('    Warning: Unknown stream type: %s\n', stream_type);
        end
    end

    fprintf('XDF loading complete!\n');
    fprintf('  EEG: %d samples @ %.1f Hz\n', size(eeg.data, 1), eeg.srate);
    if ~isempty(ppg.data)
        fprintf('  PPG: %d samples @ %.1f Hz\n', size(ppg.data, 1), ppg.srate);
    end
    if ~isempty(acc.data)
        fprintf('  ACC: %d samples @ %.1f Hz\n', size(acc.data, 1), acc.srate);
    end
    if ~isempty(gyro.data)
        fprintf('  GYRO: %d samples @ %.1f Hz\n', size(gyro.data, 1), gyro.srate);
    end
    if ~isempty(markers.timestamps)
        fprintf('  Markers: %d events\n', length(markers.timestamps));
    end
end


function data_struct = parse_stream(stream, stream_type)
    % Parse numerical data stream

    data_struct = struct();

    % Get time series data
    if isfield(stream, 'time_series')
        data_struct.data = stream.time_series';  % Transpose to n_samples × n_channels
    else
        data_struct.data = [];
    end

    % Get timestamps
    if isfield(stream, 'time_stamps')
        data_struct.timestamps = stream.time_stamps(:);
    else
        data_struct.timestamps = [];
    end

    % Get sampling rate
    if isfield(stream.info, 'nominal_srate')
        data_struct.srate = str2double(stream.info.nominal_srate);
    else
        data_struct.srate = 0;
    end

    % Get channel labels
    data_struct.channels = {};
    if isfield(stream.info, 'desc') && isfield(stream.info.desc, 'channels')
        channels_desc = stream.info.desc.channels;
        if isfield(channels_desc, 'channel')
            channels = channels_desc.channel;
            if iscell(channels)
                for i = 1:length(channels)
                    if isfield(channels{i}, 'label')
                        data_struct.channels{i} = channels{i}.label;
                    else
                        data_struct.channels{i} = sprintf('Ch%d', i);
                    end
                end
            end
        end
    end

    % Default channel names if not found
    if isempty(data_struct.channels) && ~isempty(data_struct.data)
        n_channels = size(data_struct.data, 2);
        switch stream_type
            case 'EEG'
                data_struct.channels = {'TP9', 'AF7', 'AF8', 'TP10', 'Right AUX'};
            case 'PPG'
                data_struct.channels = {'PPG1', 'PPG2', 'PPG3'};
            case 'Accelerometer'
                data_struct.channels = {'X', 'Y', 'Z'};
            case 'Gyroscope'
                data_struct.channels = {'X', 'Y', 'Z'};
            otherwise
                for i = 1:n_channels
                    data_struct.channels{i} = sprintf('Ch%d', i);
                end
        end
    end
end


function markers_struct = parse_markers(stream)
    % Parse marker/event stream

    markers_struct = struct();

    % Get timestamps
    if isfield(stream, 'time_stamps')
        markers_struct.timestamps = stream.time_stamps(:);
    else
        markers_struct.timestamps = [];
    end

    % Get labels
    if isfield(stream, 'time_series')
        labels = stream.time_series;
        if iscell(labels)
            markers_struct.labels = labels(:);
        else
            % Convert to cell array
            markers_struct.labels = cellstr(labels);
        end
    else
        markers_struct.labels = {};
    end
end
