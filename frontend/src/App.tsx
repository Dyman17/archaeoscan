import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppProvider } from "@/context/AppContext";
import { MainLayout } from "@/components/layout/MainLayout";
import { Dashboard } from "@/pages/Dashboard";
import { Sensors } from "@/pages/Sensors";
import { MapView } from "@/pages/MapView";
import { Materials } from "@/pages/Materials";
import { CameraStream } from "@/pages/CameraStream";
import { AIAnalysis } from "@/pages/AIAnalysis";
import { Artifacts } from "@/pages/Artifacts";
import { Settings } from '@/pages/Settings';

import NotFound from './pages/NotFound';

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <AppProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <MainLayout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/sensors" element={<Sensors />} />
              <Route path="/map" element={<MapView />} />
              <Route path="/materials" element={<Materials />} />
              <Route path="/camera" element={<CameraStream />} />
              <Route path="/ai" element={<AIAnalysis />} />
              <Route path="/artifacts" element={<Artifacts />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </MainLayout>
        </BrowserRouter>
      </AppProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
