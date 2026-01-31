import React from 'react';
import { cn } from '@/lib/utils';
import { Status } from '@/types';

interface StatusIndicatorProps {
  status: Status;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  pulse?: boolean;
}

const statusConfig = {
  ok: {
    label: 'OK',
    bgClass: 'bg-status-ok',
    textClass: 'text-status-ok',
  },
  warning: {
    label: 'Warning',
    bgClass: 'bg-status-warning',
    textClass: 'text-status-warning',
  },
  error: {
    label: 'Error',
    bgClass: 'bg-status-error',
    textClass: 'text-status-error',
  },
  offline: {
    label: 'Offline',
    bgClass: 'bg-status-offline',
    textClass: 'text-status-offline',
  },
};

const sizeConfig = {
  sm: 'h-2 w-2',
  md: 'h-3 w-3',
  lg: 'h-4 w-4',
};

export function StatusIndicator({
  status,
  size = 'md',
  showLabel = false,
  pulse = false,
}: StatusIndicatorProps) {
  const config = statusConfig[status];

  return (
    <div className="flex items-center gap-2">
      <span
        className={cn(
          'rounded-full shrink-0',
          sizeConfig[size],
          config.bgClass,
          pulse && status !== 'offline' && 'animate-pulse-glow'
        )}
      />
      {showLabel && (
        <span className={cn('text-sm font-medium', config.textClass)}>
          {config.label}
        </span>
      )}
    </div>
  );
}
