import { useState, useRef, useEffect } from 'react';
import { useApp } from '@/context/AppContext';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  Map,
  Layers,
  MapPin,
  ThermometerSun,
  Mountain,
  ZoomIn,
  ZoomOut,
  Crosshair,
  Download,
  Wifi,
  WifiOff
} from 'lucide-react';

export function MapView() {
  const { connectionStatus, sensorData } = useApp();
  const isConnected = connectionStatus === 'connected';
  
  // Extract GPS and map data from sensor data
  const latitude = sensorData.sensors?.gps?.lat ?? 51.5074;
  const longitude = sensorData.sensors?.gps?.lng ?? -0.1278;
  const altitude = sensorData.sensors?.gps?.altitude ?? 67;
  const accuracy = sensorData.sensors?.gps?.accuracy ?? 2;
  const scaleDistance = sensorData.sensors?.map?.scale ?? 100;

  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showMarkers, setShowMarkers] = useState(true);
  const [showContours, setShowContours] = useState(false);
  const [heatmapOpacity, setHeatmapOpacity] = useState([70]);
  const [markers, setMarkers] = useState<Array<{id: string, lat: number, lng: number, label: string}>>([
    { id: '1', lat: sensorData.sensors?.gps?.lat ?? 51.5074, lng: sensorData.sensors?.gps?.lng ?? -0.1278, label: 'Site A' },
    { id: '2', lat: sensorData.sensors?.gps?.lat ? (sensorData.sensors.gps.lat + 0.005) : 51.5124, lng: sensorData.sensors?.gps?.lng ? (sensorData.sensors.gps.lng - 0.01) : -0.1378, label: 'Site B' },
  ]);
  
  const mapRef = useRef<HTMLDivElement>(null);
  
  // Update markers when GPS data changes
  useEffect(() => {
    if (sensorData.sensors?.gps?.lat != null && sensorData.sensors?.gps?.lng != null) {
      setMarkers([
        { id: '1', lat: sensorData.sensors.gps.lat, lng: sensorData.sensors.gps.lng, label: 'Current Location' },
        { id: '2', lat: sensorData.sensors.gps.lat + 0.005, lng: sensorData.sensors.gps.lng - 0.01, label: 'Survey Point' },
      ]);
    }
  }, [sensorData]);

  // Add a new marker
  const addMarker = () => {
    // Use current GPS position if available, otherwise use last marker position + offset
    const baseLat = sensorData.sensors?.gps?.lat ?? markers[markers.length - 1]?.lat ?? 51.5074;
    const baseLng = sensorData.sensors?.gps?.lng ?? markers[markers.length - 1]?.lng ?? -0.1278;
    
    const newMarker = {
      id: `marker-${Date.now()}`,
      lat: baseLat + (Math.random() - 0.5) * 0.001,  // Smaller offset for more realistic GPS precision
      lng: baseLng + (Math.random() - 0.5) * 0.001,
      label: `Site ${markers.length + 1}`
    };
    setMarkers([...markers, newMarker]);
  };
  
  // Center map on GPS position
  const centerOnGpsPosition = () => {
    // In a real implementation, this would get actual GPS coordinates and center the map
    console.log('Centering map on GPS position');
  };
  
  // Export map as image
  const exportMapImage = async () => {
    if (mapRef.current) {
      try {
        // In a real implementation, you would capture the actual map
        // For now, we'll simulate the export
        alert('Map exported as image! In a real implementation, this would save the map as a JPEG/PNG file.');
      } catch (error) {
        console.error('Error exporting map:', error);
      }
    }
  };
  
  // Export map as PDF
  const exportMapPdf = async () => {
    try {
      // In a real implementation, you would generate a PDF
      // For now, we'll simulate the export
      alert('Map exported as PDF! In a real implementation, this would save the map as a PDF file.');
    } catch (error) {
      console.error('Error exporting map as PDF:', error);
    }
  };
  
  // Handle export button click
  const handleExport = () => {
    // Show options to export as image or PDF
    if (window.confirm('Export map as image or PDF?\n\nClick OK for Image, Cancel for PDF')) {
      exportMapImage();
    } else {
      exportMapPdf();
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Map</h1>
          <p className="text-muted-foreground">Geospatial survey visualization</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Map display */}
        <div className="lg:col-span-3 data-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Map className="h-5 w-5 text-primary" />
              <span className="font-semibold">Survey Map</span>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon">
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon">
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon">
                <Crosshair className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Map placeholder */}
          <div ref={mapRef} className="aspect-video bg-muted/30 rounded-lg border border-border flex items-center justify-center bg-grid relative overflow-hidden">
            {/* Grid overlay effect */}
            <div className="absolute inset-0 opacity-50">
              <svg width="100%" height="100%">
                <defs>
                  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="hsl(var(--border))" strokeWidth="0.5" />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />
              </svg>
            </div>

            {/* Center crosshair */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-8 h-8 border-2 border-primary rounded-full opacity-50" />
              <div className="absolute w-16 h-[1px] bg-primary/50" />
              <div className="absolute w-[1px] h-16 bg-primary/50" />
            </div>

            {/* Placeholder content */}
            <div className="text-center z-10">
              <Map className="h-12 w-12 mx-auto mb-3 text-muted-foreground opacity-50" />
              <p className="text-muted-foreground font-medium">Map View</p>
              <p className="text-sm text-muted-foreground">
                {isConnected ? 'Loading tiles...' : 'Connect to load map data'}
              </p>
            </div>

            {/* Connection indicator */}
            <div className="absolute bottom-4 left-4 flex items-center gap-2 bg-background/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-border">
              {isConnected ? (
                <Wifi className="h-4 w-4 text-status-ok" />
              ) : (
                <WifiOff className="h-4 w-4 text-status-offline" />
              )}
              <span className="text-xs font-medium">
                {isConnected ? 'Online' : 'Offline mode'}
              </span>
            </div>

            {/* Scale indicator */}
            <div className="absolute bottom-4 right-4 bg-background/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-border">
              <span className="text-xs font-mono">{scaleDistance} m</span>
            </div>
          </div>

          {/* GPS info bar */}
          <div className="mt-4 flex items-center justify-between text-sm p-3 rounded-lg bg-muted/30">
            <div className="flex items-center gap-6">
              <div>
                <span className="text-muted-foreground">Lat: </span>
                <span className="font-mono">{latitude.toFixed(6)}°</span>
              </div>
              <div>
                <span className="text-muted-foreground">Lng: </span>
                <span className="font-mono">{longitude.toFixed(6)}°</span>
              </div>
              <div>
                <span className="text-muted-foreground">Alt: </span>
                <span className="font-mono">{altitude.toFixed(2)} m</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">Accuracy:</span>
              <span className="font-mono">± {accuracy.toFixed(2)} m</span>
            </div>
          </div>
        </div>

        {/* Controls panel */}
        <div className="space-y-4">
          {/* Layers control */}
          <div className="data-card">
            <div className="flex items-center gap-2 mb-4">
              <Layers className="h-5 w-5 text-primary" />
              <span className="font-semibold">Map Layers</span>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <Label htmlFor="markers" className="text-sm">Markers</Label>
                </div>
                <Switch
                  id="markers"
                  checked={showMarkers}
                  onCheckedChange={setShowMarkers}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ThermometerSun className="h-4 w-4 text-muted-foreground" />
                  <Label htmlFor="heatmap" className="text-sm">Heatmap</Label>
                </div>
                <Switch
                  id="heatmap"
                  checked={showHeatmap}
                  onCheckedChange={setShowHeatmap}
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Mountain className="h-4 w-4 text-muted-foreground" />
                  <Label htmlFor="contours" className="text-sm">Depth Contours</Label>
                </div>
                <Switch
                  id="contours"
                  checked={showContours}
                  onCheckedChange={setShowContours}
                />
              </div>
            </div>
          </div>

          {/* Heatmap opacity */}
          {showHeatmap && (
            <div className="data-card">
              <h4 className="font-semibold mb-4">Heatmap Opacity</h4>
              <Slider
                value={heatmapOpacity}
                onValueChange={setHeatmapOpacity}
                min={10}
                max={100}
                step={5}
              />
              <div className="flex items-center justify-between mt-2 text-sm">
                <span className="text-muted-foreground">Opacity</span>
                <span className="font-mono">{heatmapOpacity[0]}%</span>
              </div>
            </div>
          )}

          {/* Survey stats */}
          <div className="data-card">
            <h4 className="font-semibold mb-4">Survey Statistics</h4>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Total markers</span>
                <span className="font-mono font-semibold">{sensorData.sensors?.map?.totalMarkers || markers.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Area covered</span>
                <span className="font-mono font-semibold">{sensorData.sensors?.map?.areaCovered || (markers.length * 250).toFixed(0)} m²</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Track length</span>
                <span className="font-mono font-semibold">{sensorData.sensors?.map?.trackLength || (markers.length * 15).toFixed(0)} m</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Depth range</span>
                <span className="font-mono font-semibold">0.5 — {sensorData.sensors?.map?.depthMax || (markers.length * 0.2 + 0.5).toFixed(1)} m</span>
              </div>
            </div>
          </div>

          {/* Quick actions */}
          <div className="data-card">
            <h4 className="font-semibold mb-4">Quick Actions</h4>
            <div className="space-y-2">
              <Button variant="outline" className="w-full justify-start" size="sm" onClick={addMarker}>
                <MapPin className="h-4 w-4 mr-2" />
                Add GPS Marker
              </Button>
              <Button variant="outline" className="w-full justify-start" size="sm" onClick={centerOnGpsPosition}>
                <Crosshair className="h-4 w-4 mr-2" />
                Center on GPS
              </Button>
              <Button variant="outline" className="w-full justify-start" size="sm" onClick={exportMapImage}>
                <Download className="h-4 w-4 mr-2" />
                Download Tiles
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
