from typing import Dict, List, Tuple
import math
from datetime import datetime

def calculate_preservation_index(
    temperature: float,
    tds: float,
    turbidity: float,
    depth: float,
    ph: float = 7.0  # Default neutral pH
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate the environmental preservation index for archaeological objects.
    
    Formula: Weighted combination of environmental factors that affect preservation.
    Output: Percentage (0-100%) representing preservation likelihood.
    
    Args:
        temperature: Water temperature in Celsius
        tds: Total dissolved solids in ppm
        turbidity: Water turbidity in NTU
        depth: Depth in meters
        ph: Water pH level (default 7.0)
    
    Returns:
        Tuple of (preservation_percentage, factor_weights_used)
    """
    
    # Define weights for each factor (based on archaeological research)
    # Negative weights mean higher values decrease preservation
    # Positive weights mean higher values improve preservation
    weights = {
        'temperature': -0.3,    # Lower temps better for preservation
        'tds': -0.25,           # Lower dissolved solids better
        'turbidity': -0.15,     # Clearer water better
        'depth': 0.2,           # Deeper usually means more stable
        'ph': 0.1               # Neutral pH is optimal
    }
    
    # Normalize values to 0-1 scale (0 = worst, 1 = best for preservation)
    # Temperature: ideal range 0-15°C, max damage at >30°C
    temp_score = max(0, min(1, (30 - abs(temperature - 10)) / 20))
    
    # TDS: ideal < 500 ppm, significant damage >2000 ppm
    tds_score = max(0, min(1, (2500 - tds) / 2000))
    
    # Turbidity: ideal < 5 NTU, significant impact >50 NTU
    turbidity_score = max(0, min(1, (100 - turbidity) / 95))
    
    # Depth: deeper is generally better (more stable conditions), up to a point
    depth_score = min(1, (depth + 10) / 50)  # Up to 40m gets full score
    
    # pH: ideal around 7.0, effective range 6.5-8.5
    ph_score = max(0, min(1, (1.5 - abs(ph - 7.0)) / 1.5))
    
    normalized_scores = {
        'temperature': temp_score,
        'tds': tds_score,
        'turbidity': turbidity_score,
        'depth': depth_score,
        'ph': ph_score
    }
    
    # Calculate weighted sum
    weighted_sum = 0
    for factor, weight in weights.items():
        weighted_sum += normalized_scores[factor] * abs(weight)
    
    # Convert to percentage (0-100)
    preservation_percentage = max(0, min(100, weighted_sum * 100))
    
    return preservation_percentage, normalized_scores

def calculate_multi_point_preservation(
    sensor_readings: List[Dict]
) -> Dict[str, any]:
    """
    Calculate preservation index from multiple sensor readings.
    
    Args:
        sensor_readings: List of sensor reading dictionaries
    
    Returns:
        Dictionary with preservation index and contributing factors
    """
    if not sensor_readings:
        return {
            'preservation_percentage': 0,
            'factors': {},
            'readings_used': 0,
            'timestamp_range': None
        }
    
    # Extract relevant sensor values
    temperatures = []
    tds_values = []
    turbidity_values = []
    depths = []
    ph_values = []
    
    timestamps = []
    
    for reading in sensor_readings:
        if 'sensors' in reading:
            sensors = reading['sensors']
            if 'temperature' in sensors:
                temperatures.append(sensors['temperature'])
            if 'tds' in sensors:
                tds_values.append(sensors['tds'])
            if 'turbidity' in sensors:
                turbidity_values.append(sensors['turbidity'])
            if 'distance' in sensors:  # Assuming distance relates to depth
                depths.append(sensors['distance'])
            if 'ph' in sensors:  # If pH sensor is available
                ph_values.append(sensors['ph'])
        
        if 'timestamp' in reading:
            timestamps.append(reading['timestamp'])
    
    # Calculate averages
    avg_temp = sum(temperatures) / len(temperatures) if temperatures else 20.0
    avg_tds = sum(tds_values) / len(tds_values) if tds_values else 500.0
    avg_turbidity = sum(turbidity_values) / len(turbidity_values) if turbidity_values else 10.0
    avg_depth = sum(depths) / len(depths) if depths else 2.0
    avg_ph = sum(ph_values) / len(ph_values) if ph_values else 7.0
    
    # Calculate preservation index
    preservation_pct, factor_scores = calculate_preservation_index(
        avg_temp, avg_tds, avg_turbidity, avg_depth, avg_ph
    )
    
    timestamp_range = {
        'start': min(timestamps) if timestamps else None,
        'end': max(timestamps) if timestamps else None
    } if timestamps else None
    
    return {
        'preservation_percentage': preservation_pct,
        'factors': factor_scores,
        'averages': {
            'temperature': avg_temp,
            'tds': avg_tds,
            'turbidity': avg_turbidity,
            'depth': avg_depth,
            'ph': avg_ph
        },
        'readings_used': len(sensor_readings),
        'timestamp_range': timestamp_range
    }

def get_preservation_recommendations(preservation_percentage: float) -> List[str]:
    """
    Get recommendations based on preservation index.
    
    Args:
        preservation_percentage: Calculated preservation index (0-100)
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    if preservation_percentage >= 80:
        recommendations.append("Excellent preservation conditions detected")
        recommendations.append("Objects likely to maintain structural integrity")
        recommendations.append("Standard monitoring protocols sufficient")
    elif preservation_percentage >= 60:
        recommendations.append("Good preservation conditions")
        recommendations.append("Minor degradation possible over long periods")
        recommendations.append("Regular monitoring recommended")
    elif preservation_percentage >= 40:
        recommendations.append("Moderate preservation risk")
        recommendations.append("Increased degradation rate possible")
        recommendations.append("Enhanced protective measures advised")
        recommendations.append("More frequent condition assessments needed")
    else:
        recommendations.append("Poor preservation conditions detected")
        recommendations.append("Significant degradation risk")
        recommendations.append("Immediate protective interventions required")
        recommendations.append("Consider relocation to controlled environment")
    
    return recommendations