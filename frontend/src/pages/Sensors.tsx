import { useState, useEffect } from 'react';
import { SensorBlock } from '@/components/common/SensorBlock';
import { SensorRow } from '@/components/common/SensorRow';
import { PreservationGauge } from '@/components/common/PreservationGauge';
import { useApp } from '@/context/AppContext';
import { 
  Magnet, 
  Activity, 
  Waves, 
  Sparkles,
  Thermometer,
  Droplets,
  Ruler
} from 'lucide-react';

export function Sensors() {
  const { connectionStatus, sensorData } = useApp();
  const isConnected = connectionStatus === 'connected';
  
  // Extract sensor values from WebSocket data
  const temperatureValue = sensorData.sensors?.temperature;
  const turbidityValue = sensorData.sensors?.turbidity;
  const tdsValue = sensorData.sensors?.tds;
  const distanceValue = sensorData.sensors?.mapping?.ultrasonic?.value ?? sensorData.sensors?.distance;
  const vibrationValue = sensorData.sensors?.artifact?.piezo?.value ?? sensorData.sensors?.vibration;
  const magnetometerValues = sensorData.sensors?.magnetometer ?? [0, 0, 0];
  const gpsData = sensorData.sensors?.mapping?.gps ?? sensorData.sensors?.gps;
  
  // Initialize preservation data with values from sensorData or defaults
  const [preservationData, setPreservationData] = useState({
    water_preservation: sensorData.sensors?.preservation?.water_preservation || 0,
    materials: sensorData.sensors?.preservation?.materials || {
      wood: 0,           // Дерево
      parchment: 0,      // Бумага/Пергамент
      fabric: 0,         // Ткань
      leather: 0,        // Кожа
      bone: 0,           // Костяные предметы
      lead: 0,           // Свинец
      copper: 0,         // Медь
      brass: 0,          // Латунь
      tin: 0,            // Олово
      zinc: 0,           // Цинк
      iron: 0,           // Железо/Чугун
      steel: 0,          // Сталь
      ceramic: 0,        // Керамика
      clay: 0,           // Глина
      soft_stone: 0,     // Мягкий камень
      hard_stone: 0,     // Твердый камень
      glass: 0,          // Стекло
      plastic: 0,        // Пластик
      rubber: 0,         // Резина
      quartz: 0,         // Кварц
      gold: 0,           // Золото
      silver: 0,         // Серебро
      platinum: 0,       // Платина
      porcelain: 0,      // Фарфор
      marble: 0,         // Мрамор
      bronze: 0,         // Бронза
      asphalt: 0,        // Асфальт/Битум
      ebonite: 0,        // Эбонит
      baked_clay: 0,     // Обожженная глина
      obsidian: 0        // Обсидиан
    },
    final_preservation: sensorData.sensors?.preservation?.final_preservation || 0
  });
  
  // Update preservation data when sensorData changes
  useEffect(() => {
    if (sensorData && sensorData.sensors && sensorData.sensors.preservation) {
      setPreservationData({
        water_preservation: sensorData.sensors.preservation.water_preservation || 0,
        materials: sensorData.sensors.preservation.materials || preservationData.materials,
        final_preservation: sensorData.sensors.preservation.final_preservation || 0
      });
    }
  }, [sensorData]);
  
  const handleCalibrate = (sensor: string) => {
    console.log(`Calibrate: ${sensor}`);
    // Placeholder for calibration action
  };
  
  // Handle export with detailed data
  const handleExport = (sensor: string) => {
    // In a real implementation, this would fetch detailed data from the API
    const detailedData = {
      sensor,
      timestamp: new Date().toISOString(),
      data: {
        water_preservation: preservationData.water_preservation,
        materials: preservationData.materials,
        final_preservation: preservationData.final_preservation,
        raw_values: {
          temperature: 22.5,
          humidity: 45.2,
          pressure: 1013.25,
          tds: 250,
          turbidity: 15.7,
          distance: 12.3,
          magnetometer: { x: 0.12, y: -0.08, z: 0.34 },
          accelerometer: { x: 0.02, y: 0.01, z: 1.01 },
          gps: { lat: 51.5074, lng: -0.1278, accuracy: 2.5 }
        }
      }
    };
    
    // Create a downloadable file
    const dataStr = JSON.stringify(detailedData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${sensor}-detailed-data-${new Date().toISOString().slice(0, 19)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    console.log(`Exported detailed data for ${sensor}`, detailedData);
  };

  // Helper function to calculate preservation for a material
  const calculateMaterialPreservation = (base: number, temp: number, turbidity: number, tds: number, turbidityThreshold: number, tempThreshold: number, tdsThreshold: number): number => {
    let preservation = base;
    
    // Apply turbidity correction
    if (turbidity > turbidityThreshold) {
      preservation -= 10;
    }
    
    // Apply temperature correction
    if (temp > tempThreshold) {
      preservation -= 5;
    }
    
    // Apply TDS correction
    if (tds > tdsThreshold) {
      preservation -= 5;
    }
    
    return Math.max(0, preservation); // Ensure non-negative
  };
  
  // Helper function to calculate water preservation
  const calculateWaterPreservation = (temp: number, turbidity: number, tds: number): number => {
    let preservation = 100;
    
    // Adjust based on factors
    if (turbidity > 50) preservation -= Math.min(30, (turbidity - 50) * 0.5);
    if (temp > 25) preservation -= Math.min(20, (temp - 25) * 1);
    if (tds > 500) preservation -= Math.min(20, (tds - 500) * 0.02);
    
    return Math.max(0, Math.round(preservation));
  };
  
  // Calculate preservation index based on sensor data if not provided by sensors
  useEffect(() => {
    if (sensorData && sensorData.sensors) {
      // Only calculate if preservation data is not already provided by sensors
      if (!sensorData.sensors.preservation) {
        const temp = sensorData.sensors.temperature || 20;
        const turbidity = sensorData.sensors.turbidity || 0;
        const tds = sensorData.sensors.tds || 0;
        
        // Calculate preservation for each material
        const calculatedPreservations = {
          wood: calculateMaterialPreservation(20, temp, turbidity, tds, 50, 25, 500), // Дерево
          parchment: calculateMaterialPreservation(15, temp, turbidity, tds, 50, 25, 500), // Бумага/Пергамент
          fabric: calculateMaterialPreservation(20, temp, turbidity, tds, 50, 25, 500), // Ткань
          leather: calculateMaterialPreservation(25, temp, turbidity, tds, 50, 25, 500), // Кожа
          bone: calculateMaterialPreservation(25, temp, turbidity, tds, 50, 25, 500), // Костяные предметы
          lead: calculateMaterialPreservation(50, temp, turbidity, tds, 80, 30, 1000), // Свинец
          copper: calculateMaterialPreservation(45, temp, turbidity, tds, 80, 30, 1000), // Медь
          brass: calculateMaterialPreservation(45, temp, turbidity, tds, 80, 30, 1000), // Латунь
          tin: calculateMaterialPreservation(40, temp, turbidity, tds, 80, 30, 1000), // Олово
          zinc: calculateMaterialPreservation(35, temp, turbidity, tds, 80, 30, 1000), // Цинк
          iron: calculateMaterialPreservation(30, temp, turbidity, tds, 50, 30, 800), // Железо/Чугун
          steel: calculateMaterialPreservation(40, temp, turbidity, tds, 50, 30, 800), // Сталь
          ceramic: calculateMaterialPreservation(70, temp, turbidity, tds, 100, 25, 500), // Керамика
          clay: calculateMaterialPreservation(60, temp, turbidity, tds, 100, 25, 500), // Глина
          soft_stone: calculateMaterialPreservation(60, temp, turbidity, tds, 100, 25, 500), // Мягкий камень
          hard_stone: calculateMaterialPreservation(90, temp, turbidity, tds, 150, 25, 500), // Твердый камень
          glass: calculateMaterialPreservation(80, temp, turbidity, tds, 100, 25, 500), // Стекло
          plastic: calculateMaterialPreservation(75, temp, turbidity, tds, 150, 25, 500), // Пластик
          rubber: calculateMaterialPreservation(65, temp, turbidity, tds, 150, 25, 500), // Резина
          quartz: calculateMaterialPreservation(95, temp, turbidity, tds, 150, 25, 500), // Кварц
          gold: calculateMaterialPreservation(100, temp, turbidity, tds, 150, 25, 500), // Золото
          silver: calculateMaterialPreservation(95, temp, turbidity, tds, 150, 25, 1500), // Серебро
          platinum: calculateMaterialPreservation(100, temp, turbidity, tds, 150, 25, 500), // Платина
          porcelain: calculateMaterialPreservation(90, temp, turbidity, tds, 150, 25, 500), // Фарфор
          marble: calculateMaterialPreservation(85, temp, turbidity, tds, 150, 25, 500), // Мрамор
          bronze: calculateMaterialPreservation(75, temp, turbidity, tds, 80, 30, 1000), // Бронза
          asphalt: calculateMaterialPreservation(65, temp, turbidity, tds, 80, 30, 1000), // Асфальт/Битум
          ebonite: calculateMaterialPreservation(65, temp, turbidity, tds, 80, 30, 1000), // Эбонит
          baked_clay: calculateMaterialPreservation(80, temp, turbidity, tds, 150, 25, 500), // Обожженная глина
          obsidian: calculateMaterialPreservation(95, temp, turbidity, tds, 150, 25, 500) // Обсидиан
        };
        
        // Calculate average preservation
        const avgPreservation = Math.round(Object.values(calculatedPreservations).reduce((sum, val) => sum + val, 0) / Object.keys(calculatedPreservations).length);
        
        setPreservationData(prev => ({
          water_preservation: calculateWaterPreservation(temp, turbidity, tds),
          materials: calculatedPreservations,
          final_preservation: avgPreservation
        }));
      }
    }
  }, [sensorData]);
  
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Sensors</h1>
          <p className="text-muted-foreground">Live sensor readings and status</p>
        </div>
        {!isConnected && (
          <div className="flex items-center gap-2 text-sm text-status-warning bg-status-warning/10 px-3 py-1.5 rounded-md">
            <span className="h-2 w-2 rounded-full bg-status-warning animate-pulse" />
            Awaiting connection
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Artifact Detection Block */}
        <SensorBlock
          title="Artifact Detection"
          icon={<Sparkles className="h-5 w-5" />}
          summary="Magnetometer, Accelerometer, Piezo, Spectrometer"
        >
          <SensorRow
            name="TLV493D Magnetometer"
            value={isConnected ? `${magnetometerValues[0]}, ${magnetometerValues[1]}, ${magnetometerValues[2]}` : '—'}
            unit="µT"
            status={isConnected ? 'ok' : 'offline'}
            min="—"
            max="—"
            trendData={[]}
            onCalibrate={() => handleCalibrate('magnetometer')}
            onExport={() => handleExport('magnetometer')}
          />
          <SensorRow
            name="MPU-9250 Accelerometer X"
            value={isConnected ? sensorData.sensors?.accelerometer?.[0] || '—' : '—'}
            unit="g"
            status={isConnected ? 'ok' : 'offline'}
            min="—"
            max="—"
            trendData={[]}
            onCalibrate={() => handleCalibrate('accel-x')}
            onExport={() => handleExport('accel-x')}
          />
          <SensorRow
            name="MPU-9250 Accelerometer Y"
            value={isConnected ? sensorData.sensors?.accelerometer?.[1] || '—' : '—'}
            unit="g"
            status={isConnected ? 'ok' : 'offline'}
            min="—"
            max="—"
            trendData={[]}
            onCalibrate={() => handleCalibrate('accel-y')}
            onExport={() => handleExport('accel-y')}
          />
          <SensorRow
            name="MPU-9250 Accelerometer Z"
            value={isConnected ? sensorData.sensors?.accelerometer?.[2] || '—' : '—'}
            unit="g"
            status={isConnected ? 'ok' : 'offline'}
            min="—"
            max="—"
            trendData={[]}
            onCalibrate={() => handleCalibrate('accel-z')}
            onExport={() => handleExport('accel-z')}
          />
          <SensorRow
            name="Piezo Vibration"
            value={isConnected ? vibrationValue : '—'}
            unit="Hz"
            status={isConnected ? 'ok' : 'offline'}
            min="—"
            max="—"
            trendData={[]}
            onCalibrate={() => handleCalibrate('piezo')}
            onExport={() => handleExport('piezo')}
          />
          <SensorRow
            name="AS7343 Spectrometer"
            value={isConnected ? sensorData.sensors?.spectrometer || '—' : '—'}
            unit="nm"
            status={isConnected ? 'ok' : 'offline'}
            min="—"
            max="—"
            trendData={[]}
            onCalibrate={() => handleCalibrate('spectrometer')}
            onExport={() => handleExport('spectrometer')}
          />

          {/* Summary */}
          <div className="mt-4 p-3 rounded-lg bg-muted/30 border border-border/50">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Detection Status</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {isConnected ? 'Monitoring active' : 'Waiting for sensor data...'}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Magnet className="h-4 w-4 text-muted-foreground" />
                <Activity className="h-4 w-4 text-muted-foreground" />
                <Waves className="h-4 w-4 text-muted-foreground" />
              </div>
            </div>
          </div>
        </SensorBlock>

        {/* Environment & Preservation Block */}
        <SensorBlock
          title="Environment & Preservation"
          icon={<Thermometer className="h-5 w-5" />}
          summary="Temperature, Turbidity, TDS"
        >
          <SensorRow
            name="TS-300B Turbidity"
            value={isConnected ? turbidityValue : '—'}
            unit="NTU"
            status={isConnected ? 'ok' : 'offline'}
            min="—"
            max="—"
            trendData={[]}
            onCalibrate={() => handleCalibrate('turbidity')}
            onExport={() => handleExport('turbidity')}
          />
          <SensorRow
            name="DS18B20 Temperature"
            value={isConnected ? temperatureValue : '—'}
            unit="°C"
            status={isConnected ? 'ok' : 'offline'}
            min="—"
            max="—"
            trendData={[]}
            onCalibrate={() => handleCalibrate('temperature')}
            onExport={() => handleExport('temperature')}
          />
          <SensorRow
            name="TDS Meter"
            value={isConnected ? tdsValue : '—'}
            unit="ppm"
            status={isConnected ? 'ok' : 'offline'}
            min="—"
            max="—"
            trendData={[]}
            onCalibrate={() => handleCalibrate('tds')}
            onExport={() => handleExport('tds')}
          />

          {/* Preservation summary with gauge */}
          <div className="mt-4 p-4 rounded-lg bg-muted/30 border border-border/50">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium mb-2">Preservation Index</p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Thermometer className="h-3 w-3" />
                  <span>Water: {preservationData.water_preservation}%</span>
                  <Droplets className="h-3 w-3 ml-2" />
                  <span>Final: {preservationData.final_preservation}%</span>
                </div>
              </div>
              <PreservationGauge value={isConnected ? preservationData.final_preservation : 0} size="md" />
            </div>
            
            {/* Detailed preservation breakdown */}
            <div className="mt-3 text-xs">
              <p className="font-medium mb-1">Material Preservation:</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(preservationData.materials).map(([material, value]) => (
                  <div key={material} className="flex items-center gap-1">
                    <span className="text-muted-foreground capitalize">{material}:</span>
                    <span className="font-mono">{typeof value === 'number' ? value : 0}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </SensorBlock>

        {/* Mapping Block */}
        <SensorBlock
          title="Mapping & Distance"
          icon={<Ruler className="h-5 w-5" />}
          summary="Ultrasonic ranging, GPS integration"
          className="xl:col-span-2"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <SensorRow
                name="HC-SR04T Ultrasonic"
                value={isConnected ? distanceValue : '—'}
                unit="cm"
                status={isConnected ? 'ok' : 'offline'}
                min="—"
                max="—"
                trendData={[]}
                onCalibrate={() => handleCalibrate('ultrasonic')}
                onExport={() => handleExport('ultrasonic')}
              />
            </div>

            <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
              <h4 className="text-sm font-medium mb-3">GPS Position</h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-xs text-muted-foreground">Latitude</p>
                  <p className="font-mono">{gpsData ? `${gpsData.lat}°` : '—°'}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Longitude</p>
                  <p className="font-mono">{gpsData ? `${gpsData.lng}°` : '—°'}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Altitude</p>
                  <p className="font-mono">{gpsData ? `${gpsData.alt || '—'} m` : '— m'}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Accuracy</p>
                  <p className="font-mono">± {gpsData ? `${gpsData.accuracy || '—'} m` : '— m'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Mapping summary */}
          <div className="mt-4 p-3 rounded-lg bg-muted/30 border border-border/50">
            <div className="flex items-center justify-between text-sm">
              <div>
                <p className="font-medium">Mapping Status</p>
                <p className="text-xs text-muted-foreground">
                  {isConnected ? 'Ready for survey' : 'Waiting for position fix...'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground">Points recorded</p>
                <p className="font-mono text-lg font-semibold">—</p>
              </div>
            </div>
          </div>
        </SensorBlock>
      </div>
    </div>
  );
}
