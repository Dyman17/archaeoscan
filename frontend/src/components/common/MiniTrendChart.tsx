import React, { memo, useMemo } from 'react';

interface MiniTrendChartProps {
  data: number[];
  height?: number;
  color?: string;
  showArea?: boolean;
}

export const MiniTrendChart = memo(function MiniTrendChart({
  data,
  height = 48,
  color = 'hsl(var(--primary))',
  showArea = true,
}: MiniTrendChartProps) {
  const { pathD, areaD } = useMemo(() => {
    if (data.length < 2) {
      return { pathD: '', areaD: '' };
    }

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;

    const width = 100;
    const padding = 2;
    const effectiveHeight = height - padding * 2;

    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = padding + effectiveHeight - ((value - min) / range) * effectiveHeight;
      return { x, y };
    });

    const pathD = points
      .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
      .join(' ');

    const areaD = `${pathD} L ${width} ${height} L 0 ${height} Z`;

    return { pathD, areaD };
  }, [data, height]);

  if (data.length < 2) {
    return (
      <div 
        className="flex items-center justify-center text-xs text-muted-foreground"
        style={{ height }}
      >
        No data
      </div>
    );
  }

  return (
    <svg
      viewBox={`0 0 100 ${height}`}
      className="w-full"
      style={{ height }}
      preserveAspectRatio="none"
    >
      {showArea && (
        <path
          d={areaD}
          fill={color}
          fillOpacity={0.1}
        />
      )}
      <path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
});
