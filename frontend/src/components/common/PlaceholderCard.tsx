import React from 'react';
import { cn } from '@/lib/utils';
import { WifiOff, AlertCircle } from 'lucide-react';

interface PlaceholderCardProps {
  title?: string;
  message?: string;
  type?: 'offline' | 'error' | 'loading' | 'empty';
  className?: string;
}

export function PlaceholderCard({
  title,
  message,
  type = 'offline',
  className,
}: PlaceholderCardProps) {
  const Icon = type === 'error' ? AlertCircle : WifiOff;

  const defaultMessages = {
    offline: 'Waiting for connection...',
    error: 'Error loading data',
    loading: 'Loading...',
    empty: 'No data available',
  };

  return (
    <div
      className={cn(
        'data-card flex flex-col items-center justify-center py-8 text-center',
        className
      )}
    >
      {type === 'loading' ? (
        <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin mb-4" />
      ) : (
        <Icon className={cn(
          'h-8 w-8 mb-4',
          type === 'error' ? 'text-status-error' : 'text-muted-foreground'
        )} />
      )}
      {title && <h4 className="font-medium mb-1">{title}</h4>}
      <p className="text-sm text-muted-foreground">
        {message || defaultMessages[type]}
      </p>
    </div>
  );
}
