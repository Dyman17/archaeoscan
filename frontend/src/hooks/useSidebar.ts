import { useState, useCallback, useEffect } from 'react';

export type SidebarMode = 'expanded' | 'compact' | 'hidden';

interface UseSidebarOptions {
  defaultMode?: SidebarMode;
  mobileBreakpoint?: number;
}

interface UseSidebarReturn {
  mode: SidebarMode;
  setMode: (mode: SidebarMode) => void;
  toggle: () => void;
  width: number;
  isResizing: boolean;
  startResizing: () => void;
  stopResizing: () => void;
  resize: (width: number) => void;
  isMobile: boolean;
}

const EXPANDED_WIDTH = 240;
const COMPACT_WIDTH = 64;
const MIN_WIDTH = 64;
const MAX_WIDTH = 320;

export function useSidebar(options: UseSidebarOptions = {}): UseSidebarReturn {
  const { defaultMode = 'expanded', mobileBreakpoint = 768 } = options;

  const [mode, setModeState] = useState<SidebarMode>(defaultMode);
  const [width, setWidth] = useState(EXPANDED_WIDTH);
  const [isResizing, setIsResizing] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Handle responsive mode
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < mobileBreakpoint;
      setIsMobile(mobile);
      if (mobile && mode !== 'hidden') {
        setModeState('hidden');
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [mobileBreakpoint, mode]);

  const setMode = useCallback((newMode: SidebarMode) => {
    setModeState(newMode);
    switch (newMode) {
      case 'expanded':
        setWidth(EXPANDED_WIDTH);
        break;
      case 'compact':
        setWidth(COMPACT_WIDTH);
        break;
      case 'hidden':
        setWidth(0);
        break;
    }
  }, []);

  const toggle = useCallback(() => {
    if (isMobile) {
      setMode(mode === 'hidden' ? 'expanded' : 'hidden');
    } else {
      const modes: SidebarMode[] = ['expanded', 'compact', 'hidden'];
      const currentIndex = modes.indexOf(mode);
      const nextIndex = (currentIndex + 1) % modes.length;
      setMode(modes[nextIndex]);
    }
  }, [mode, setMode, isMobile]);

  const startResizing = useCallback(() => {
    setIsResizing(true);
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback((newWidth: number) => {
    const clampedWidth = Math.min(Math.max(newWidth, MIN_WIDTH), MAX_WIDTH);
    setWidth(clampedWidth);

    // Auto-snap to modes
    if (clampedWidth <= MIN_WIDTH + 10) {
      setModeState('compact');
    } else if (clampedWidth >= EXPANDED_WIDTH - 20) {
      setModeState('expanded');
    }
  }, []);

  return {
    mode,
    setMode,
    toggle,
    width,
    isResizing,
    startResizing,
    stopResizing,
    resize,
    isMobile,
  };
}
