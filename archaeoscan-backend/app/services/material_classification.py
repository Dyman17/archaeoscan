import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class MaterialClassifier:
    """
    AI service for classifying archaeological materials based on spectrometer readings
    and environmental context.
    """
    
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.classes = ['metal', 'ceramic', 'organic', 'stone', 'unknown']
        
        # Predefined reference spectra for different materials
        self.reference_signatures = {
            'metal': {
                'fe_peak': (290, 310),  # Iron absorption peak
                'cu_peak': (650, 670),  # Copper absorption peak
                'overall_shape': 'sharp_peaks'
            },
            'ceramic': {
                'si_peak': (900, 1000),  # Silica peak
                'al_peak': (450, 470),   # Aluminum peak
                'overall_shape': 'broad_peaks'
            },
            'organic': {
                'ch_peak': (1600, 1700), # Carbon-hydrogen bonds
                'oh_peak': (3200, 3600), # Hydroxyl groups
                'overall_shape': 'complex_pattern'
            },
            'stone': {
                'ca_co3': (1400, 1500),  # Calcium carbonate
                'si_o': (1000, 1200),    # Silicon-oxygen bonds
                'overall_shape': 'mineral_specific'
            }
        }
        
    def preprocess_spectrum(self, wavelengths: List[float], intensities: List[float]) -> np.ndarray:
        """
        Preprocess spectrometer data for classification.
        
        Args:
            wavelengths: List of wavelength values
            intensities: List of corresponding intensity values
            
        Returns:
            Normalized feature vector ready for classification
        """
        # Convert to numpy arrays
        wavelengths = np.array(wavelengths)
        intensities = np.array(intensities)
        
        # Normalize intensities to 0-1 range
        if intensities.max() != intensities.min():
            intensities = (intensities - intensities.min()) / (intensities.max() - intensities.min())
        else:
            intensities = np.zeros_like(intensities)
        
        # Extract key features from spectrum
        features = []
        
        # Statistical features
        features.append(np.mean(intensities))  # Average intensity
        features.append(np.std(intensities))   # Intensity variation
        features.append(np.max(intensities))   # Peak intensity
        features.append(np.min(intensities))   # Minimum intensity
        features.append(np.median(intensities)) # Median intensity
        
        # Peak detection features (simplified)
        peaks = self.find_peaks(intensities)
        features.append(len(peaks))  # Number of peaks
        features.append(np.mean(peaks) if peaks else 0)  # Average peak position
        features.append(np.std(peaks) if peaks else 0)   # Peak distribution
        
        # Spectral slope
        if len(wavelengths) > 1:
            slope = (intensities[-1] - intensities[0]) / (wavelengths[-1] - wavelengths[0])
            features.append(slope)
        else:
            features.append(0)
        
        # Material-specific features
        material_features = self.extract_material_features(wavelengths, intensities)
        features.extend(material_features)
        
        return np.array(features).reshape(1, -1)
    
    def find_peaks(self, intensities: np.ndarray, threshold: float = 0.3) -> List[int]:
        """
        Find peaks in the spectrum above a certain threshold.
        
        Args:
            intensities: Normalized intensity values
            threshold: Minimum intensity to consider as a peak
            
        Returns:
            List of peak positions
        """
        peaks = []
        for i in range(1, len(intensities) - 1):
            if intensities[i] > intensities[i-1] and intensities[i] > intensities[i+1] and intensities[i] > threshold:
                peaks.append(i)
        return peaks
    
    def extract_material_features(self, wavelengths: np.ndarray, intensities: np.ndarray) -> List[float]:
        """
        Extract material-specific features based on known absorption/emission peaks.
        
        Args:
            wavelengths: Wavelength values
            intensities: Intensity values
            
        Returns:
            List of material-specific features
        """
        features = []
        
        # Check for characteristic peaks for each material type
        for mat_type, signature in self.reference_signatures.items():
            if 'fe_peak' in signature:
                fe_start, fe_end = signature['fe_peak']
                fe_intensity = self.get_peak_intensity(wavelengths, intensities, fe_start, fe_end)
                features.append(fe_intensity)
            else:
                features.append(0)  # No applicable peak
                
            if 'si_peak' in signature:
                si_start, si_end = signature['si_peak']
                si_intensity = self.get_peak_intensity(wavelengths, intensities, si_start, si_end)
                features.append(si_intensity)
            else:
                features.append(0)
                
            if 'ch_peak' in signature:
                ch_start, ch_end = signature['ch_peak']
                ch_intensity = self.get_peak_intensity(wavelengths, intensities, ch_start, ch_end)
                features.append(ch_intensity)
            else:
                features.append(0)
        
        return features[:9]  # Limit to 9 features to keep consistent shape
    
    def get_peak_intensity(self, wavelengths: np.ndarray, intensities: np.ndarray, start: float, end: float) -> float:
        """
        Get the maximum intensity within a specific wavelength range.
        
        Args:
            wavelengths: Array of wavelength values
            intensities: Array of intensity values
            start: Start wavelength
            end: End wavelength
            
        Returns:
            Maximum intensity in the specified range
        """
        mask = (wavelengths >= start) & (wavelengths <= end)
        if np.any(mask):
            return np.max(intensities[mask])
        else:
            return 0.0
    
    def prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare synthetic training data based on reference signatures.
        In a real implementation, this would use actual measured spectra.
        
        Returns:
            Tuple of (features, labels)
        """
        # This is a simplified approach - in reality, you'd have real training data
        X = []
        y = []
        
        # Generate synthetic examples for each material type
        for material in self.classes[:-1]:  # Exclude 'unknown' for training
            for _ in range(50):  # 50 examples per material
                # Create synthetic spectrum based on reference signature
                wavelengths = np.linspace(400, 1000, 100)  # 100 wavelength points
                intensities = np.random.random(100) * 0.1  # Base noise
                
                # Add characteristic peaks for this material
                if material == 'metal':
                    # Add iron and copper peaks
                    peak_pos_fe = np.random.randint(29, 31)  # scaled to our 100-point range
                    peak_pos_cu = np.random.randint(65, 67)
                    intensities[peak_pos_fe] += 0.8
                    intensities[peak_pos_cu] += 0.6
                elif material == 'ceramic':
                    # Add silica and aluminum peaks
                    peak_pos_si = np.random.randint(90, 100)
                    peak_pos_al = np.random.randint(45, 47)
                    intensities[peak_pos_si] += 0.7
                    intensities[peak_pos_al] += 0.5
                elif material == 'organic':
                    # Add carbon-hydrogen and hydroxyl peaks
                    peak_pos_ch = np.random.randint(60, 70)
                    peak_pos_oh = np.random.randint(90, 95)
                    intensities[peak_pos_ch] += 0.6
                    intensities[peak_pos_oh] += 0.7
                elif material == 'stone':
                    # Add calcium carbonate and silicon-oxygen peaks
                    peak_pos_caco3 = np.random.randint(40, 50)
                    peak_pos_sio = np.random.randint(67, 80)
                    intensities[peak_pos_caco3] += 0.6
                    intensities[peak_pos_sio] += 0.7
                
                # Add some noise and variation
                intensities += np.random.normal(0, 0.05, intensities.shape)
                intensities = np.clip(intensities, 0, 1)  # Keep in 0-1 range
                
                # Preprocess to get features
                features = self.preprocess_spectrum(wavelengths.tolist(), intensities.tolist()).flatten()
                X.append(features)
                y.append(material)
        
        return np.array(X), np.array(y)
    
    def train(self):
        """
        Train the material classifier with synthetic data.
        """
        print("Training material classifier...")
        X, y = self.prepare_training_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train classifier
        self.classifier.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_accuracy = self.classifier.score(X_train_scaled, y_train)
        test_accuracy = self.classifier.score(X_test_scaled, y_test)
        
        print(f"Training completed. Train accuracy: {train_accuracy:.2f}, Test accuracy: {test_accuracy:.2f}")
        self.is_trained = True
    
    def predict_material(self, wavelengths: List[float], intensities: List[float], 
                         environmental_context: Optional[Dict] = None) -> Dict[str, any]:
        """
        Predict material type from spectrometer data.
        
        Args:
            wavelengths: List of wavelength values
            intensities: List of corresponding intensity values
            environmental_context: Additional context like temperature, humidity, etc.
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained:
            self.train()
        
        # Preprocess the spectrum
        features = self.preprocess_spectrum(wavelengths, intensities)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Make prediction
        predicted_class = self.classifier.predict(features_scaled)[0]
        
        # Get prediction probabilities
        probabilities = self.classifier.predict_proba(features_scaled)[0]
        class_probabilities = dict(zip(self.classifier.classes_, probabilities))
        
        # Calculate confidence as the probability of the predicted class
        confidence = class_probabilities.get(predicted_class, 0.0)
        
        # Adjust confidence based on environmental context if provided
        if environmental_context:
            confidence = self.adjust_confidence_with_context(confidence, environmental_context, predicted_class)
        
        # Determine if prediction is reliable
        is_reliable = confidence > 0.6  # Threshold for reliability
        
        return {
            'material_type': predicted_class if is_reliable else 'unknown',
            'confidence': confidence if is_reliable else 0.1,
            'all_probabilities': class_probabilities,
            'is_reliable': is_reliable,
            'spectral_signature': {
                'wavelengths': wavelengths,
                'intensities': intensities
            },
            'environmental_context': environmental_context or {}
        }
    
    def adjust_confidence_with_context(self, base_confidence: float, 
                                     environmental_context: Dict, 
                                     predicted_material: str) -> float:
        """
        Adjust confidence based on environmental context.
        
        Args:
            base_confidence: Initial confidence from spectral analysis
            environmental_context: Environmental factors
            predicted_material: Predicted material type
            
        Returns:
            Adjusted confidence value
        """
        # Adjust confidence based on environmental factors
        adjustments = []
        
        # Temperature effect: extreme temperatures may affect reliability
        if 'temperature' in environmental_context:
            temp = environmental_context['temperature']
            if temp > 50 or temp < -10:  # Extreme temperatures
                adjustments.append(-0.1)
        
        # Humidity effect: Very high humidity may affect measurements
        if 'humidity' in environmental_context:
            humidity = environmental_context['humidity']
            if humidity > 90:
                adjustments.append(-0.05)
        
        # Depth effect: Deep underwater measurements may have different characteristics
        if 'depth' in environmental_context:
            depth = environmental_context['depth']
            if depth > 100:  # Very deep
                adjustments.append(-0.05)
        
        # Apply adjustments
        adjusted_confidence = base_confidence + sum(adjustments)
        return max(0.05, min(1.0, adjusted_confidence))  # Clamp between 0.05 and 1.0

# Global classifier instance
classifier_instance = MaterialClassifier()

def classify_material(wavelengths: List[float], intensities: List[float], 
                     environmental_context: Optional[Dict] = None) -> Dict[str, any]:
    """
    Main function to classify materials from spectrometer data.
    
    Args:
        wavelengths: List of wavelength values
        intensities: List of corresponding intensity values
        environmental_context: Additional context like temperature, humidity, etc.
        
    Returns:
        Dictionary with classification results
    """
    return classifier_instance.predict_material(wavelengths, intensities, environmental_context)

def get_material_properties(material_type: str) -> Dict[str, any]:
    """
    Get known properties of a classified material type.
    
    Args:
        material_type: Type of material ('metal', 'ceramic', 'organic', 'stone', 'unknown')
        
    Returns:
        Dictionary with material properties
    """
    properties = {
        'metal': {
            'density_range': [2.7, 22.6],  # g/cm³
            'conductivity': 'high',
            'corrosion_susceptibility': 'high',
            'typical_age_range': 'ancient to modern',
            'preservation_notes': 'May corrode in wet environments'
        },
        'ceramic': {
            'density_range': [2.0, 3.0],  # g/cm³
            'conductivity': 'low',
            'corrosion_susceptibility': 'low',
            'typical_age_range': 'ancient to modern',
            'preservation_notes': 'Generally stable but may crack'
        },
        'organic': {
            'density_range': [0.8, 1.5],  # g/cm³
            'conductivity': 'low',
            'corrosion_susceptibility': 'high',
            'typical_age_range': 'ancient to modern',
            'preservation_notes': 'Requires careful preservation'
        },
        'stone': {
            'density_range': [2.0, 3.3],  # g/cm³
            'conductivity': 'low',
            'corrosion_susceptibility': 'medium',
            'typical_age_range': 'ancient to modern',
            'preservation_notes': 'Generally durable but may weather'
        },
        'unknown': {
            'density_range': [None, None],
            'conductivity': 'unknown',
            'corrosion_susceptibility': 'unknown',
            'typical_age_range': 'unknown',
            'preservation_notes': 'Insufficient data for classification'
        }
    }
    
    return properties.get(material_type.lower(), properties['unknown'])