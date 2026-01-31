import { PreservationGauge } from '@/components/common/PreservationGauge';
import { PlaceholderCard } from '@/components/common/PlaceholderCard';
import { useApp } from '@/context/AppContext';
import { 
  Thermometer, 
  Battery, 
  Shield,
  Radio,
  Map,
  Layers
} from 'lucide-react';

export function Dashboard() {
  const { connectionStatus, sensorData } = useApp();
  const isConnected = connectionStatus === 'connected';
  
  // Extract sensor values from WebSocket data
  const temperatureValue = sensorData.sensors?.temperature;
  const turbidityValue = sensorData.sensors?.turbidity;
  const tdsValue = sensorData.sensors?.tds;
  const distanceValue = sensorData.sensors?.mapping?.ultrasonic?.value ?? sensorData.sensors?.distance;
  const magnetometerValues = sensorData.sensors?.magnetometer ?? [0, 0, 0];
  const accelerometerValues = sensorData.sensors?.accelerometer ?? [0, 0, 0];
  const spectrometerValue = sensorData.sensors?.spectrometer;
  const batteryValue = sensorData.sensors?.battery;
  const gpsData = sensorData.sensors?.mapping?.gps ?? sensorData.sensors?.gps;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Real-time system overview</p>
        </div>
        {!isConnected && (
          <div className="flex items-center gap-2 text-sm text-status-warning bg-status-warning/10 px-3 py-1.5 rounded-md">
            <span className="h-2 w-2 rounded-full bg-status-warning animate-pulse" />
            Awaiting connection
          </div>
        )}
      </div>

      {/* Three main sensor groups from Sensors page */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Artifact Detection Summary */}
        <div className="data-card p-4">
          <div className="flex items-center gap-2 mb-3">
            <Radio className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Artifact Detection</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Magnetometer</span>
              <span className="font-mono">{isConnected ? `${magnetometerValues[0]}, ${magnetometerValues[1]}, ${magnetometerValues[2]}` : 'Offline'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Accelerometer</span>
              <span className="font-mono">{isConnected ? `${accelerometerValues[0]}, ${accelerometerValues[1]}, ${accelerometerValues[2]}` : 'Offline'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Spectrometer</span>
              <span className="font-mono">{isConnected ? spectrometerValue : 'Offline'}</span>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-border/50">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Status</span>
              <span className={`text-xs px-2 py-1 rounded-full ${isConnected ? 'bg-status-ok/20 text-status-ok' : 'bg-status-offline/20 text-status-offline'}`}>
                {isConnected ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>
        
        {/* Environment & Preservation Summary */}
        <div className="data-card p-4">
          <div className="flex items-center gap-2 mb-3">
            <Thermometer className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Environment & Preservation</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Temperature</span>
              <span className="font-mono">{isConnected ? `${temperatureValue} °C` : 'Offline'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Turbidity</span>
              <span className="font-mono">{isConnected ? `${turbidityValue} NTU` : 'Offline'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">TDS</span>
              <span className="font-mono">{isConnected ? `${tdsValue} ppm` : 'Offline'}</span>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-border/50">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Preservation</span>
              <span className="font-mono text-lg font-semibold">{isConnected ? `${sensorData.sensors?.preservation ?? '—'}%` : '—'}</span>
            </div>
          </div>
        </div>
        
        {/* Mapping & Distance Summary */}
        <div className="data-card p-4">
          <div className="flex items-center gap-2 mb-3">
            <Map className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Mapping & Distance</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Ultrasonic</span>
              <span className="font-mono">{isConnected ? `${distanceValue} cm` : 'Offline'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">GPS Accuracy</span>
              <span className="font-mono">{isConnected ? `± ${sensorData.sensors?.gps?.accuracy ?? '—'} m` : 'Offline'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Satellites</span>
              <span className="font-mono">{isConnected ? sensorData.sensors?.satellites ?? sensorData.sensors?.mapping?.gps?.satellites ?? '—' : 'Offline'}</span>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-border/50">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Status</span>
              <span className={`text-xs px-2 py-1 rounded-full ${isConnected ? 'bg-status-ok/20 text-status-ok' : 'bg-status-offline/20 text-status-offline'}`}>
                {isConnected ? 'Fixed' : 'No Fix'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* System status row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Battery card */}
        <div className="data-card flex items-center gap-4">
          <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
            <Battery className="h-6 w-6" />
          </div>
          <div className="flex-1">
            <p className="text-sm text-muted-foreground">Battery</p>
            <p className="font-mono text-2xl font-semibold">{batteryValue}%</p>
          </div>
          <div className="text-right text-sm text-muted-foreground">
            <p>Est. runtime</p>
            <p className="font-mono">{batteryValue > 50 ? '2h 30m' : batteryValue > 20 ? '1h 15m' : '30m'}</p>
          </div>
        </div>

        {/* Preservation index */}
        <div className="data-card flex items-center gap-4">
          <PreservationGauge value={sensorData.sensors?.preservation ?? 0} size="md" />
          <div className="flex-1">
            <p className="text-sm text-muted-foreground">Preservation Index</p>
            <p className="text-sm mt-1">
              {isConnected ? (
                `${sensorData.sensors?.preservation?.final_preservation ?? sensorData.sensors?.preservation ?? '0'}% preservation probability`
              ) : (
                <span className="text-status-offline">No data</span>
              )}
            </p>
          </div>
        </div>

        {/* Active sensors */}
        <div className="data-card">
          <div className="flex items-center gap-2 mb-3">
            <Shield className="h-5 w-5 text-primary" />
            <span className="font-medium">Active Sensors</span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <div className="text-center p-2 rounded bg-muted/50">
              <p className="font-mono text-lg font-semibold">{magnetometerValues[0] !== 0 || accelerometerValues[0] !== 0 ? '✓' : '0'}</p>
              <p className="text-xs text-muted-foreground">Artifact</p>
            </div>
            <div className="text-center p-2 rounded bg-muted/50">
              <p className="font-mono text-lg font-semibold">{(temperatureValue != null && temperatureValue !== 0) || (turbidityValue != null && turbidityValue !== 0) || (tdsValue != null && tdsValue !== 0) ? '✓' : '0'}</p>
              <p className="text-xs text-muted-foreground">Environment</p>
            </div>
            <div className="text-center p-2 rounded bg-muted/50">
              <p className="font-mono text-lg font-semibold">{(distanceValue != null && distanceValue !== 0) || (sensorData.sensors?.mapping?.gps?.lat != null && sensorData.sensors?.mapping?.gps?.lng != null) ? '✓' : '0'}</p>
              <p className="text-xs text-muted-foreground">Mapping</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick access panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Recent detections */}
        <div className="data-card lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Radio className="h-5 w-5 text-primary" />
              <h3 className="font-semibold">Recent Detections</h3>
            </div>
            <span className="text-xs text-muted-foreground">Last 24h</span>
          </div>
          {isConnected ? (
            <div className="space-y-2">
              <PlaceholderCard type="empty" message="No detections recorded" />
            </div>
          ) : (
            <PlaceholderCard type="offline" />
          )}
        </div>

        {/* Quick map */}
        <div className="data-card">
          <div className="flex items-center gap-2 mb-4">
            <Map className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Survey Area</h3>
          </div>
          <div className="aspect-square bg-muted/30 rounded-lg flex items-center justify-center border border-border/50 bg-grid">
            <div className="text-center text-muted-foreground">
              <Map className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Map preview</p>
              <p className="text-xs">Connect to view</p>
            </div>
          </div>
        </div>
      </div>

      {/* Material analysis summary */}
      <div className="data-card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Material Analysis Summary</h3>
          </div>
          <span className="text-xs text-muted-foreground">Spectral analysis</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 rounded-lg bg-muted/30">
            <p className="text-2xl font-mono font-bold text-primary">{sensorData.sensors?.materials?.samples ?? sensorData.sensors?.samples ?? '0'}</p>
            <p className="text-sm text-muted-foreground">Samples</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-muted/30">
            <p className="text-2xl font-mono font-bold text-chart-2">{sensorData.sensors?.materials?.identified ?? sensorData.sensors?.identified ?? '0'}</p>
            <p className="text-sm text-muted-foreground">Identified</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-muted/30">
            <p className="text-2xl font-mono font-bold text-chart-3">{sensorData.sensors?.materials?.avgConfidence ?? sensorData.sensors?.avgConfidence ?? '0'}%</p>
            <p className="text-sm text-muted-foreground">Avg Confidence</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-muted/30">
            <p className="text-2xl font-mono font-bold text-chart-4">{sensorData.sensors?.materials?.uniqueTypes ?? sensorData.sensors?.uniqueTypes ?? '0'}</p>
            <p className="text-sm text-muted-foreground">Unique Types</p>
          </div>
        </div>
      </div>
    </div>
  );
}
