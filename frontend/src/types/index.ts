// Status types for sensors and connections
export type Status = 'ok' | 'warning' | 'error' | 'offline';

// Connection status for WebSocket
export type ConnectionStatus = 'connected' | 'connecting' | 'disconnected';

// Sensor reading base interface
export interface SensorReading {
  value: number;
  unit: string;
  timestamp: number;
  status: Status;
  min?: number;
  max?: number;
}

// Environmental sensor data
export interface EnvironmentData {
  temperature: SensorReading;
  humidity: SensorReading;
  pressure: SensorReading;
  tds: SensorReading;
  turbidity: SensorReading;
}

// Artifact detection data
export interface ArtifactData {
  magnetometer: SensorReading;
  accelerometer: {
    x: SensorReading;
    y: SensorReading;
    z: SensorReading;
  };
  piezo: SensorReading;
  spectrometer: SensorReading;
}

// Mapping sensor data
export interface MappingData {
  ultrasonic: SensorReading;
  gps: {
    lat: number;
    lng: number;
    altitude: number;
    accuracy: number;
  };
  scale: number;
  totalMarkers: number;
  areaCovered: string;
  trackLength: string;
  depthMax: string;
}

// System status data
export interface SystemStatus {
  battery: number;
  connection: ConnectionStatus;
  preservationIndex: number;
  lastUpdate: number;
}

// Radar data point
export interface RadarPoint {
  x: number;
  y: number;
  depth: number;
  intensity: number;
  isTarget: boolean;
}

// Material analysis result
export interface MaterialAnalysis {
  type: string;
  confidence: number;
  spectralData: number[];
  referenceMatch: string;
}

// Camera stream info
export interface CameraStream {
  fps: number;
  resolution: string;
  depth: number;
  gps: {
    latitude: number;
    longitude: number;
  };
}

// Settings configuration
export interface AppSettings {
  websocketUrl: string;
  updateFrequency: number;
  theme: 'dark' | 'light';
  units: 'metric' | 'imperial';
  performanceMode: 'balanced' | 'high' | 'powersave';
  esp32Ip?: string;
}

// Alert notification
export interface Alert {
  id: string;
  type: Status;
  message: string;
  timestamp: number;
  acknowledged: boolean;
}

// Navigation item
export interface NavItem {
  id: string;
  label: string;
  icon: string;
  path: string;
}
