import React from 'react';
import { useApp } from '@/context/AppContext';
import { Menu, Wifi, WifiOff, AlertTriangle, Battery, BatteryCharging, BatteryLow, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';

interface TopBarProps {
  onMenuClick: () => void;
}

export function TopBar({ onMenuClick }: TopBarProps) {
  const { connectionStatus, battery, alerts, currentTime, acknowledgeAlert } = useApp();

  const unacknowledgedAlerts = alerts.filter((a) => !a.acknowledged);
  const criticalAlerts = unacknowledgedAlerts.filter((a) => a.type === 'error');

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Wifi className="h-4 w-4" />;
      case 'connecting':
        return <Wifi className="h-4 w-4 animate-pulse" />;
      default:
        return <WifiOff className="h-4 w-4" />;
    }
  };

  const getConnectionColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'text-status-ok';
      case 'connecting':
        return 'text-status-warning';
      default:
        return 'text-status-error';
    }
  };

  const getBatteryIcon = () => {
    if (battery <= 20) return <BatteryLow className="h-4 w-4" />;
    if (battery >= 95) return <BatteryCharging className="h-4 w-4" />;
    return <Battery className="h-4 w-4" />;
  };

  const getBatteryColor = () => {
    if (battery <= 20) return 'text-status-error';
    if (battery <= 40) return 'text-status-warning';
    return 'text-status-ok';
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  return (
    <header className="h-12 bg-card border-b border-border flex items-center justify-between px-4 shrink-0">
      {/* Left section */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>
        
        <div className="flex items-center gap-2">
          <img 
            src="/logo.png" 
            alt="ArchaeoScan Logo" 
            className="w-8 h-8 rounded-md object-contain"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.onerror = null; // prevents looping
              target.style.display = 'none';
              // Show fallback if image fails to load
              const fallbackDiv = document.createElement('div');
              fallbackDiv.className = 'w-8 h-8 bg-primary rounded-md flex items-center justify-center';
              fallbackDiv.innerHTML = '<span class="text-primary-foreground font-bold text-sm">AS</span>';
              target.parentNode?.replaceChild(fallbackDiv, target);
            }}
          />
          <span className="font-semibold text-lg hidden sm:block">ArchaeoScan</span>
        </div>
      </div>

      {/* Center section - Critical alerts */}
      {criticalAlerts.length > 0 && (
        <div className="hidden md:flex items-center gap-2 bg-status-error/10 border border-status-error/30 rounded-md px-3 py-1">
          <AlertTriangle className="h-4 w-4 text-status-error" />
          <span className="text-sm text-status-error font-medium">
            {criticalAlerts[0].message}
          </span>
        </div>
      )}

      {/* Right section */}
      <div className="flex items-center gap-4">
        {/* Connection status */}
        <div className={cn('flex items-center gap-1.5', getConnectionColor())}>
          {getConnectionIcon()}
          <span className="text-xs font-medium hidden sm:block capitalize">
            {connectionStatus}
          </span>
        </div>

        {/* Battery */}
        <div className={cn('flex items-center gap-1.5', getBatteryColor())}>
          {getBatteryIcon()}
          <span className="text-xs font-mono font-medium">{battery}%</span>
        </div>

        {/* Time */}
        <div className="font-mono text-sm text-muted-foreground hidden sm:block">
          {formatTime(currentTime)}
        </div>

        {/* Alerts */}
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-4 w-4" />
              {unacknowledgedAlerts.length > 0 && (
                <Badge
                  variant="destructive"
                  className="absolute -top-1 -right-1 h-4 w-4 p-0 text-[10px] flex items-center justify-center"
                >
                  {unacknowledgedAlerts.length}
                </Badge>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80" align="end">
            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Alerts</h4>
              {alerts.length === 0 ? (
                <p className="text-sm text-muted-foreground">No alerts</p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {alerts.slice(0, 10).map((alert) => (
                    <div
                      key={alert.id}
                      className={cn(
                        'p-2 rounded-md text-sm border cursor-pointer transition-colors',
                        alert.acknowledged
                          ? 'bg-muted/50 border-border opacity-60'
                          : alert.type === 'error'
                          ? 'bg-status-error/10 border-status-error/30'
                          : alert.type === 'warning'
                          ? 'bg-status-warning/10 border-status-warning/30'
                          : 'bg-muted border-border'
                      )}
                      onClick={() => acknowledgeAlert(alert.id)}
                    >
                      <div className="flex items-start gap-2">
                        <AlertTriangle
                          className={cn(
                            'h-4 w-4 mt-0.5 shrink-0',
                            alert.type === 'error'
                              ? 'text-status-error'
                              : alert.type === 'warning'
                              ? 'text-status-warning'
                              : 'text-muted-foreground'
                          )}
                        />
                        <div>
                          <p>{alert.message}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {new Date(alert.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </PopoverContent>
        </Popover>
      </div>
    </header>
  );
}
