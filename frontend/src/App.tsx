import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './auth/AuthContext'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { Layout } from './components/Layout'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { VerifyEmailPage } from './pages/VerifyEmailPage'
import { Dashboard } from './features/dashboard/Dashboard'
import { CVLibrary } from './features/cvs/CVLibrary'
import { JobTracker } from './features/jobs/JobTracker'
import { JobDetail } from './features/jobs/JobDetail'
import { ApplicationBoard } from './features/applications/ApplicationBoard'
import { ApplicationWorkspace } from './features/applications/ApplicationWorkspace'
import { AITools } from './features/ai/AITools'
import { ProfilePage } from './features/profile/ProfilePage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30_000 },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />
            <Route
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/cvs" element={<CVLibrary />} />
              <Route path="/jobs" element={<JobTracker />} />
              <Route path="/jobs/:jobId" element={<JobDetail />} />
              <Route path="/applications" element={<ApplicationBoard />} />
              <Route path="/applications/:appId" element={<ApplicationWorkspace />} />
              <Route path="/ai" element={<AITools />} />
              <Route path="/profile" element={<ProfilePage />} />
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}
