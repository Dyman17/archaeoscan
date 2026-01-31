
import React from 'react';
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
  Table
} from 'lucide-react';

export function Settings() {
  const { settings, updateSettings, connectionStatus } = useApp();
  
  // Load settings from backend on component mount
  React.useEffect(() => {
    const loadSettings = async () => {
      try {
        const response = await fetch('/api/settings/config');
        if (response.ok) {
          const backendSettings = await response.json();
          // Update local settings with backend values
          updateSettings(backendSettings);
        }
      } catch (error) {
        console.error('Failed to load settings from backend:', error);
      }
    };
    
    loadSettings();
  }, [updateSettings]);

  const handleSave = async () => {
    try {
      const response = await fetch('/api/settings/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          websocketUrl: settings.websocketUrl,
          esp32Ip: settings.esp32Ip,
          units: settings.units
        })
      });
      
      if (response.ok) {
        console.log('Settings saved successfully');
        // Show success message
        alert('Settings saved successfully!');
      } else {
        console.error('Failed to save settings');
        alert('Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error saving settings');
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
          <h2 className="font-semibold text-lg">Connection</h2>
        </div>

        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="websocket-url">WebSocket Server URL</Label>
              <Input
                id="websocket-url"
                value={settings.websocketUrl}
                onChange={(e) => updateSettings({ websocketUrl: e.target.value })}
                placeholder="ws://localhost:8080"
                className="font-mono"
              />
              <p className="text-xs text-muted-foreground">
                Backend WebSocket endpoint for real-time data
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="esp32-ip">ESP32-CAM IP Address</Label>
              <Input
                id="esp32-ip"
                value={settings.esp32Ip}
                onChange={(e) => updateSettings({ esp32Ip: e.target.value })}
                placeholder="192.168.1.100"
                className="font-mono"
              />
              <p className="text-xs text-muted-foreground">
                IP address of your ESP32-CAM device
              </p>
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
