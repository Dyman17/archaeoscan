import React, { memo } from 'react';
import { cn } from '@/lib/utils';
import { Status } from '@/types';
import { StatusIndicator } from './StatusIndicator';
import { Button } from '@/components/ui/button';
import { Settings2, Download } from 'lucide-react';
import { MiniTrendChart } from './MiniTrendChart';

interface SensorRowProps {
  name: string;
  value: string | number;
  unit: string;
  status: Status;
  min?: string | number;
  max?: string | number;
  trendData?: number[];
  onCalibrate?: () => void;
  onExport?: () => void;
  className?: string;
}

export const SensorRow = memo(function SensorRow({
  name,
  value,
  unit,
  status,
  min,
  max,
  trendData,
  onCalibrate,
  onExport,
  className,
}: SensorRowProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-4 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors',
        className
      )}
    >
      {/* Status */}
      <StatusIndicator status={status} size="md" pulse />

      {/* Name */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{name}</p>
        {(min !== undefined || max !== undefined) && (
          <p className="text-xs text-muted-foreground">
            Min: {min ?? '—'} / Max: {max ?? '—'}
          </p>
        )}
      </div>

      {/* Mini trend */}
      {trendData && trendData.length > 0 && (
        <div className="w-20 h-8 hidden sm:block">
          <MiniTrendChart data={trendData} height={32} />
        </div>
      )}

      {/* Value */}
      <div className="text-right">
        <span className="font-mono text-lg font-semibold">{value}</span>
        <span className="font-mono text-sm text-muted-foreground ml-1">{unit}</span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1">
        {onCalibrate && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={onCalibrate}
          >
            <Settings2 className="h-4 w-4" />
          </Button>
        )}
        {onExport && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={onExport}
          >
            <Download className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
});
