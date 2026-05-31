import { useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme, App as AntApp, Spin } from 'antd';
import { useAuthStore } from './store/authStore';
import { useSupervisorAuthStore } from './supervisor/store/supervisorAuthStore';
import { onAuthChange, getCurrentAdminData } from './services/authService';
import { onSupervisorAuthChange, getCurrentSupervisorData } from './supervisor/services/supervisorAuthService';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/MainLayout';
import SupervisorProtectedRoute from './supervisor/SupervisorProtectedRoute';
import SupervisorLayout from './supervisor/SupervisorLayout';

// Lazy load pages for better performance
const LandingPage = lazy(() => import('./pages/LandingPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const SupervisorLoginPage = lazy(() => import('./supervisor/pages/SupervisorLoginPage'));
const SupervisorDashboardPage = lazy(() => import('./supervisor/pages/SupervisorDashboardPage'));
const SupervisorOrgsPage = lazy(() => import('./supervisor/pages/SupervisorOrgsPage'));
const SupervisorOrgDetailPage = lazy(() => import('./supervisor/pages/SupervisorOrgDetailPage'));
const SupervisorBlockedUsersPage = lazy(() => import('./supervisor/pages/SupervisorBlockedUsersPage'));
const SupervisorMessagesPage = lazy(() => import('./supervisor/pages/SupervisorMessagesPage'));
const SupervisorSettingsPage = lazy(() => import('./supervisor/pages/SupervisorSettingsPage'));
import OwnerProtectedRoute from './owner/OwnerProtectedRoute';
const OwnerLoginPage = lazy(() => import('./owner/pages/OwnerLoginPage'));
const OwnerDashboardPage = lazy(() => import('./owner/pages/OwnerDashboardPage'));

// Admin Pages
const OverviewPage = lazy(() => import('./pages/OverviewPage'));
const UsersPage = lazy(() => import('./pages/UsersPage'));
const PackagesPage = lazy(() => import('./pages/PackagesPage'));
const MessagesPage = lazy(() => import('./pages/MessagesPage'));
const ComputersPage = lazy(() => import('./pages/ComputersPage'));
const AnnouncementsPage = lazy(() => import('./pages/AnnouncementsPage'));
const ReportsPage = lazy(() => import('./pages/ReportsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

function App() {
  const { setUser, setLoading } = useAuthStore();
  const { setSupervisor, setLoading: setSupervisorLoading } = useSupervisorAuthStore();

  useEffect(() => {
    // Listen for regular Admin Auth Changes
    const unsubscribeAdmin = onAuthChange(async (user) => {
      setUser(user);
      if (user) {
        try {
          const adminData = await getCurrentAdminData(user.uid);
          setUser(adminData);
        } catch (error) {
          console.error('Error fetching admin data:', error);
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    // Listen for Supervisor Auth Changes
    const unsubscribeSupervisor = onSupervisorAuthChange(async (user) => {
      if (user) {
        try {
          const result = await getCurrentSupervisorData(user.uid);
          setSupervisor(result?.supervisor || { uid: user.uid });
        } catch (error) {
          console.error('Error fetching supervisor data:', error);
          setSupervisor({ uid: user.uid });
        }
      } else {
        setSupervisor(null);
      }
      setSupervisorLoading(false);
    });

    return () => {
      unsubscribeAdmin();
      unsubscribeSupervisor();
    };
  }, [setUser, setLoading, setSupervisor, setSupervisorLoading]);

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#667eea',
          borderRadius: 8,
          fontFamily: 'Rubik, system-ui, sans-serif',
        },
      }}
    >
      <AntApp>
        <Router>
          <Suspense
            fallback={
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#fafbfc' }}>
                <Spin size="large" tip="טוען מערכת..." />
              </div>
            }
          >
            <Routes>
              {/* Public Routes */}
              <Route path='/' element={<LandingPage />} />
              <Route path='/login' element={<LoginPage />} />
              <Route path='/supervisor/login' element={<SupervisorLoginPage />} />

              {/* Protected Supervisor Routes */}
              <Route
                path='/supervisor'
                element={
                  <SupervisorProtectedRoute>
                    <SupervisorLayout />
                  </SupervisorProtectedRoute>
                }
              >
                <Route index element={<SupervisorDashboardPage />} />
                <Route path='organizations' element={<SupervisorOrgsPage />} />
                <Route path='organizations/:orgId' element={<SupervisorOrgDetailPage />} />
                <Route path='messages' element={<SupervisorMessagesPage />} />
                <Route path='blocked' element={<SupervisorBlockedUsersPage />} />
                <Route path='settings' element={<SupervisorSettingsPage />} />
              </Route>

              {/* Protected Admin Routes */}
              <Route
                path='/admin'
                element={
                  <ProtectedRoute>
                    <MainLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<OverviewPage />} />
                <Route path='users' element={<UsersPage />} />
                <Route path='packages' element={<PackagesPage />} />
                <Route path='messages' element={<MessagesPage />} />
                <Route path='computers' element={<ComputersPage />} />
                <Route path='announcements' element={<AnnouncementsPage />} />
                <Route path='reports' element={<ReportsPage />} />
                <Route path='settings' element={<SettingsPage />} />
              </Route>

              {/* Owner Routes */}
              <Route path='/owner/login' element={<OwnerLoginPage />} />
              <Route path='/owner' element={<OwnerProtectedRoute><OwnerDashboardPage /></OwnerProtectedRoute>} />

              {/* Catch all - redirect to home */}
              <Route path='*' element={<Navigate to='/' replace />} />
            </Routes>
          </Suspense>
        </Router>
      </AntApp>
    </ConfigProvider>
  );
}

export default App;
