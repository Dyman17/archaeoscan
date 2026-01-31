import { useState, useEffect, useRef } from 'react';
import { useApp } from '@/context/AppContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Camera,
  Download,
  Circle,
  Square,
  MapPin,
  Layers,
  Wifi,
  WifiOff,
  Eye,
  EyeOff
} from 'lucide-react';

export function CameraStream(): JSX.Element {
  const { settings, sensorData, connectionStatus } = useApp();

  const [isRecording, setIsRecording] = useState(false);
  const [recordedVideoUrl, setRecordedVideoUrl] = useState<string | null>(null);
  const [recordingStartTime, setRecordingStartTime] = useState<number | null>(null);
  const [recordingDuration, setRecordingDuration] = useState<number>(0);
  const [showOverlay, setShowOverlay] = useState(true);
  // const [showGrid, setShowGrid] = useState(false); // TODO: Implement grid toggle functionality
  
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // ESP32 IP address - this should be configurable
  const esp32Ip = settings.esp32Ip || '172.20.10.9'; // Default IP

  // Use sensorData from context instead of direct WebSocket connection
  const isConnected = connectionStatus === 'connected';
  
  // Extract GPS and battery data from sensorData
  const gpsData = sensorData.sensors?.gps;
  const batteryLevel = sensorData.sensors?.battery || 100;
  
  // Extract accelerometer data
  const accelerometerValues = sensorData.sensors?.accelerometer || [0, 0, 0];
  
  // Extract magnetometer data
  const magnetometerValues = sensorData.sensors?.magnetometer || [0, 0, 0];
  
  // Extract spectrometer data
  const spectrometerData = sensorData.spectrometer || {};
  
  // Simulated status based on connection and sensor data
  const espStatus = {
    battery: batteryLevel,
    latitude: gpsData?.lat || 0,
    longitude: gpsData?.lng || 0,
    accuracy: gpsData?.accuracy || 0,
    connected: isConnected,
    signalStrength: 'Strong',
  };

  // Refs
  const recordedChunksRef = useRef<Blob[]>([]);
  
  // Toggle recording
  const toggleRecording = async () => {
    if (isRecording) {
      // Stop recording via backend
      try {
        const response = await fetch('/api/camera/record/stop', { method: 'POST' });
        if (response.ok) {
          const result = await response.json();
          console.log('Recording stopped:', result);
        } else {
          console.error('Failed to stop recording:', response.status);
        }
      } catch (error) {
        console.error('Error stopping recording:', error);
      }
      setIsRecording(false);
    } else {
      // Start recording via backend
      try {
        const response = await fetch('/api/camera/record/start', { method: 'POST' });
        if (response.ok) {
          const result = await response.json();
          console.log('Recording started:', result);
          setIsRecording(true);
        } else {
          console.error('Failed to start recording:', response.status);
        }
      } catch (error) {
        console.error('Error starting recording:', error);
      }
    }
  };
  

  

  
  // Capture snapshot
  const captureSnapshot = async () => {
    try {
      const response = await fetch('/api/camera/snapshot');
      
      if (response.ok) {
        const result = await response.json();
        console.log('Snapshot captured:', result);
        alert(`Snapshot saved: ${result.filename}`);
      } else {
        console.error('Failed to capture snapshot:', response.status);
        alert('Failed to capture snapshot');
      }
    } catch (error) {
      console.error('Error capturing snapshot:', error);
      alert('Error capturing snapshot');
    }
  };
  
  // Save recorded video
  const saveRecordedVideo = async () => {
    try {
      // For recording, we need to start/stop recording via backend
      // The actual video file is managed by the backend
      alert('Video is being saved on the server. Check the recordings folder.');
      console.log('Video saved on server side');
    } catch (error) {
      console.error('Error saving video:', error);
    }
  };
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recordedVideoUrl) {
        URL.revokeObjectURL(recordedVideoUrl);
      }
    };
  }, [recordedVideoUrl]);
  
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Camera Stream</h1>
          <p className="text-muted-foreground">ESP32 camera feed with overlay data</p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant={isRecording ? 'destructive' : 'outline'}
            size="sm"
            onClick={toggleRecording}
          >
            {isRecording ? (
              <>
                <Square className="h-4 w-4 mr-2" />
                Stop Recording
              </>
            ) : (
              <>
                <Circle className="h-4 w-4 mr-2 text-status-error" />
                Record
              </>
            )}
          </Button>
          <Button variant="outline" size="sm" onClick={captureSnapshot}>
            <Camera className="h-4 w-4 mr-2" />
            Snapshot
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setShowOverlay(!showOverlay)}
          >
            {showOverlay ? (
              <>
                <EyeOff className="h-4 w-4 mr-2" />
                Hide Overlay
              </>
            ) : (
              <>
                <Eye className="h-4 w-4 mr-2" />
                Show Overlay
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Video feed */}
        <div className="lg:col-span-3 data-card">

          {/* ESP32-CAM MJPEG Stream */}
          <div className="relative overflow-hidden rounded-lg">
            {/* ESP32-CAM MJPEG Stream */}
            <img 
              id="video-stream"
              src={`http://${esp32Ip}:81/stream`} 
              alt="ESP32-CAM Stream" 
              className="w-full object-contain bg-black"
              style={{ maxHeight: '70vh' }}
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzMzIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiPkxpdmUgQ2FtZXJhIEZlZWQ8L3RleHQ+PC9zdmc+';
              }}
            />
            
            {/* Grid overlay - disabled for now */}
            {/* {showGrid && (
              <div className="absolute inset-0 pointer-events-none">
                <svg width="100%" height="100%" className="opacity-30">
                  <defs>
                    <pattern id="camera-grid" width="33.33%" height="33.33%" patternUnits="userSpaceOnUse">
                      <path d="M 100% 0 L 0 0 0 100%" fill="none" stroke="white" strokeWidth="1" />
                    </pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#camera-grid)" />
                </svg>
              </div>
            )} */}

            {/* Data overlay */}
            {showOverlay && (
              <>
                {/* Top left - GPS */}
                <div className="absolute top-3 left-3 bg-black/60 backdrop-blur-sm px-2 py-1 rounded text-xs text-white font-mono">
                  <div className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    <span>{espStatus.latitude.toFixed(6)}°, {espStatus.longitude.toFixed(6)}°</span>
                  </div>
                </div>

                {/* Top right - Accuracy */}
                <div className="absolute top-3 right-3 bg-black/60 backdrop-blur-sm px-2 py-1 rounded text-xs text-white font-mono">
                  <div className="flex items-center gap-1">
                    <Layers className="h-3 w-3" />
                    <span>±{espStatus.accuracy.toFixed(2)}m</span>
                  </div>
                </div>

                {/* Bottom left - FPS */}
                <div className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-sm px-2 py-1 rounded text-xs text-white font-mono">
                  <span>— FPS</span>
                </div>

                {/* Bottom right - Connection */}
                <div className="absolute bottom-3 right-3 bg-black/60 backdrop-blur-sm px-2 py-1 rounded text-xs text-white">
                  <div className="flex items-center gap-1">
                    {espStatus.connected ? (
                      <Wifi className="h-3 w-3 text-status-ok" />
                    ) : (
                      <WifiOff className="h-3 w-3 text-status-error" />
                    )}
                    <span>{espStatus.connected ? 'Live' : 'No Signal'}</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Right panel - GPS & Status + Controls */}
        <div className="lg:col-span-1 space-y-4">
          {/* GPS & Status Panel */}
          <Card>
            <CardHeader>
              <CardTitle>EspCam Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <span className="text-sm font-medium">Connection</span>
                  <Badge variant={espStatus.connected ? 'default' : 'destructive'}>
                    {espStatus.connected ? 'Connected' : 'Disconnected'}
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <span className="text-sm font-medium">Battery</span>
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          espStatus.battery > 50 ? 'bg-green-500' : 
                          espStatus.battery > 20 ? 'bg-yellow-500' : 'bg-red-500'
                        }`} 
                        style={{ width: `${espStatus.battery}%` }}
                      ></div>
                    </div>
                    <span className="text-sm">{Math.round(espStatus.battery)}%</span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <span className="text-sm font-medium">Signal Strength</span>
                  <Badge variant={espStatus.signalStrength === 'Strong' ? 'default' : 'secondary'}>
                    {espStatus.signalStrength}
                  </Badge>
                </div>

                <div className="p-3 bg-muted rounded-lg">
                  <h4 className="text-sm font-medium mb-2">GPS Coordinates</h4>
                  <div className="text-sm space-y-1">
                    <p><span className="text-muted-foreground">Lat:</span> {espStatus.latitude.toFixed(6)}</p>
                    <p><span className="text-muted-foreground">Lng:</span> {espStatus.longitude.toFixed(6)}</p>
                    <p><span className="text-muted-foreground">Accuracy:</span> ±{espStatus.accuracy.toFixed(2)}m</p>
                  </div>
                </div>

                <div className="p-3 bg-muted rounded-lg">
                  <h4 className="text-sm font-medium mb-2">Sensors Data</h4>
                  <div className="text-sm space-y-1">
                    <p><span className="text-muted-foreground">Accel X:</span> {(accelerometerValues[0] !== undefined ? accelerometerValues[0].toFixed(3) : '—')}</p>
                    <p><span className="text-muted-foreground">Accel Y:</span> {(accelerometerValues[1] !== undefined ? accelerometerValues[1].toFixed(3) : '—')}</p>
                    <p><span className="text-muted-foreground">Accel Z:</span> {(accelerometerValues[2] !== undefined ? accelerometerValues[2].toFixed(3) : '—')}</p>
                    <p className="border-t border-muted my-1 pt-1"><span className="text-muted-foreground">Mag X:</span> {(magnetometerValues[0] !== undefined ? magnetometerValues[0].toFixed(3) : '—')}</p>
                    <p><span className="text-muted-foreground">Mag Y:</span> {(magnetometerValues[1] !== undefined ? magnetometerValues[1].toFixed(3) : '—')}</p>
                    <p><span className="text-muted-foreground">Mag Z:</span> {(magnetometerValues[2] !== undefined ? magnetometerValues[2].toFixed(3) : '—')}</p>
                    <p className="border-t border-muted my-1 pt-1"><span className="text-muted-foreground">Spectrometer:</span> {sensorData.spectrometer?.wavelengths ? `${sensorData.spectrometer.wavelengths.length} pts` : '—'}</p>
                  </div>
                </div>

                <div className="p-3 bg-muted rounded-lg">
                  <h4 className="text-sm font-medium mb-2">Summary</h4>
                  <p className="text-sm">
                    {espStatus.connected 
                      ? `Signal ${espStatus.signalStrength}. Battery at ${Math.round(espStatus.battery)}%. GPS accuracy ±${espStatus.accuracy.toFixed(2)}m.` 
                      : 'ESP32 disconnected. Check network connection.'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Controls panel */}
          <div className="space-y-4">
          </div>

          {/* Recording stats */}
          <div className="data-card">
            <h4 className="font-semibold mb-4">Recording</h4>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Duration</span>
                <span className="font-mono">{recordingDuration > 0 ? `${Math.floor(recordingDuration / 60)}:${String(recordingDuration % 60).padStart(2, '0')}` : '00:00'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Status</span>
                <span className="font-mono">{isRecording ? 'Recording...' : 'Stopped'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Snapshots</span>
                <span className="font-mono">—</span>
              </div>
            </div>
            {recordedVideoUrl && (
              <div className="mt-3 pt-3 border-t border-muted">
                <Button variant="outline" className="w-full" size="sm" onClick={saveRecordedVideo}>
                  <Download className="h-4 w-4 mr-2" />
                  Save Recording
                </Button>
              </div>
            )}
          </div>

        </div>
      </div>

      {/* Summary bar */}
      <div className="data-card">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">Session Summary</h3>
          <span className="text-sm text-muted-foreground">Current session</span>
        </div>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center p-3 rounded-lg bg-muted/30">
            <p className="text-2xl font-mono font-bold">—</p>
            <p className="text-sm text-muted-foreground">Snapshots</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-muted/30">
            <p className="text-2xl font-mono font-bold">—</p>
            <p className="text-sm text-muted-foreground">Recordings</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-muted/30">
            <p className="text-2xl font-mono font-bold">— min</p>
            <p className="text-sm text-muted-foreground">Total Time</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-muted/30">
            <p className="text-2xl font-mono font-bold">— MB</p>
            <p className="text-sm text-muted-foreground">Data Size</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-muted/30">
            <p className="text-2xl font-mono font-bold">— fps</p>
            <p className="text-sm text-muted-foreground">Avg FPS</p>
          </div>
        </div>
      </div>
    </div>
  );
}
