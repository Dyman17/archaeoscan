import React, { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { ConnectionStatus, Alert, AppSettings } from '@/types';
import { useWebSocket } from '@/hooks/useWebSocket';

interface AppContextType {
  // Connection
  connectionStatus: ConnectionStatus;
  setConnectionStatus: (status: ConnectionStatus) => void;
  
  // System
  battery: number;
  setBattery: (level: number) => void;
  
  // Sensor data
  sensorData: Record<string, any>;
  setSensorData: (data: Record<string, any>) => void;
  
  // Alerts
  alerts: Alert[];
  addAlert: (alert: Omit<Alert, 'id' | 'timestamp' | 'acknowledged'>) => void;
  acknowledgeAlert: (id: string) => void;
  clearAlerts: () => void;
  
  // Settings
  settings: AppSettings;
  updateSettings: (updates: Partial<AppSettings>) => void;
  
  // Current time
  currentTime: Date;
}

const defaultSettings: AppSettings = {
  websocketUrl: 'wss://web-production-263d0.up.railway.app/ws',
  updateFrequency: 1000,
  theme: 'dark',
  units: 'metric',
  performanceMode: 'balanced',
  esp32Ip: '172.20.10.9',
};

const AppContext = createContext<AppContextType | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const [battery, setBattery] = useState(100);
  const [sensorData, setSensorData] = useState<Record<string, any>>({});
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [settings, setSettings] = useState<AppSettings>(defaultSettings);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update time every second
  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection
  const { status: wsStatus, connect: connectWebSocket, disconnect: disconnectWebSocket } = useWebSocket({
    url: settings.websocketUrl,
    onConnect: () => {
      setConnectionStatus('connected');
    },
    onDisconnect: () => {                   
      setConnectionStatus('disconnected');
    },
    onMessage: (data) => {
      console.log('Received sensor data:', data);
      // Update sensor data
      if (data && typeof data === 'object') {
        setSensorData(prev => ({
          ...prev,
          ...data
        }));
      }
      // Update battery if present in the message
      if (data && typeof data === 'object' && 'sensors' in data && typeof data.sensors === 'object' && data.sensors && 'battery' in data.sensors) {
        const sensorData = data.sensors as Record<string, any>;
        if (typeof sensorData.battery === 'number') {
          setBattery(sensorData.battery);
        }
      }
    },
  });

  // Connect to WebSocket when component mounts
  useEffect(() => {
    connectWebSocket();
    return () => {
      disconnectWebSocket();
    };
  }, [settings.websocketUrl]);

  // Update connection status when WebSocket status changes
  useEffect(() => {
    setConnectionStatus(wsStatus);
  }, [wsStatus]);

  const addAlert = useCallback((alert: Omit<Alert, 'id' | 'timestamp' | 'acknowledged'>) => {
    const newAlert: Alert = {
      ...alert,
      id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      acknowledged: false,
    };
    setAlerts((prev) => [newAlert, ...prev].slice(0, 50)); // Keep last 50 alerts
  }, []);

  const acknowledgeAlert = useCallback((id: string) => {
    setAlerts((prev) =>
      prev.map((alert) =>
        alert.id === id ? { ...alert, acknowledged: true } : alert
      )
    );
  }, []);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  const updateSettings = useCallback((updates: Partial<AppSettings>) => {
    setSettings((prev) => ({ ...prev, ...updates }));
  }, []);

  return (
    <AppContext.Provider
      value={{
        connectionStatus,
        setConnectionStatus,
        battery,
        setBattery,
        sensorData,
        setSensorData,
        alerts,
        addAlert,
        acknowledgeAlert,
        clearAlerts,
        settings,
        updateSettings,
        currentTime,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return {
    ...context,
    sensorData: context.sensorData,
    setSensorData: context.setSensorData
  };
}
