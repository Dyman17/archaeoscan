import { useCallback, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Radio, 
  Map, 
  Layers, 
  Video, 
  Brain,
  Database,
  Settings,
  ChevronLeft,
  ChevronRight,
  GripVertical
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { SidebarMode } from '@/hooks/useSidebar';

interface SidebarProps {
  mode: SidebarMode;
  width: number;
  isResizing: boolean;
  onToggle: () => void;
  onStartResizing: () => void;
  onStopResizing: () => void;
  onResize: (width: number) => void;
}

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/' },
  { id: 'sensors', label: 'Sensors', icon: Radio, path: '/sensors' },
  { id: 'map', label: 'Map', icon: Map, path: '/map' },
  { id: 'materials', label: 'Materials', icon: Layers, path: '/materials' },
  { id: 'camera', label: 'Camera Stream', icon: Video, path: '/camera' },
  { id: 'ai', label: 'AI Analysis', icon: Brain, path: '/ai' },
  { id: 'artifacts', label: 'Artifacts DB', icon: Database, path: '/artifacts' },
  { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' },
];

export function Sidebar({
  mode,
  width,
  isResizing,
  onToggle,
  onStartResizing,
  onStopResizing,
  onResize,
}: SidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();

  const isCompact = mode === 'compact' || width <= 80;
  const isHidden = mode === 'hidden';

  // Handle mouse move for resizing
  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (isResizing) {
        onResize(e.clientX);
      }
    },
    [isResizing, onResize]
  );

  const handleMouseUp = useCallback(() => {
    onStopResizing();
  }, [onStopResizing]);

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing, handleMouseMove, handleMouseUp]);

  if (isHidden) {
    return (
      <Button
        variant="ghost"
        size="icon"
        onClick={onToggle}
        className="fixed left-2 top-14 z-50 bg-card border border-border shadow-lg"
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    );
  }

  return (
    <aside
      className={cn(
        'bg-sidebar border-r border-sidebar-border flex flex-col shrink-0 relative transition-all duration-200',
        isResizing && 'select-none'
      )}
      style={{ width: isCompact ? 64 : width }}
    >
      {/* Toggle button */}
      <div className="p-2 flex justify-end border-b border-sidebar-border">
        <Button variant="ghost" size="icon" onClick={onToggle} className="h-8 w-8">
          <ChevronLeft className={cn('h-4 w-4 transition-transform', isCompact && 'rotate-180')} />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          const button = (
            <Button
              key={item.id}
              variant={isActive ? 'secondary' : 'ghost'}
              className={cn(
                'w-full justify-start gap-3 h-10',
                isActive && 'bg-sidebar-accent text-sidebar-accent-foreground border border-sidebar-primary/30',
                isCompact && 'justify-center px-0'
              )}
              onClick={() => navigate(item.path)}
            >
              <Icon className={cn('h-5 w-5 shrink-0', isActive && 'text-sidebar-primary')} />
              {!isCompact && <span className="truncate">{item.label}</span>}
            </Button>
          );

          if (isCompact) {
            return (
              <Tooltip key={item.id} delayDuration={0}>
                <TooltipTrigger asChild>{button}</TooltipTrigger>
                <TooltipContent side="right" className="font-medium">
                  {item.label}
                </TooltipContent>
              </Tooltip>
            );
          }

          return button;
        })}
      </nav>

      {/* Resize handle */}
      {!isCompact && (
        <div
          className={cn(
            'absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-primary/50 transition-colors group',
            isResizing && 'bg-primary/50'
          )}
          onMouseDown={onStartResizing}
        >
          <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-8 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <GripVertical className="h-4 w-4 text-muted-foreground" />
          </div>
        </div>
      )}

      {/* Version info */}
      <div className={cn('p-3 border-t border-sidebar-border', isCompact && 'p-2')}>
        {isCompact ? (
          <Tooltip delayDuration={0}>
            <TooltipTrigger asChild>
              <div className="text-xs text-muted-foreground text-center">v1</div>
            </TooltipTrigger>
            <TooltipContent side="right">ArchaeoScan v1.0.0</TooltipContent>
          </Tooltip>
        ) : (
          <div className="text-xs text-muted-foreground">ArchaeoScan v1.0.0</div>
        )}
      </div>
    </aside>
  );
}
