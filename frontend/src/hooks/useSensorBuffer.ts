import { useState, useCallback, useRef } from 'react';
import { SensorReading } from '@/types';

interface BufferedReading extends SensorReading {
  id: string;
}

interface UseSensorBufferOptions {
  maxSize?: number;
}

interface UseSensorBufferReturn {
  readings: BufferedReading[];
  addReading: (reading: SensorReading) => void;
  clearBuffer: () => void;
  getLatest: () => BufferedReading | null;
  getRange: (start: number, end: number) => BufferedReading[];
  getStats: () => { min: number; max: number; avg: number } | null;
}

export function useSensorBuffer(options: UseSensorBufferOptions = {}): UseSensorBufferReturn {
  const { maxSize = 1000 } = options;
  const [readings, setReadings] = useState<BufferedReading[]>([]);
  const idCounter = useRef(0);

  const addReading = useCallback((reading: SensorReading) => {
    const bufferedReading: BufferedReading = {
      ...reading,
      id: `reading-${idCounter.current++}`,
    };

    setReadings((prev) => {
      const newReadings = [...prev, bufferedReading];
      if (newReadings.length > maxSize) {
        return newReadings.slice(-maxSize);
      }
      return newReadings;
    });
  }, [maxSize]);

  const clearBuffer = useCallback(() => {
    setReadings([]);
  }, []);

  const getLatest = useCallback((): BufferedReading | null => {
    return readings[readings.length - 1] || null;
  }, [readings]);

  const getRange = useCallback((start: number, end: number): BufferedReading[] => {
    return readings.filter(
      (r) => r.timestamp >= start && r.timestamp <= end
    );
  }, [readings]);

  const getStats = useCallback(() => {
    if (readings.length === 0) return null;

    const values = readings.map((r) => r.value);
    return {
      min: Math.min(...values),
      max: Math.max(...values),
      avg: values.reduce((a, b) => a + b, 0) / values.length,
    };
  }, [readings]);

  return {
    readings,
    addReading,
    clearBuffer,
    getLatest,
    getRange,
    getStats,
  };
}
