classdef MuseUdp < handle
    % MUSEUDP UDP receiver for MuseGUI data streaming
    %
    % This class provides methods to receive real-time Muse sensor data
    % over UDP protocol from the MuseGUI application.
    %
    % Supported data types:
    %   - EEG: 5 channels (TP9, AF7, AF8, TP10, Right AUX) @ 256 Hz
    %   - PPG: 3 channels (PPG1, PPG2, PPG3) @ 64 Hz
    %   - ACC: 3 channels (X, Y, Z) @ 52 Hz
    %   - GYRO: 3 channels (X, Y, Z) @ 52 Hz
    %
    % Example:
    %   mu = MuseUdp();                          % Create receiver
    %   [data, ts, ok] = mu.get_eeg_sample();    % Get single EEG sample
    %   chunk = mu.get_eeg_chunk(50);            % Get 50 EEG samples
    %   mu.close();                              % Close receiver
    %
    % Author: MuseGUI Development Team
    % Version: 1.0.0

    properties (Access = private)
        udp_socket          % UDP socket object
        host                % Host IP address
        port                % UDP port number
        buffer_size         % UDP buffer size
        is_open             % Connection status
    end

    properties (Constant)
        % Packet sizes (bytes)
        EEG_PACKET_SIZE = 24;   % 4 (timestamp) + 20 (5 channels × 4)
        PPG_PACKET_SIZE = 16;   % 4 (timestamp) + 12 (3 channels × 4)
        ACC_PACKET_SIZE = 16;   % 4 (timestamp) + 12 (3 channels × 4)
        GYRO_PACKET_SIZE = 16;  % 4 (timestamp) + 12 (3 channels × 4)

        % Channel counts
        EEG_CHANNELS = 5;
        PPG_CHANNELS = 3;
        ACC_CHANNELS = 3;
        GYRO_CHANNELS = 3;

        % Default settings
        DEFAULT_HOST = '127.0.0.1';
        DEFAULT_PORT = 5000;
        DEFAULT_BUFFER_SIZE = 2048;
    end

    methods
        function obj = MuseUdp(host, port, buffer_size)
            % MUSEUDP Constructor
            %
            % Syntax:
            %   mu = MuseUdp()
            %   mu = MuseUdp(host)
            %   mu = MuseUdp(host, port)
            %   mu = MuseUdp(host, port, buffer_size)
            %
            % Inputs:
            %   host - IP address (default: '127.0.0.1')
            %   port - UDP port (default: 5000)
            %   buffer_size - UDP buffer size (default: 2048 bytes)

            if nargin < 1 || isempty(host)
                host = obj.DEFAULT_HOST;
            end

            if nargin < 2 || isempty(port)
                port = obj.DEFAULT_PORT;
            end

            if nargin < 3 || isempty(buffer_size)
                buffer_size = obj.DEFAULT_BUFFER_SIZE;
            end

            obj.host = host;
            obj.port = port;
            obj.buffer_size = buffer_size;
            obj.is_open = false;

            % Create UDP socket
            obj.open();
        end

        function open(obj)
            % OPEN Open UDP connection

            if obj.is_open
                warning('MuseUdp:AlreadyOpen', 'UDP socket already open');
                return;
            end

            try
                % Create UDP socket
                obj.udp_socket = udpport('datagram', ...
                    'LocalHost', obj.host, ...
                    'LocalPort', obj.port, ...
                    'InputBufferSize', obj.buffer_size);

                % Configure timeout
                configureCallback(obj.udp_socket, 'off');

                obj.is_open = true;
                fprintf('MuseUdp: Connected to %s:%d (buffer: %d bytes)\n', ...
                    obj.host, obj.port, obj.buffer_size);

            catch ME
                error('MuseUdp:OpenFailed', ...
                    'Failed to open UDP socket: %s', ME.message);
            end
        end

        function close(obj)
            % CLOSE Close UDP connection

            if ~obj.is_open
                return;
            end

            try
                clear obj.udp_socket;
                obj.is_open = false;
                fprintf('MuseUdp: Connection closed\n');
            catch ME
                warning('MuseUdp:CloseFailed', ...
                    'Error closing UDP socket: %s', ME.message);
            end
        end

        function [data, timestamp, success] = get_eeg_sample(obj)
            % GET_EEG_SAMPLE Get single EEG sample
            %
            % Returns:
            %   data - 1×5 array of EEG channel values (µV)
            %   timestamp - Sample timestamp (float)
            %   success - True if sample received successfully

            [data, timestamp, success] = obj.get_sample('eeg');
        end

        function [data, timestamp, success] = get_ppg_sample(obj)
            % GET_PPG_SAMPLE Get single PPG sample
            %
            % Returns:
            %   data - 1×3 array of PPG channel values
            %   timestamp - Sample timestamp (float)
            %   success - True if sample received successfully

            [data, timestamp, success] = obj.get_sample('ppg');
        end

        function [data, timestamp, success] = get_acc_sample(obj)
            % GET_ACC_SAMPLE Get single accelerometer sample
            %
            % Returns:
            %   data - 1×3 array of accelerometer values (g)
            %   timestamp - Sample timestamp (float)
            %   success - True if sample received successfully

            [data, timestamp, success] = obj.get_sample('acc');
        end

        function [data, timestamp, success] = get_gyro_sample(obj)
            % GET_GYRO_SAMPLE Get single gyroscope sample
            %
            % Returns:
            %   data - 1×3 array of gyroscope values (deg/s)
            %   timestamp - Sample timestamp (float)
            %   success - True if sample received successfully

            [data, timestamp, success] = obj.get_sample('gyro');
        end

        function chunk = get_eeg_chunk(obj, n_samples)
            % GET_EEG_CHUNK Get multiple EEG samples
            %
            % Inputs:
            %   n_samples - Number of samples to retrieve
            %
            % Returns:
            %   chunk - n_samples×6 matrix [timestamp, ch1, ch2, ch3, ch4, ch5]

            chunk = obj.get_chunk('eeg', n_samples);
        end

        function chunk = get_ppg_chunk(obj, n_samples)
            % GET_PPG_CHUNK Get multiple PPG samples
            %
            % Inputs:
            %   n_samples - Number of samples to retrieve
            %
            % Returns:
            %   chunk - n_samples×4 matrix [timestamp, ch1, ch2, ch3]

            chunk = obj.get_chunk('ppg', n_samples);
        end

        function chunk = get_acc_chunk(obj, n_samples)
            % GET_ACC_CHUNK Get multiple accelerometer samples
            %
            % Inputs:
            %   n_samples - Number of samples to retrieve
            %
            % Returns:
            %   chunk - n_samples×4 matrix [timestamp, X, Y, Z]

            chunk = obj.get_chunk('acc', n_samples);
        end

        function chunk = get_gyro_chunk(obj, n_samples)
            % GET_GYRO_CHUNK Get multiple gyroscope samples
            %
            % Inputs:
            %   n_samples - Number of samples to retrieve
            %
            % Returns:
            %   chunk - n_samples×4 matrix [timestamp, X, Y, Z]

            chunk = obj.get_chunk('gyro', n_samples);
        end

        function set_udp_buffer_size(obj, new_size)
            % SET_UDP_BUFFER_SIZE Change UDP buffer size
            %
            % Inputs:
            %   new_size - New buffer size in bytes
            %
            % Note: Requires closing and reopening the connection

            obj.close();
            obj.buffer_size = new_size;
            obj.open();
        end

        function status = is_connected(obj)
            % IS_CONNECTED Check if UDP socket is open
            %
            % Returns:
            %   status - True if connected

            status = obj.is_open;
        end

        function available = bytes_available(obj)
            % BYTES_AVAILABLE Get number of bytes available
            %
            % Returns:
            %   available - Number of bytes in buffer

            if ~obj.is_open
                available = 0;
                return;
            end

            available = obj.udp_socket.NumDatagramsAvailable;
        end
    end

    methods (Access = private)
        function [data, timestamp, success] = get_sample(obj, data_type)
            % GET_SAMPLE Internal method to get a single sample

            % Initialize outputs
            data = [];
            timestamp = 0;
            success = false;

            if ~obj.is_open
                warning('MuseUdp:NotOpen', 'UDP socket not open');
                return;
            end

            % Determine packet size and channel count
            switch lower(data_type)
                case 'eeg'
                    packet_size = obj.EEG_PACKET_SIZE;
                    n_channels = obj.EEG_CHANNELS;
                case 'ppg'
                    packet_size = obj.PPG_PACKET_SIZE;
                    n_channels = obj.PPG_CHANNELS;
                case 'acc'
                    packet_size = obj.ACC_PACKET_SIZE;
                    n_channels = obj.ACC_CHANNELS;
                case 'gyro'
                    packet_size = obj.GYRO_PACKET_SIZE;
                    n_channels = obj.GYRO_CHANNELS;
                otherwise
                    error('MuseUdp:InvalidType', 'Unknown data type: %s', data_type);
            end

            try
                % Read UDP packet
                if obj.udp_socket.NumDatagramsAvailable > 0
                    packet = read(obj.udp_socket, 1, 'uint8');

                    % Check packet size
                    if length(packet.Data) ~= packet_size
                        warning('MuseUdp:InvalidPacket', ...
                            'Invalid packet size: %d (expected %d)', ...
                            length(packet.Data), packet_size);
                        return;
                    end

                    % Parse packet: timestamp (float32) + channels (float32s)
                    values = typecast(uint8(packet.Data), 'single');
                    timestamp = double(values(1));
                    data = double(values(2:end));
                    success = true;
                else
                    % No data available
                    data = zeros(1, n_channels);
                end

            catch ME
                warning('MuseUdp:ReadError', 'Error reading UDP: %s', ME.message);
                data = zeros(1, n_channels);
            end
        end

        function chunk = get_chunk(obj, data_type, n_samples)
            % GET_CHUNK Internal method to get multiple samples

            % Determine channel count
            switch lower(data_type)
                case 'eeg'
                    n_channels = obj.EEG_CHANNELS;
                case 'ppg'
                    n_channels = obj.PPG_CHANNELS;
                case 'acc'
                    n_channels = obj.ACC_CHANNELS;
                case 'gyro'
                    n_channels = obj.GYRO_CHANNELS;
                otherwise
                    error('MuseUdp:InvalidType', 'Unknown data type: %s', data_type);
            end

            % Preallocate chunk matrix
            chunk = zeros(n_samples, n_channels + 1);  % +1 for timestamp

            % Collect samples
            for i = 1:n_samples
                [data, timestamp, success] = obj.get_sample(data_type);

                if success
                    chunk(i, :) = [timestamp, data];
                else
                    % Pad with zeros if sample not available
                    chunk(i, :) = zeros(1, n_channels + 1);
                end

                % Small pause to avoid overwhelming the buffer
                pause(0.001);
            end
        end
    end

    methods (Static)
        function demo()
            % DEMO Demonstrate MuseUdp usage

            fprintf('=== MuseUdp Demo ===\n\n');

            try
                % Create receiver
                fprintf('Creating UDP receiver...\n');
                mu = MuseUdp();

                % Wait for data
                fprintf('Waiting for data (make sure MuseGUI is streaming)...\n');
                pause(2);

                % Get single samples
                fprintf('\nRetrieving single samples:\n');
                [eeg_data, eeg_ts, eeg_ok] = mu.get_eeg_sample();
                if eeg_ok
                    fprintf('  EEG [%.3f]: %s\n', eeg_ts, mat2str(eeg_data, 3));
                end

                [ppg_data, ppg_ts, ppg_ok] = mu.get_ppg_sample();
                if ppg_ok
                    fprintf('  PPG [%.3f]: %s\n', ppg_ts, mat2str(ppg_data, 3));
                end

                % Get chunks
                fprintf('\nRetrieving 10-sample chunks:\n');
                eeg_chunk = mu.get_eeg_chunk(10);
                fprintf('  EEG chunk size: %d×%d\n', size(eeg_chunk, 1), size(eeg_chunk, 2));

                ppg_chunk = mu.get_ppg_chunk(10);
                fprintf('  PPG chunk size: %d×%d\n', size(ppg_chunk, 1), size(ppg_chunk, 2));

                % Close
                mu.close();
                fprintf('\nDemo complete!\n');

            catch ME
                fprintf('Error: %s\n', ME.message);
            end
        end
    end
end
