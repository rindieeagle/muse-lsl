"""
Automatic Artifact Detection
Detects common EEG artifacts in real-time
"""

import logging
import numpy as np
from collections import deque
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ArtifactType(Enum):
    """Types of artifacts"""
    EYE_BLINK = "eye_blink"
    JAW_CLENCH = "jaw_clench"
    MOVEMENT = "movement"
    ELECTRODE_DISCONNECTION = "electrode_disconnection"
    HIGH_FREQUENCY_NOISE = "high_frequency_noise"
    SATURATION = "saturation"


@dataclass
class ArtifactEvent:
    """Represents a detected artifact"""
    artifact_type: ArtifactType
    timestamp: float
    channel: int
    severity: float  # 0-1 scale
    description: str

    def __repr__(self):
        return f"{self.artifact_type.value} on ch{self.channel} (severity: {self.severity:.2f})"


class ArtifactDetector:
    """
    Real-time EEG artifact detection

    Detects:
    - Eye blinks (large frontal spikes in AF7/AF8)
    - Jaw clenching (high beta/gamma in temporal)
    - Movement artifacts (correlated with ACC/GYRO)
    - Electrode disconnections (flatline or extreme values)
    - High-frequency noise
    - Saturation
    """

    def __init__(self, sample_rate: int = 256):
        """
        Initialize artifact detector

        Args:
            sample_rate: EEG sample rate (Hz)
        """
        self.sample_rate = sample_rate

        # Data buffers (per channel)
        self.buffer_size = 256  # 1 second
        self.eeg_buffers = [deque(maxlen=self.buffer_size) for _ in range(5)]
        self.acc_buffer = deque(maxlen=52)  # 1 second at 52 Hz
        self.gyro_buffer = deque(maxlen=52)

        # Artifact history
        self.detected_artifacts: List[ArtifactEvent] = []
        self.max_history = 100

        # Detection thresholds
        self.thresholds = {
            'eye_blink_amplitude': 150,      # µV (frontal spike)
            'jaw_clench_beta_ratio': 2.0,    # Beta power ratio
            'movement_acc_threshold': 1.5,   # g (acceleration)
            'flatline_variance': 0.1,        # µV² (near-zero variance)
            'saturation_level': 1800,        # µV (near ADC limits)
            'noise_std': 100,                # µV (high standard deviation)
        }

        # Channel names
        self.channel_names = ['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX']

        # Artifact counters
        self.artifact_counts = {art_type: 0 for art_type in ArtifactType}

        logger.info("Artifact Detector initialized")

    def add_eeg_sample(self, sample: List[float]):
        """
        Add EEG sample to buffers

        Args:
            sample: List of 5 EEG channel values (µV)
        """
        for i, value in enumerate(sample[:5]):
            self.eeg_buffers[i].append(value)

    def add_acc_sample(self, sample: List[float]):
        """
        Add accelerometer sample

        Args:
            sample: List of 3 ACC values (X, Y, Z in g)
        """
        self.acc_buffer.append(sample[:3])

    def add_gyro_sample(self, sample: List[float]):
        """
        Add gyroscope sample

        Args:
            sample: List of 3 GYRO values (X, Y, Z in deg/s)
        """
        self.gyro_buffer.append(sample[:3])

    def detect_artifacts(self, timestamp: float) -> List[ArtifactEvent]:
        """
        Detect artifacts in current buffer

        Args:
            timestamp: Current timestamp

        Returns:
            List of detected artifacts
        """
        artifacts = []

        # Check if we have enough data
        if len(self.eeg_buffers[0]) < 128:
            return artifacts

        # Detect different artifact types
        artifacts.extend(self._detect_eye_blinks(timestamp))
        artifacts.extend(self._detect_jaw_clenching(timestamp))
        artifacts.extend(self._detect_movement(timestamp))
        artifacts.extend(self._detect_disconnections(timestamp))
        artifacts.extend(self._detect_saturation(timestamp))
        artifacts.extend(self._detect_noise(timestamp))

        # Store artifacts
        for artifact in artifacts:
            self.detected_artifacts.append(artifact)
            self.artifact_counts[artifact.artifact_type] += 1

        # Limit history
        if len(self.detected_artifacts) > self.max_history:
            self.detected_artifacts = self.detected_artifacts[-self.max_history:]

        return artifacts

    def _detect_eye_blinks(self, timestamp: float) -> List[ArtifactEvent]:
        """
        Detect eye blinks (frontal spikes)

        Eye blinks cause large amplitude spikes in frontal channels (AF7, AF8)
        """
        artifacts = []

        # Check AF7 (channel 1) and AF8 (channel 2)
        for ch_idx in [1, 2]:
            if len(self.eeg_buffers[ch_idx]) < 32:
                continue

            # Get recent data (last 125ms)
            recent_data = list(self.eeg_buffers[ch_idx])[-32:]
            data_array = np.array(recent_data)

            # Look for large amplitude spike
            max_amplitude = np.max(np.abs(data_array))

            if max_amplitude > self.thresholds['eye_blink_amplitude']:
                severity = min(max_amplitude / (self.thresholds['eye_blink_amplitude'] * 2), 1.0)

                artifact = ArtifactEvent(
                    artifact_type=ArtifactType.EYE_BLINK,
                    timestamp=timestamp,
                    channel=ch_idx,
                    severity=severity,
                    description=f"Eye blink detected on {self.channel_names[ch_idx]} ({max_amplitude:.1f} µV)"
                )
                artifacts.append(artifact)

        return artifacts

    def _detect_jaw_clenching(self, timestamp: float) -> List[ArtifactEvent]:
        """
        Detect jaw clenching (elevated high-frequency activity)

        Jaw clenching causes high beta/gamma activity in temporal channels
        """
        artifacts = []

        # Check temporal channels (TP9, TP10)
        for ch_idx in [0, 3]:
            if len(self.eeg_buffers[ch_idx]) < 128:
                continue

            data = np.array(list(self.eeg_buffers[ch_idx])[-128:])

            # Compute FFT
            fft = np.fft.rfft(data)
            freqs = np.fft.rfftfreq(len(data), 1.0 / self.sample_rate)

            # Get beta (13-30 Hz) and low frequency (4-13 Hz) power
            beta_idx = np.logical_and(freqs >= 13, freqs <= 30)
            low_idx = np.logical_and(freqs >= 4, freqs <= 13)

            beta_power = np.mean(np.abs(fft[beta_idx]))
            low_power = np.mean(np.abs(fft[low_idx]))

            # Check ratio
            if low_power > 0:
                ratio = beta_power / low_power

                if ratio > self.thresholds['jaw_clench_beta_ratio']:
                    severity = min((ratio - self.thresholds['jaw_clench_beta_ratio']) / 3.0, 1.0)

                    artifact = ArtifactEvent(
                        artifact_type=ArtifactType.JAW_CLENCH,
                        timestamp=timestamp,
                        channel=ch_idx,
                        severity=severity,
                        description=f"Jaw clenching on {self.channel_names[ch_idx]} (β/α ratio: {ratio:.2f})"
                    )
                    artifacts.append(artifact)

        return artifacts

    def _detect_movement(self, timestamp: float) -> List[ArtifactEvent]:
        """
        Detect movement artifacts (correlated with ACC/GYRO)

        Large accelerometer or gyroscope values indicate head movement
        """
        artifacts = []

        if len(self.acc_buffer) < 10:
            return artifacts

        # Get recent ACC data
        acc_data = np.array(list(self.acc_buffer)[-10:])

        # Compute acceleration magnitude
        acc_magnitude = np.linalg.norm(acc_data, axis=1)

        # Check for large movements
        max_acc = np.max(acc_magnitude)

        if max_acc > self.thresholds['movement_acc_threshold']:
            severity = min((max_acc - self.thresholds['movement_acc_threshold']) / 2.0, 1.0)

            artifact = ArtifactEvent(
                artifact_type=ArtifactType.MOVEMENT,
                timestamp=timestamp,
                channel=-1,  # Affects all channels
                severity=severity,
                description=f"Movement detected (acceleration: {max_acc:.2f} g)"
            )
            artifacts.append(artifact)

        return artifacts

    def _detect_disconnections(self, timestamp: float) -> List[ArtifactEvent]:
        """
        Detect electrode disconnections (flatline)

        Disconnected electrodes show very low variance or constant values
        """
        artifacts = []

        for ch_idx in range(5):
            if len(self.eeg_buffers[ch_idx]) < 64:
                continue

            data = np.array(list(self.eeg_buffers[ch_idx])[-64:])

            # Check variance
            variance = np.var(data)

            if variance < self.thresholds['flatline_variance']:
                severity = 1.0 - (variance / self.thresholds['flatline_variance'])

                artifact = ArtifactEvent(
                    artifact_type=ArtifactType.ELECTRODE_DISCONNECTION,
                    timestamp=timestamp,
                    channel=ch_idx,
                    severity=severity,
                    description=f"Possible disconnection on {self.channel_names[ch_idx]} (variance: {variance:.3f})"
                )
                artifacts.append(artifact)

        return artifacts

    def _detect_saturation(self, timestamp: float) -> List[ArtifactEvent]:
        """
        Detect signal saturation (near ADC limits)

        Saturated signals indicate electrode issues or extreme artifacts
        """
        artifacts = []

        for ch_idx in range(5):
            if len(self.eeg_buffers[ch_idx]) < 16:
                continue

            data = np.array(list(self.eeg_buffers[ch_idx])[-16:])

            # Check for values near saturation
            max_val = np.max(np.abs(data))

            if max_val > self.thresholds['saturation_level']:
                severity = min(max_val / 2000.0, 1.0)

                artifact = ArtifactEvent(
                    artifact_type=ArtifactType.SATURATION,
                    timestamp=timestamp,
                    channel=ch_idx,
                    severity=severity,
                    description=f"Saturation on {self.channel_names[ch_idx]} ({max_val:.1f} µV)"
                )
                artifacts.append(artifact)

        return artifacts

    def _detect_noise(self, timestamp: float) -> List[ArtifactEvent]:
        """
        Detect high-frequency noise

        Excessive variance or standard deviation indicates noisy signal
        """
        artifacts = []

        for ch_idx in range(5):
            if len(self.eeg_buffers[ch_idx]) < 64:
                continue

            data = np.array(list(self.eeg_buffers[ch_idx])[-64:])

            # Check standard deviation
            std = np.std(data)

            if std > self.thresholds['noise_std']:
                severity = min(std / (self.thresholds['noise_std'] * 2), 1.0)

                artifact = ArtifactEvent(
                    artifact_type=ArtifactType.HIGH_FREQUENCY_NOISE,
                    timestamp=timestamp,
                    channel=ch_idx,
                    severity=severity,
                    description=f"Noisy signal on {self.channel_names[ch_idx]} (σ: {std:.1f} µV)"
                )
                artifacts.append(artifact)

        return artifacts

    def get_artifact_summary(self) -> Dict[str, int]:
        """
        Get summary of detected artifacts

        Returns:
            Dictionary with counts per artifact type
        """
        return self.artifact_counts.copy()

    def get_recent_artifacts(self, n: int = 10) -> List[ArtifactEvent]:
        """
        Get most recent artifacts

        Args:
            n: Number of artifacts to return

        Returns:
            List of recent artifacts
        """
        return self.detected_artifacts[-n:]

    def clear_history(self):
        """Clear artifact history"""
        self.detected_artifacts.clear()
        self.artifact_counts = {art_type: 0 for art_type in ArtifactType}
        logger.info("Artifact history cleared")

    def get_signal_quality_score(self) -> float:
        """
        Calculate overall signal quality score

        Returns:
            Quality score (0-100, higher is better)
        """
        if len(self.detected_artifacts) == 0:
            return 100.0

        # Count recent artifacts (last 30)
        recent = self.detected_artifacts[-30:]

        # Weight artifacts by severity
        total_severity = sum(a.severity for a in recent)

        # Calculate score (more artifacts = lower score)
        score = max(0, 100 - (total_severity * 10))

        return score

    def set_threshold(self, threshold_name: str, value: float):
        """
        Set detection threshold

        Args:
            threshold_name: Name of threshold
            value: New threshold value
        """
        if threshold_name in self.thresholds:
            self.thresholds[threshold_name] = value
            logger.info(f"Threshold updated: {threshold_name} = {value}")
        else:
            logger.warning(f"Unknown threshold: {threshold_name}")
