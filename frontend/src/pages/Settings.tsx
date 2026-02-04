
import React, { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Settings as SettingsIcon,
  Wifi,
  Download,
  Upload,
  RotateCcw,
  Save,
  AlertTriangle,
  FileText,
  Table,
  Activity,
  CheckCircle
} from 'lucide-react';

export function Settings() {
  const { settings, updateSettings, connectionStatus } = useApp();
  const [config, setConfig] = useState({
    esp_camera_ip: '192.168.1.45',
    esp_data_ip: '192.168.1.46',
    server_ws: 'wss://web-production-263d0.up.railway.app/ws',
    esp32Ip: '192.168.1.45'
  });
  const [pingResults, setPingResults] = useState<Record<string, { status: string, latency?: number }>>({});
  const [testing, setTesting] = useState<string | null>(null);
  
  // Load config from backend on component mount
  React.useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await fetch('/api/config');
        if (response.ok) {
          const backendConfig = await response.json();
          setConfig(backendConfig);
          // Update local settings with backend values
          updateSettings({
            websocketUrl: backendConfig.server_ws,
            esp32Ip: backendConfig.esp_camera_ip
          });
        }
      } catch (error) {
        console.error('Failed to load config from backend:', error);
      }
    };
    
    loadConfig();
  }, [updateSettings]);

  const handleSave = async () => {
    try {
      const response = await fetch('/api/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
      });
      
      if (response.ok) {
        console.log('Config saved successfully');
        alert('Configuration saved successfully!');
        // Update local settings
        updateSettings({
          websocketUrl: config.server_ws,
          esp32Ip: config.esp_camera_ip
        });
      } else {
        console.error('Failed to save config');
        alert('Failed to save configuration');
      }
    } catch (error) {
      console.error('Error saving config:', error);
      alert('Error saving configuration');
    }
  };

  const handlePing = async (target: string) => {
    setTesting(target);
    try {
      const response = await fetch(`/api/ping/${target}`);
      if (response.ok) {
        const result = await response.json();
        setPingResults(prev => ({
          ...prev,
          [target]: result
        }));
      } else {
        setPingResults(prev => ({
          ...prev,
          [target]: { status: 'error' }
        }));
      }
    } catch (error) {
      setPingResults(prev => ({
        ...prev,
        [target]: { status: 'error' }
      }));
    } finally {
      setTesting(null);
    }
  };

  const handleExport = async (format: 'json' | 'csv' | 'pdf') => {
    try {
      let response;
      let filename;
      
      switch (format) {
        case 'json':
          // Export current settings as JSON
          const settingsBlob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
          const settingsUrl = URL.createObjectURL(settingsBlob);
          const settingsLink = document.createElement('a');
          settingsLink.href = settingsUrl;
          settingsLink.download = `archaeoscan-settings-${new Date().toISOString().split('T')[0]}.json`;
          settingsLink.click();
          URL.revokeObjectURL(settingsUrl);
          return;
          
        case 'csv':
          response = await fetch('/api/settings/export/csv', {
            method: 'POST',
          });
          filename = `archaeoscan-data-${new Date().toISOString().split('T')[0]}.csv`;
          break;
          
        case 'pdf':
          response = await fetch('/api/settings/export/pdf', {
            method: 'POST',
          });
          filename = `archaeoscan-data-${new Date().toISOString().split('T')[0]}.pdf`;
          break;
          
        default:
          throw new Error('Unsupported export format');
      }
      
      if (response && response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        console.log(`${format.toUpperCase()} export completed successfully`);
      } else {
        console.error(`Failed to export ${format}`);
        alert(`Failed to export ${format.toUpperCase()} file`);
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Error exporting data');
    }
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const importedSettings = JSON.parse(event.target?.result as string);
            updateSettings(importedSettings);
          } catch (err) {
            console.error('Failed to import settings:', err);
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  const handleFactoryReset = async () => {
    if (window.confirm('Are you sure you want to reset all settings to defaults?')) {
      try {
        const response = await fetch('/api/settings/reset', {
          method: 'POST',
        });
        
        if (response.ok) {
          // Reset local settings to match backend defaults
          updateSettings({
            websocketUrl: 'ws://localhost:8000/ws',
            esp32Ip: '192.168.1.100',
            units: 'metric',
          });
          console.log('Settings reset successfully');
          alert('Settings reset to defaults successfully!');
        } else {
          console.error('Failed to reset settings');
          alert('Failed to reset settings');
        }
      } catch (error) {
        console.error('Error resetting settings:', error);
        alert('Error resetting settings');
      }
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-muted-foreground">Configure system preferences</p>
        </div>
        <Button onClick={handleSave}>
          <Save className="h-4 w-4 mr-2" />
          Save Changes
        </Button>
      </div>

      {/* Connection settings */}
      <div className="data-card">
        <div className="flex items-center gap-2 mb-6">
          <Wifi className="h-5 w-5 text-primary" />
          <h2 className="font-semibold text-lg">Connection Configuration</h2>
        </div>

        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="esp-camera-ip">ESP32-CAM IP Address</Label>
              <div className="flex gap-2">
                <Input
                  id="esp-camera-ip"
                  value={config.esp_camera_ip}
                  onChange={(e) => setConfig(prev => ({ ...prev, esp_camera_ip: e.target.value }))}
                  placeholder="192.168.1.45"
                  className="font-mono"
                />
                <Button 
                  variant="outline" 
                  onClick={() => handlePing('esp-camera')}
                  disabled={testing === 'esp-camera'}
                >
                  {testing === 'esp-camera' ? (
                    <RotateCcw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Activity className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                IP address of ESP32 camera module
              </p>
              {pingResults['esp-camera'] && (
                <div className="text-xs">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded ${
                    pingResults['esp-camera'].status === 'ok' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {pingResults['esp-camera'].status === 'ok' ? (
                      <CheckCircle className="h-3 w-3" />
                    ) : (
                      <AlertTriangle className="h-3 w-3" />
                    )}
                    {pingResults['esp-camera'].status === 'ok' 
                      ? `Connected (${pingResults['esp-camera'].latency}ms)` 
                      : 'Connection failed'
                    }
                  </span>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="esp-data-ip">ESP32 Data IP Address</Label>
              <div className="flex gap-2">
                <Input
                  id="esp-data-ip"
                  value={config.esp_data_ip}
                  onChange={(e) => setConfig(prev => ({ ...prev, esp_data_ip: e.target.value }))}
                  placeholder="192.168.1.46"
                  className="font-mono"
                />
                <Button 
                  variant="outline" 
                  onClick={() => handlePing('esp-data')}
                  disabled={testing === 'esp-data'}
                >
                  {testing === 'esp-data' ? (
                    <RotateCcw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Activity className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                IP address of ESP32 sensor data module
              </p>
              {pingResults['esp-data'] && (
                <div className="text-xs">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded ${
                    pingResults['esp-data'].status === 'ok' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {pingResults['esp-data'].status === 'ok' ? (
                      <CheckCircle className="h-3 w-3" />
                    ) : (
                      <AlertTriangle className="h-3 w-3" />
                    )}
                    {pingResults['esp-data'].status === 'ok' 
                      ? `Connected (${pingResults['esp-data'].latency}ms)` 
                      : 'Connection failed'
                    }
                  </span>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="server-ws">WebSocket Server URL</Label>
              <div className="flex gap-2">
                <Input
                  id="server-ws"
                  value={config.server_ws}
                  onChange={(e) => setConfig(prev => ({ ...prev, server_ws: e.target.value }))}
                  placeholder="wss://your-server.railway.app/ws"
                  className="font-mono"
                />
                <Button 
                  variant="outline" 
                  onClick={() => handlePing('server')}
                  disabled={testing === 'server'}
                >
                  {testing === 'server' ? (
                    <RotateCcw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Activity className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Backend WebSocket endpoint for real-time data
              </p>
              {pingResults['server'] && (
                <div className="text-xs">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded ${
                    pingResults['server'].status === 'ok' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {pingResults['server'].status === 'ok' ? (
                      <CheckCircle className="h-3 w-3" />
                    ) : (
                      <AlertTriangle className="h-3 w-3" />
                    )}
                    {pingResults['server'].status === 'ok' 
                      ? `Connected (${pingResults['server'].latency}ms)` 
                      : 'Connection failed'
                    }
                  </span>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <Label>Connection Status</Label>
              <div className="flex items-center gap-2 p-3 rounded-lg bg-muted/30">
                <span
                  className={`h-2 w-2 rounded-full ${
                    connectionStatus === 'connected'
                      ? 'bg-status-ok'
                      : connectionStatus === 'connecting'
                      ? 'bg-status-warning animate-pulse'
                      : 'bg-status-error'
                  }`}
                />
                <span className="text-sm capitalize">{connectionStatus}</span>
              </div>
            </div>
          </div>
        </div>
      </div>



      {/* Units settings */}
      <div className="data-card">
        <div className="flex items-center gap-2 mb-6">
          <SettingsIcon className="h-5 w-5 text-primary" />
          <h2 className="font-semibold text-lg">Units</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <Label htmlFor="unit-system">Measurement System</Label>
            <Select
              value={settings.units}
              onValueChange={(value: 'metric' | 'imperial') =>
                updateSettings({ units: value })
              }
            >
              <SelectTrigger id="unit-system">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="metric">Metric (m, °C, kg)</SelectItem>
                <SelectItem value="imperial">Imperial (ft, °F, lb)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Data management */}
      <div className="data-card">
        <div className="flex items-center gap-2 mb-6">
          <Download className="h-5 w-5 text-primary" />
          <h2 className="font-semibold text-lg">Data Management</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Button variant="outline" onClick={() => handleExport('json')}>
            <Download className="h-4 w-4 mr-2" />
            Export Settings
          </Button>
          <Button variant="outline" onClick={() => handleExport('csv')}>
            <Table className="h-4 w-4 mr-2" />
            Export Data (CSV)
          </Button>
          <Button variant="outline" onClick={() => handleExport('pdf')}>
            <FileText className="h-4 w-4 mr-2" />
            Export Data (PDF)
          </Button>
          <Button variant="outline" onClick={handleImport}>
            <Upload className="h-4 w-4 mr-2" />
            Import Settings
          </Button>
        </div>
        <div className="mt-4">
          <Button 
            variant="outline" 
            onClick={handleFactoryReset} 
            className="text-status-error hover:text-status-error w-full md:w-auto"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Factory Reset
          </Button>
        </div>
      </div>

      {/* System info */}
      <div className="data-card">
        <div className="flex items-center gap-2 mb-6">
          <SettingsIcon className="h-5 w-5 text-primary" />
          <h2 className="font-semibold text-lg">System Information</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Version</p>
            <p className="font-mono font-medium">1.0.0</p>
          </div>
          <div>
            <p className="text-muted-foreground">Build</p>
            <p className="font-mono font-medium">2024.01</p>
          </div>
          <div>
            <p className="text-muted-foreground">Platform</p>
            <p className="font-mono font-medium">Web</p>
          </div>
          <div>
            <p className="text-muted-foreground">Environment</p>
            <p className="font-mono font-medium">Development</p>
          </div>
        </div>
      </div>

      {/* Warning notice */}
      <div className="flex items-start gap-3 p-4 rounded-lg bg-status-warning/10 border border-status-warning/30">
        <AlertTriangle className="h-5 w-5 text-status-warning shrink-0 mt-0.5" />
        <div className="text-sm">
          <p className="font-medium text-status-warning">Configuration Note</p>
          <p className="text-muted-foreground mt-1">
            Changes to connection settings may require reconnecting to the backend server.
            Some settings will take effect after the next data refresh cycle.
          </p>
        </div>
      </div>
    </div>
  );
}
