import React, { memo } from 'react';
import { cn } from '@/lib/utils';

interface PreservationGaugeProps {
  value: number; // 0-100
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const sizeConfig = {
  sm: { outer: 60, stroke: 4, fontSize: 'text-sm' },
  md: { outer: 80, stroke: 6, fontSize: 'text-lg' },
  lg: { outer: 120, stroke: 8, fontSize: 'text-2xl' },
};

export const PreservationGauge = memo(function PreservationGauge({
  value,
  size = 'md',
  showLabel = true,
  className,
}: PreservationGaugeProps) {
  const config = sizeConfig[size];
  const radius = (config.outer - config.stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = ((100 - Math.min(100, Math.max(0, value))) / 100) * circumference;

  const getColor = (val: number) => {
    if (val >= 80) return 'hsl(var(--status-ok))';
    if (val >= 50) return 'hsl(var(--status-warning))';
    return 'hsl(var(--status-error))';
  };

  const color = getColor(value);

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg
        width={config.outer}
        height={config.outer}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={config.outer / 2}
          cy={config.outer / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={config.stroke}
        />
        {/* Progress circle */}
        <circle
          cx={config.outer / 2}
          cy={config.outer / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={config.stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={progress}
          className="transition-all duration-500 ease-out"
        />
      </svg>
      {showLabel && (
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn('font-mono font-bold', config.fontSize)} style={{ color }}>
            {Math.round(value)}%
          </span>
          {size !== 'sm' && (
            <span className="text-xs text-muted-foreground">Preservation</span>
          )}
        </div>
      )}
    </div>
  );
});
