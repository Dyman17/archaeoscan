import { useRef, useEffect, useState } from 'react';
import { useApp } from '@/context/AppContext';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { 
  Radar as RadarIcon, 
  Layers, 
  ZoomIn, 
  ZoomOut,
  RotateCcw,
  Download
} from 'lucide-react';

export function Radar() {
  const { connectionStatus, sensorData } = useApp();
  const isConnected = connectionStatus === 'connected';
  
  // Extract radar data from sensor data
  const targetsFound = sensorData.sensors?.radar?.targets ?? 0;
  const highConfidence = sensorData.sensors?.radar?.highConfidence ?? 0;
  const mediumConfidence = sensorData.sensors?.radar?.mediumConfidence ?? 0;
  const lowConfidence = sensorData.sensors?.radar?.lowConfidence ?? 0;
  const scanRate = sensorData.sensors?.radar?.scanRate ?? '—';
  const resolution = sensorData.sensors?.radar?.resolution ?? '—';
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [showRawData, setShowRawData] = useState(true);
  const [showFiltered, setShowFiltered] = useState(true);
  const [showTargets, setShowTargets] = useState(true);
  const [depthScale, setDepthScale] = useState([50]);
  const [zoom, setZoom] = useState(1);

  // Draw radar visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const maxRadius = Math.min(width, height) / 2 - 20;

    // Clear canvas
    ctx.fillStyle = 'hsl(220, 20%, 7%)';
    ctx.fillRect(0, 0, width, height);

    // Draw grid circles
    ctx.strokeStyle = 'hsl(220, 15%, 18%)';
    ctx.lineWidth = 1;
    for (let i = 1; i <= 5; i++) {
      const radius = (maxRadius / 5) * i;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Draw grid lines
    for (let i = 0; i < 8; i++) {
      const angle = (Math.PI * 2 * i) / 8;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(
        centerX + Math.cos(angle) * maxRadius,
        centerY + Math.sin(angle) * maxRadius
      );
      ctx.stroke();
    }

    // Draw depth labels
    ctx.fillStyle = 'hsl(215, 15%, 55%)';
    ctx.font = '10px JetBrains Mono';
    for (let i = 1; i <= 5; i++) {
      const depth = (depthScale[0] / 5) * i;
      ctx.fillText(
        `${depth.toFixed(0)}m`,
        centerX + 5,
        centerY - (maxRadius / 5) * i + 12
      );
    }

    // Draw center point
    ctx.fillStyle = 'hsl(173, 80%, 40%)';
    ctx.beginPath();
    ctx.arc(centerX, centerY, 4, 0, Math.PI * 2);
    ctx.fill();

    // Placeholder message
    if (!isConnected) {
      ctx.fillStyle = 'hsl(215, 15%, 55%)';
      ctx.font = '14px Inter';
      ctx.textAlign = 'center';
      ctx.fillText('Waiting for radar data...', centerX, height - 30);
    }
  }, [isConnected, depthScale, zoom, showRawData, showFiltered, showTargets]);

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.25, 3));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.25, 0.5));
  const handleReset = () => {
    setZoom(1);
    setDepthScale([50]);
  };
  
  // Export radar scan functionality
  const exportScan = async () => {
    try {
      // Get the canvas element
      const canvas = canvasRef.current;
      if (!canvas) {
        console.error('Canvas not found');
        return;
      }
      
      // Show options to export as image or PDF
      const exportChoice = window.confirm('Export radar scan as image or PDF?\n\nClick OK for Image, Cancel for PDF');
      
      if (exportChoice) {
        // Export as image (PNG/JPEG)
        const dataUrl = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = `radar-scan-${new Date().toISOString().slice(0, 19)}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('Radar scan exported as PNG');
      } else {
        // For PDF export, we would typically use a library like jsPDF
        // For now, we'll simulate PDF export
        alert('PDF export would be implemented with a library like jsPDF in a real application.');
        
        // In a real implementation, this would combine the radar image with metadata
        console.log('Radar scan PDF export would be generated');
      }
    } catch (error) {
      console.error('Error exporting radar scan:', error);
      alert('Error exporting radar scan. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Radar</h1>
          <p className="text-muted-foreground">Ground-penetrating radar visualization</p>
        </div>
        <Button variant="outline" size="sm" onClick={exportScan}>
          <Download className="h-4 w-4 mr-2" />
          Export Scan
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Radar display */}
        <div className="lg:col-span-3 data-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <RadarIcon className="h-5 w-5 text-primary" />
              <span className="font-semibold">Radar View</span>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon" onClick={handleZoomOut}>
                <ZoomOut className="h-4 w-4" />
              </Button>
              <span className="text-sm font-mono w-12 text-center">{zoom.toFixed(2)}x</span>
              <Button variant="ghost" size="icon" onClick={handleZoomIn}>
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" onClick={handleReset}>
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          <div className="aspect-square bg-background rounded-lg border border-border overflow-hidden">
            <canvas
              ref={canvasRef}
              width={600}
              height={600}
              className="w-full h-full"
              style={{ transform: `scale(${zoom})` }}
            />
          </div>
        </div>

        {/* Controls panel */}
        <div className="space-y-4">
          {/* Layers */}
          <div className="data-card">
            <div className="flex items-center gap-2 mb-4">
              <Layers className="h-5 w-5 text-primary" />
              <span className="font-semibold">Layers</span>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="raw-data" className="text-sm">Raw Data</Label>
                <Switch
                  id="raw-data"
                  checked={showRawData}
                  onCheckedChange={setShowRawData}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="filtered" className="text-sm">Filtered</Label>
                <Switch
                  id="filtered"
                  checked={showFiltered}
                  onCheckedChange={setShowFiltered}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="targets" className="text-sm">Targets</Label>
                <Switch
                  id="targets"
                  checked={showTargets}
                  onCheckedChange={setShowTargets}
                />
              </div>
            </div>
          </div>



          {/* Detection info */}
          <div className="data-card">
            <h4 className="font-semibold mb-4">Detection Summary</h4>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Targets found</span>
                <span className="font-mono font-semibold">{targetsFound}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">High confidence</span>
                <span className="font-mono text-status-ok font-semibold">{highConfidence}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Medium confidence</span>
                <span className="font-mono text-status-warning font-semibold">{mediumConfidence}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Low confidence</span>
                <span className="font-mono text-muted-foreground font-semibold">{lowConfidence}</span>
              </div>
            </div>
          </div>

          {/* Scan status */}
          <div className="data-card">
            <h4 className="font-semibold mb-4">Scan Status</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Status</span>
                <span className={isConnected ? 'text-status-ok' : 'text-status-offline'}>
                  {isConnected ? 'Active' : 'Idle'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Scan rate</span>
                <span className="font-mono">{scanRate} Hz</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Resolution</span>
                <span className="font-mono">{resolution} cm</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
