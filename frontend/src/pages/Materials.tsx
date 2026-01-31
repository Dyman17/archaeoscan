import React, { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Layers,
  Sparkles,
  Database,
  Download,
  RefreshCw,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export function Materials() {
  const { connectionStatus, sensorData } = useApp();
  const isConnected = connectionStatus === 'connected';
  
  // Extract material analysis data from sensor data
  const materialType = sensorData.sensors?.materials?.materialType ?? sensorData.sensors?.materialType;
  const confidence = sensorData.sensors?.materials?.confidence ?? sensorData.sensors?.confidence ?? 0;
  const totalReferences = sensorData.sensors?.materials?.totalReferences ?? sensorData.sensors?.totalReferences;
  const metalReferences = sensorData.sensors?.materials?.metalReferences ?? sensorData.sensors?.metalReferences;
  const ceramicReferences = sensorData.sensors?.materials?.ceramicReferences ?? sensorData.sensors?.ceramicReferences;
  const organicReferences = sensorData.sensors?.materials?.organicReferences ?? sensorData.sensors?.organicReferences;
  const mineralReferences = sensorData.sensors?.materials?.mineralReferences ?? sensorData.sensors?.mineralReferences;
  const sampleCount = sensorData.sensors?.materials?.sampleCount ?? sensorData.sensors?.sampleCount;

  const [selectedReference, setSelectedReference] = useState('all');

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Materials</h1>
          <p className="text-muted-foreground">Spectral analysis and material identification</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Analyze
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Spectral plot */}
        <div className="lg:col-span-2 data-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <span className="font-semibold">Spectral Analysis</span>
            </div>
            <Select value={selectedReference} onValueChange={setSelectedReference}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Reference Library" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Materials</SelectItem>
                <SelectItem value="metals">Metals</SelectItem>
                <SelectItem value="ceramics">Ceramics</SelectItem>
                <SelectItem value="organic">Organic</SelectItem>
                <SelectItem value="minerals">Minerals</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Spectral chart placeholder */}
          <div className="aspect-[2/1] bg-muted/30 rounded-lg border border-border flex items-center justify-center relative overflow-hidden">
            {/* Fake axis lines */}
            <div className="absolute left-12 top-4 bottom-12 w-[1px] bg-border" />
            <div className="absolute left-12 right-4 bottom-12 h-[1px] bg-border" />
            
            {/* Axis labels */}
            <div className="absolute left-2 top-1/2 -translate-y-1/2 -rotate-90 text-xs text-muted-foreground">
              Intensity
            </div>
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs text-muted-foreground">
              Wavelength (nm)
            </div>

            {/* Placeholder content */}
            <div className="text-center">
              <Sparkles className="h-12 w-12 mx-auto mb-3 text-muted-foreground opacity-50" />
              <p className="text-muted-foreground font-medium">Spectral Data</p>
              <p className="text-sm text-muted-foreground">
                {isConnected ? 'Awaiting sample...' : 'Connect to analyze'}
              </p>
            </div>
          </div>

          {/* Wavelength bands legend */}
          <div className="mt-4 flex items-center justify-center gap-4 text-xs">
            <div className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-violet-500" />
              <span className="text-muted-foreground">UV</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-blue-500" />
              <span className="text-muted-foreground">Blue</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-green-500" />
              <span className="text-muted-foreground">Green</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-yellow-500" />
              <span className="text-muted-foreground">Yellow</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-red-500" />
              <span className="text-muted-foreground">Red</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-rose-900" />
              <span className="text-muted-foreground">NIR</span>
            </div>
          </div>
        </div>

        {/* Analysis results */}
        <div className="space-y-4">
          {/* Current analysis */}
          <div className="data-card">
            <div className="flex items-center gap-2 mb-4">
              <Layers className="h-5 w-5 text-primary" />
              <span className="font-semibold">Current Analysis</span>
            </div>

            <div className="space-y-4">
              {/* Material type */}
              <div>
                <p className="text-sm text-muted-foreground mb-1">Identified Material</p>
                <p className="text-xl font-semibold">{materialType}</p>
              </div>

              {/* Confidence */}
              <div>
                <p className="text-sm text-muted-foreground mb-2">Confidence</p>
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all duration-500"
                      style={{ width: `${confidence}%` }}
                    />
                  </div>
                  <span className="font-mono text-sm w-12 text-right">{confidence}%</span>
                </div>
              </div>

              {/* Match status */}
              <div className="flex items-center gap-2 p-3 rounded-lg bg-muted/30">
                {materialType !== '—' ? (
                  <CheckCircle2 className="h-4 w-4 text-status-ok" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-muted-foreground" />
                )}
                <span className="text-sm text-muted-foreground">
                  {materialType !== '—' ? `Match found: ${materialType}` : 'No sample analyzed'}
                </span>
              </div>
            </div>
          </div>

          {/* Reference library */}
          <div className="data-card">
            <div className="flex items-center gap-2 mb-4">
              <Database className="h-5 w-5 text-primary" />
              <span className="font-semibold">Reference Library</span>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm p-2 rounded bg-muted/30">
                <span>Total references</span>
                <span className="font-mono font-semibold">{totalReferences}</span>
              </div>
              <div className="flex items-center justify-between text-sm p-2 rounded bg-muted/30">
                <span>Metals</span>
                <span className="font-mono">{metalReferences}</span>
              </div>
              <div className="flex items-center justify-between text-sm p-2 rounded bg-muted/30">
                <span>Ceramics</span>
                <span className="font-mono">{ceramicReferences}</span>
              </div>
              <div className="flex items-center justify-between text-sm p-2 rounded bg-muted/30">
                <span>Organic</span>
                <span className="font-mono">{organicReferences}</span>
              </div>
              <div className="flex items-center justify-between text-sm p-2 rounded bg-muted/30">
                <span>Minerals</span>
                <span className="font-mono">{mineralReferences}</span>
              </div>
            </div>
          </div>

          {/* Recent matches */}
          <div className="data-card">
            <h4 className="font-semibold mb-4">Recent Matches</h4>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>No recent analyses</p>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis history */}
      <div className="data-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Analysis History</h3>
          <Badge variant="secondary">{sampleCount} samples</Badge>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Time</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Material</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Confidence</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Reference</th>
                <th className="text-left py-3 px-4 font-medium text-muted-foreground">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td colSpan={5} className="py-8 text-center text-muted-foreground">
                  No analysis history available
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
