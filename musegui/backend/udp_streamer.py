"""
UDP Streamer for MATLAB Integration
Transmits Muse data over UDP protocol for real-time MATLAB processing
"""

import socket
import struct
import logging
import threading
from typing import Optional, Callable
from queue import Queue, Empty
import time

logger = logging.getLogger(__name__)


class UDPStreamer:
    """
    UDP data streamer for transmitting Muse sensor data to MATLAB

    Packet formats:
    - EEG: 4 bytes timestamp + 20 bytes data (5 channels × 4 bytes float) = 24 bytes
    - PPG: 4 bytes timestamp + 12 bytes data (3 channels × 4 bytes float) = 16 bytes
    - ACC: 4 bytes timestamp + 12 bytes data (3 channels × 4 bytes float) = 16 bytes
    - GYRO: 4 bytes timestamp + 12 bytes data (3 channels × 4 bytes float) = 16 bytes
    """

    def __init__(self, host: str = '127.0.0.1', port: int = 5000):
        """
        Initialize UDP streamer

        Args:
            host: Target IP address (default: localhost)
            port: Target UDP port (default: 5000)
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.is_streaming = False

        # Separate queues for different data types
        self.eeg_queue = Queue(maxsize=1000)
        self.ppg_queue = Queue(maxsize=1000)
        self.acc_queue = Queue(maxsize=1000)
        self.gyro_queue = Queue(maxsize=1000)

        # Worker threads
        self.threads = []

        # Statistics
        self.packets_sent = {'eeg': 0, 'ppg': 0, 'acc': 0, 'gyro': 0}
        self.bytes_sent = 0
        self.errors = 0

        logger.info(f"UDP Streamer initialized: {host}:{port}")

    def start(self):
        """Start UDP streaming"""
        if self.is_streaming:
            logger.warning("UDP streaming already started")
            return

        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)

            self.is_streaming = True

            # Start worker threads for each data type
            self.threads = [
                threading.Thread(target=self._stream_worker, args=('eeg', self.eeg_queue, 24), daemon=True),
                threading.Thread(target=self._stream_worker, args=('ppg', self.ppg_queue, 16), daemon=True),
                threading.Thread(target=self._stream_worker, args=('acc', self.acc_queue, 16), daemon=True),
                threading.Thread(target=self._stream_worker, args=('gyro', self.gyro_queue, 16), daemon=True),
            ]

            for thread in self.threads:
                thread.start()

            logger.info("UDP streaming started")

        except Exception as e:
            logger.error(f"Failed to start UDP streaming: {e}")
            self.is_streaming = False
            raise

    def stop(self):
        """Stop UDP streaming"""
        if not self.is_streaming:
            return

        self.is_streaming = False

        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=1.0)

        # Close socket
        if self.socket:
            self.socket.close()
            self.socket = None

        # Clear queues
        self._clear_queue(self.eeg_queue)
        self._clear_queue(self.ppg_queue)
        self._clear_queue(self.acc_queue)
        self._clear_queue(self.gyro_queue)

        logger.info(f"UDP streaming stopped. Stats: {self.get_stats()}")

    def send_eeg_sample(self, timestamp: float, channels: list):
        """
        Send EEG sample via UDP

        Args:
            timestamp: Sample timestamp (float)
            channels: List of 5 EEG channel values [TP9, AF7, AF8, TP10, AUX]
        """
        if not self.is_streaming:
            return

        if len(channels) != 5:
            logger.error(f"Invalid EEG channel count: {len(channels)}, expected 5")
            return

        try:
            self.eeg_queue.put_nowait((timestamp, channels))
        except:
            # Queue full, skip sample
            pass

    def send_ppg_sample(self, timestamp: float, channels: list):
        """
        Send PPG sample via UDP

        Args:
            timestamp: Sample timestamp (float)
            channels: List of 3 PPG channel values
        """
        if not self.is_streaming:
            return

        if len(channels) != 3:
            logger.error(f"Invalid PPG channel count: {len(channels)}, expected 3")
            return

        try:
            self.ppg_queue.put_nowait((timestamp, channels))
        except:
            pass

    def send_acc_sample(self, timestamp: float, channels: list):
        """
        Send accelerometer sample via UDP

        Args:
            timestamp: Sample timestamp (float)
            channels: List of 3 accelerometer values [X, Y, Z]
        """
        if not self.is_streaming:
            return

        if len(channels) != 3:
            logger.error(f"Invalid ACC channel count: {len(channels)}, expected 3")
            return

        try:
            self.acc_queue.put_nowait((timestamp, channels))
        except:
            pass

    def send_gyro_sample(self, timestamp: float, channels: list):
        """
        Send gyroscope sample via UDP

        Args:
            timestamp: Sample timestamp (float)
            channels: List of 3 gyroscope values [X, Y, Z]
        """
        if not self.is_streaming:
            return

        if len(channels) != 3:
            logger.error(f"Invalid GYRO channel count: {len(channels)}, expected 3")
            return

        try:
            self.gyro_queue.put_nowait((timestamp, channels))
        except:
            pass

    def _stream_worker(self, data_type: str, queue: Queue, packet_size: int):
        """
        Worker thread for streaming data

        Args:
            data_type: Type of data (eeg, ppg, acc, gyro)
            queue: Queue containing data samples
            packet_size: Expected packet size in bytes
        """
        logger.debug(f"Started UDP worker for {data_type}")

        while self.is_streaming:
            try:
                # Get sample from queue (with timeout)
                timestamp, channels = queue.get(timeout=0.1)

                # Pack data into binary format
                # Format: float (timestamp) + n floats (channels)
                packet = struct.pack(f'<{1 + len(channels)}f', timestamp, *channels)

                # Verify packet size
                if len(packet) != packet_size:
                    logger.error(f"Unexpected packet size for {data_type}: {len(packet)} != {packet_size}")
                    continue

                # Send packet
                self.socket.sendto(packet, (self.host, self.port))

                # Update statistics
                self.packets_sent[data_type] += 1
                self.bytes_sent += len(packet)

            except Empty:
                # No data available, continue
                continue
            except Exception as e:
                if self.is_streaming:  # Only log if still supposed to be streaming
                    logger.error(f"Error sending {data_type} packet: {e}")
                    self.errors += 1

        logger.debug(f"Stopped UDP worker for {data_type}")

    def _clear_queue(self, queue: Queue):
        """Clear all items from a queue"""
        while not queue.empty():
            try:
                queue.get_nowait()
            except Empty:
                break

    def get_stats(self) -> dict:
        """Get streaming statistics"""
        return {
            'packets_sent': self.packets_sent.copy(),
            'total_packets': sum(self.packets_sent.values()),
            'bytes_sent': self.bytes_sent,
            'errors': self.errors,
            'is_streaming': self.is_streaming,
            'queue_sizes': {
                'eeg': self.eeg_queue.qsize(),
                'ppg': self.ppg_queue.qsize(),
                'acc': self.acc_queue.qsize(),
                'gyro': self.gyro_queue.qsize(),
            }
        }

    def reset_stats(self):
        """Reset streaming statistics"""
        self.packets_sent = {'eeg': 0, 'ppg': 0, 'acc': 0, 'gyro': 0}
        self.bytes_sent = 0
        self.errors = 0

    def __del__(self):
        """Cleanup on deletion"""
        self.stop()
