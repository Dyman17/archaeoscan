import React, { ReactNode } from 'react';
import { TopBar } from './TopBar';
import { Sidebar } from './Sidebar';
import { useSidebar } from '@/hooks/useSidebar';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const {
    mode,
    width,
    isResizing,
    toggle,
    startResizing,
    stopResizing,
    resize,
  } = useSidebar();

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-background">
      <TopBar onMenuClick={toggle} />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          mode={mode}
          width={width}
          isResizing={isResizing}
          onToggle={toggle}
          onStartResizing={startResizing}
          onStopResizing={stopResizing}
          onResize={resize}
        />
        
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
