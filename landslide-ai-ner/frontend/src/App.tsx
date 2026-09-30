import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';

import { Navbar } from './components/layout/Navbar';
import { SystemHeader } from './components/layout/SystemHeader';

import { DashboardPage } from './pages/DashboardPage';
import { LiveMapPage } from './pages/LiveMapPage';
import { RiskAnalysisPage } from './pages/RiskAnalysisPage';
import { WeatherPage } from './pages/WeatherPage';
import { SensorsPage } from './pages/SensorsPage';
import { FieldReportsPage } from './pages/FieldReportsPage';
import { AlertsPage } from './pages/AlertsPage';
import { LoginPage } from './pages/LoginPage';

import { useAuthStore } from './store/authStore';
import { useDashboardStore } from './store/dashboardStore';
import { api } from './services/api';

// Guard: redirects unauthenticated users to /login
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

// Main application layout (header + nav + page content)
const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="min-h-screen bg-[#0a0f1e] flex flex-col">
    <SystemHeader />
    <Navbar />
    <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
      {children}
    </main>
  </div>
);

const App: React.FC = () => {
  const { checkAuth } = useAuthStore();
  const { setSummary } = useDashboardStore();

  // On mount: verify existing token and pre-load dashboard summary
  useEffect(() => {
    checkAuth();
    api.getSummary().then(setSummary).catch(() => {});
  }, []);

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected application routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout>
              <DashboardPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/map"
        element={
          <ProtectedRoute>
            <AppLayout>
              <LiveMapPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/risk-analysis"
        element={
          <ProtectedRoute>
            <AppLayout>
              <RiskAnalysisPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/weather"
        element={
          <ProtectedRoute>
            <AppLayout>
              <WeatherPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/sensors"
        element={
          <ProtectedRoute>
            <AppLayout>
              <SensorsPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <AppLayout>
              <FieldReportsPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/alerts"
        element={
          <ProtectedRoute>
            <AppLayout>
              <AlertsPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
