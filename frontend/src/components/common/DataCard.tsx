import React, { ReactNode, memo } from 'react';
import { cn } from '@/lib/utils';
import { Status } from '@/types';
import { StatusIndicator } from './StatusIndicator';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface DataCardProps {
  title: string;
  value: string | number;
  unit?: string;
  status?: Status;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;
  icon?: ReactNode;
  chart?: ReactNode;
  className?: string;
  onClick?: () => void;
}

export const DataCard = memo(function DataCard({
  title,
  value,
  unit,
  status = 'ok',
  trend,
  trendValue,
  icon,
  chart,
  className,
  onClick,
}: DataCardProps) {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;

  return (
    <div
      className={cn(
        'data-card group',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {icon && (
            <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center text-primary">
              {icon}
            </div>
          )}
          <span className="text-sm font-medium text-muted-foreground">{title}</span>
        </div>
        <StatusIndicator status={status} size="sm" pulse />
      </div>

      {/* Value */}
      <div className="flex items-baseline gap-1 mb-2">
        <span className="sensor-value text-foreground">{value}</span>
        {unit && <span className="sensor-unit">{unit}</span>}
      </div>

      {/* Trend */}
      {trend && (
        <div className={cn(
          'flex items-center gap-1 text-xs',
          trend === 'up' && 'text-status-ok',
          trend === 'down' && 'text-status-error',
          trend === 'stable' && 'text-muted-foreground'
        )}>
          <TrendIcon className="h-3 w-3" />
          {trendValue && <span>{trendValue}</span>}
        </div>
      )}

      {/* Mini chart */}
      {chart && (
        <div className="mt-3 h-12">
          {chart}
        </div>
      )}
    </div>
  );
});
