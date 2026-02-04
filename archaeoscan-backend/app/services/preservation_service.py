from typing import Dict, Any
import time

class PreservationService:
    def __init__(self):
        self.data_buffer = []
    
    def add_sensor_data(self, data: Dict[str, Any]):
        """Add sensor data to buffer for periodic saving"""
        self.data_buffer.append({
            **data,
            "timestamp": time.time()
        })
    
    def get_buffer_size(self) -> int:
        """Get current buffer size"""
        return len(self.data_buffer)
    
    def clear_buffer(self):
        """Clear the data buffer"""
        self.data_buffer.clear()

# Global instance
preservation_service = PreservationService()
