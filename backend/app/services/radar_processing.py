import numpy as np
from scipy import signal
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class AnomalyType(Enum):
    METAL = "metal"
    STONE = "stone"
    VOID = "void"
    ORGANIC = "organic"
    UNKNOWN = "unknown"

@dataclass
class AnomalyDetectionResult:
    x: float
    y: float
    type: AnomalyType
    confidence: float
    amplitude: float
    depth: float

class RadarProcessor:
    """
    Service for processing Ground Penetrating Radar (GPR) data to detect anomalies
    and classify them based on signal characteristics.
    """
    
    def __init__(self):
        # Signal processing parameters
        self.noise_threshold = 0.1
        self.signal_threshold = 0.3
        self.min_anomaly_separation = 0.5  # Minimum distance between anomalies
        self.depth_resolution = 0.1  # meters per sample
        self.frequency_band = (10, 1000)  # MHz
        
    def preprocess_signal(self, raw_signal: List[float], sampling_rate: float = 1000.0) -> np.ndarray:
        """
        Preprocess raw radar signal to reduce noise and enhance features.
        
        Args:
            raw_signal: Raw radar signal data
            sampling_rate: Sampling rate in Hz
            
        Returns:
            Denoised and enhanced signal
        """
        signal_array = np.array(raw_signal)
        
        # If signal is too short, return as is
        if len(signal_array) < 3:
            return signal_array
        
        # Apply bandpass filter to remove noise outside expected frequency range
        nyquist = sampling_rate / 2
        
        # Ensure frequencies are within valid range (0, 1) for digital filters
        low_freq = max(0.01, min(0.99, self.frequency_band[0] / nyquist))
        high_freq = max(0.01, min(0.99, self.frequency_band[1] / nyquist))
        
        # Ensure low_freq < high_freq
        if low_freq >= high_freq:
            low_freq = 0.01
            high_freq = 0.99
        
        # Only apply filter if signal is long enough for the filter padding
        if len(signal_array) > 8:  # Need at least some length for filtering
            try:
                # Design Butterworth bandpass filter
                b, a = signal.butter(4, [low_freq, high_freq], btype='band', analog=False)
                filtered_signal = signal.filtfilt(b, a, signal_array)
            except Exception:
                # If filtering fails, use the original signal
                filtered_signal = signal_array
        else:
            # If signal is too short, skip filtering
            filtered_signal = signal_array
        
        # Apply additional smoothing with Savitzky-Golay filter if signal is long enough
        if len(filtered_signal) > 5:
            # Ensure window length is appropriate and odd
            window_length = min(5, len(filtered_signal))
            if window_length % 2 == 0:
                window_length -= 1  # Make it odd
            if window_length < 3:
                window_length = 3  # Minimum for polynomial order 3
            if len(filtered_signal) >= window_length:
                smoothed_signal = signal.savgol_filter(filtered_signal, window_length, 3)
            else:
                smoothed_signal = filtered_signal
        else:
            smoothed_signal = filtered_signal
        
        return smoothed_signal
    
    def detect_reflections(self, processed_signal: np.ndarray) -> List[Tuple[int, float]]:
        """
        Detect signal reflections that indicate subsurface objects.
        
        Args:
            processed_signal: Preprocessed radar signal
            
        Returns:
            List of (index, amplitude) tuples for detected reflections
        """
        # Find peaks in the signal
        peaks, properties = signal.find_peaks(
            np.abs(processed_signal),
            height=self.signal_threshold,
            distance=int(self.min_anomaly_separation / self.depth_resolution)  # Convert to samples
        )
        
        # Create list of (index, amplitude) pairs
        reflections = [(peak_idx, processed_signal[peak_idx]) for peak_idx in peaks]
        
        return reflections
    
    def classify_anomaly(self, reflection_amplitude: float, signal_width: float, 
                        depth: float, surrounding_signals: List[float]) -> Tuple[AnomalyType, float]:
        """
        Classify anomaly type based on signal characteristics.
        
        Args:
            reflection_amplitude: Amplitude of the reflection
            signal_width: Width of the signal response
            depth: Depth of the anomaly
            surrounding_signals: Signals in surrounding area
            
        Returns:
            Tuple of (anomaly_type, confidence)
        """
        # Calculate various signal features
        abs_amplitude = abs(reflection_amplitude)
        
        # Metal objects typically have strong, sharp reflections
        if abs_amplitude > 0.7 and signal_width < 5:
            confidence = min(0.95, abs_amplitude)
            return AnomalyType.METAL, confidence
        
        # Stone/rock objects have moderate, broader reflections
        elif 0.3 < abs_amplitude < 0.7 and signal_width > 8:
            confidence = min(0.85, abs_amplitude * 1.1)
            return AnomalyType.STONE, confidence
        
        # Organic materials often have weaker, broader signals
        elif 0.2 < abs_amplitude < 0.5 and signal_width > 10:
            confidence = min(0.75, abs_amplitude * 1.2)
            return AnomalyType.ORGANIC, confidence
        
        # Void/air pockets might have specific reflection patterns
        elif abs_amplitude < 0.2 and len([s for s in surrounding_signals if abs(s) < 0.1]) > len(surrounding_signals) * 0.7:
            confidence = 0.7
            return AnomalyType.VOID, confidence
        
        # Default to unknown with lower confidence
        else:
            confidence = max(0.1, abs_amplitude * 0.5)
            return AnomalyType.UNKNOWN, confidence
    
    def analyze_depth_profile(self, depth_profile: List[float]) -> Dict[str, any]:
        """
        Analyze depth profile to identify layers and transitions.
        
        Args:
            depth_profile: Array of signal amplitudes at different depths
            
        Returns:
            Dictionary with layer analysis
        """
        profile_array = np.array(depth_profile)
        
        # Find major transitions (boundaries between layers)
        gradient = np.gradient(profile_array)
        abs_gradient = np.abs(gradient)
        
        # Identify significant boundaries
        threshold = np.std(abs_gradient) * 1.5  # Adaptive threshold
        boundaries = np.where(abs_gradient > threshold)[0]
        
        # Calculate layer properties
        layers = []
        start_idx = 0
        
        for boundary_idx in boundaries:
            if boundary_idx - start_idx > 5:  # Minimum layer thickness
                layer_data = profile_array[start_idx:boundary_idx]
                layer_properties = {
                    'start_depth': start_idx * self.depth_resolution,
                    'end_depth': boundary_idx * self.depth_resolution,
                    'mean_amplitude': float(np.mean(layer_data)),
                    'std_amplitude': float(np.std(layer_data)),
                    'thickness': (boundary_idx - start_idx) * self.depth_resolution
                }
                layers.append(layer_properties)
                start_idx = boundary_idx
        
        # Add final layer
        if start_idx < len(profile_array):
            layer_data = profile_array[start_idx:]
            layer_properties = {
                'start_depth': start_idx * self.depth_resolution,
                'end_depth': (len(profile_array) - 1) * self.depth_resolution,
                'mean_amplitude': float(np.mean(layer_data)),
                'std_amplitude': float(np.std(layer_data)),
                'thickness': (len(profile_array) - start_idx) * self.depth_resolution
            }
            layers.append(layer_properties)
        
        return {
            'layers': layers,
            'boundaries': [idx * self.depth_resolution for idx in boundaries.tolist()],
            'total_depth': len(depth_profile) * self.depth_resolution
        }
    
    def detect_anomalies(self, depth_profile: List[float], x_position: float = 0.0, 
                        y_position: float = 0.0) -> List[AnomalyDetectionResult]:
        """
        Main method to detect and classify anomalies in radar data.
        
        Args:
            depth_profile: Array of signal amplitudes at different depths
            x_position: X coordinate of measurement
            y_position: Y coordinate of measurement
            
        Returns:
            List of detected anomalies with classifications
        """
        if not depth_profile:
            return []
        
        # Preprocess the signal
        processed_signal = self.preprocess_signal(depth_profile)
        
        # Detect reflections
        reflections = self.detect_reflections(processed_signal)
        
        anomalies = []
        
        for idx, amplitude in reflections:
            # Estimate signal width (simplified)
            signal_width = self.estimate_signal_width(processed_signal, idx)
            
            # Get depth
            depth = idx * self.depth_resolution
            
            # Get surrounding signals for context
            start_idx = max(0, idx - 10)
            end_idx = min(len(processed_signal), idx + 10)
            surrounding_signals = processed_signal[start_idx:end_idx].tolist()
            
            # Classify the anomaly
            anomaly_type, confidence = self.classify_anomaly(
                amplitude, signal_width, depth, surrounding_signals
            )
            
            # Create anomaly result
            anomaly_result = AnomalyDetectionResult(
                x=x_position,
                y=y_position,
                type=anomaly_type,
                confidence=confidence,
                amplitude=amplitude,
                depth=depth
            )
            
            anomalies.append(anomaly_result)
        
        return anomalies
    
    def estimate_signal_width(self, signal: np.ndarray, peak_idx: int, threshold_factor: float = 0.5) -> int:
        """
        Estimate the width of a signal peak at a given threshold.
        
        Args:
            signal: Signal array
            peak_idx: Index of the peak
            threshold_factor: Factor to determine width threshold (relative to peak amplitude)
            
        Returns:
            Estimated width in samples
        """
        peak_value = signal[peak_idx]
        threshold = abs(peak_value) * threshold_factor
        
        # Find left edge
        left_edge = peak_idx
        while left_edge > 0 and abs(signal[left_edge]) > threshold:
            left_edge -= 1
        
        # Find right edge
        right_edge = peak_idx
        while right_edge < len(signal) - 1 and abs(signal[right_edge]) > threshold:
            right_edge += 1
        
        return right_edge - left_edge
    
    def process_radar_scan(self, radar_data: Dict) -> Dict[str, any]:
        """
        Process a complete radar scan with multiple depth profiles.
        
        Args:
            radar_data: Dictionary containing radar scan data
                - 'depth_profiles': List of depth profiles
                - 'coordinates': List of (x, y) coordinates for each profile
                - 'metadata': Additional metadata about the scan
                
        Returns:
            Processed radar scan results
        """
        depth_profiles = radar_data.get('depth_profile', [])
        coordinates = radar_data.get('coordinates', [])
        
        # If no coordinates provided, assume a simple linear scan
        if not coordinates:
            coordinates = [(i * 0.1, 0) for i in range(len(depth_profiles))]
        
        all_anomalies = []
        layer_analysis = []
        
        # Process each depth profile
        for i, profile in enumerate(depth_profiles):
            if i < len(coordinates):
                x, y = coordinates[i]
            else:
                x, y = i * 0.1, 0  # Default spacing if coordinates not provided
            
            # Detect anomalies in this profile
            profile_anomalies = self.detect_anomalies(profile, x, y)
            all_anomalies.extend(profile_anomalies)
            
            # Analyze layer structure
            layer_info = self.analyze_depth_profile(profile)
            layer_info['position'] = {'x': x, 'y': y}
            layer_analysis.append(layer_info)
        
        # Sort anomalies by confidence (highest first)
        all_anomalies.sort(key=lambda a: a.confidence, reverse=True)
        
        return {
            'anomalies': [
                {
                    'x': anomaly.x,
                    'y': anomaly.y,
                    'type': anomaly.type.value,
                    'confidence': anomaly.confidence,
                    'amplitude': anomaly.amplitude,
                    'depth': anomaly.depth
                } for anomaly in all_anomalies
            ],
            'layer_analysis': layer_analysis,
            'total_anomalies_detected': len(all_anomalies),
            'scan_area': {
                'min_x': min([a.x for a in all_anomalies]) if all_anomalies else 0,
                'max_x': max([a.x for a in all_anomalies]) if all_anomalies else 0,
                'min_y': min([a.y for a in all_anomalies]) if all_anomalies else 0,
                'max_y': max([a.y for a in all_anomalies]) if all_anomalies else 0
            }
        }

# Global radar processor instance
radar_processor = RadarProcessor()

def process_radar_data(depth_profile: List[float], coordinates: Optional[Tuple[float, float]] = None) -> Dict[str, any]:
    """
    Process radar data and detect anomalies.
    
    Args:
        depth_profile: Array of signal amplitudes at different depths
        coordinates: Optional (x, y) coordinates of the measurement
        
    Returns:
        Dictionary with processed results
    """
    x, y = coordinates if coordinates else (0.0, 0.0)
    anomalies = radar_processor.detect_anomalies(depth_profile, x, y)
    
    return {
        'anomalies': [
            {
                'x': anomaly.x,
                'y': anomaly.y,
                'type': anomaly.type.value,
                'confidence': anomaly.confidence,
                'amplitude': anomaly.amplitude,
                'depth': anomaly.depth
            } for anomaly in anomalies
        ],
        'total_detected': len(anomalies)
    }

def analyze_depth_layers(depth_profile: List[float]) -> Dict[str, any]:
    """
    Analyze depth profile to identify geological layers.
    
    Args:
        depth_profile: Array of signal amplitudes at different depths
        
    Returns:
        Dictionary with layer analysis
    """
    return radar_processor.analyze_depth_profile(depth_profile)