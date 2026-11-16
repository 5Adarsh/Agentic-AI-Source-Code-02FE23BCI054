import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import ProtectedRoute from './components/layout/ProtectedRoute'

// Auth
import LoginPage from './pages/auth/LoginPage'

// Dashboard
import DashboardPage from './pages/dashboard/DashboardPage'

// Faculty
import FacultyListPage from './pages/faculty/FacultyListPage'
import FacultyDetailPage from './pages/faculty/FacultyDetailPage'
import FacultyFormPage from './pages/faculty/FacultyFormPage'

// Publications
import PublicationsPage from './pages/publications/PublicationsPage'
import PublicationDetailPage from './pages/publications/PublicationDetailPage'
import ImportPage from './pages/publications/ImportPage'

// Duplicates & Verification
import DuplicatesPage from './pages/duplicates/DuplicatesPage'
import VerificationPage from './pages/verification/VerificationPage'

// Agents
import AgentsPage from './pages/agents/AgentsPage'

// Analytics
import AnalyticsPage from './pages/analytics/AnalyticsPage'

// Reports
import ReportsPage from './pages/reports/ReportsPage'

// Settings
import SettingsPage from './pages/settings/SettingsPage'

// 404
import NotFoundPage from './pages/NotFoundPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected — wrapped in layout */}
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />

            {/* Faculty */}
            <Route path="/faculty" element={<FacultyListPage />} />
            <Route path="/faculty/new" element={<FacultyFormPage />} />
            <Route path="/faculty/:id" element={<FacultyDetailPage />} />
            <Route path="/faculty/:id/edit" element={<FacultyFormPage />} />

            {/* Publications */}
            <Route path="/publications" element={<PublicationsPage />} />
            <Route path="/publications/import" element={<ImportPage />} />
            <Route path="/publications/:id" element={<PublicationDetailPage />} />

            {/* Duplicates */}
            <Route path="/duplicates" element={<DuplicatesPage />} />

            {/* Verification Center */}
            <Route path="/verification" element={<VerificationPage />} />

            {/* Agents */}
            <Route path="/agents" element={<AgentsPage />} />

            {/* Analytics */}
            <Route path="/analytics" element={<AnalyticsPage />} />

            {/* Reports */}
            <Route path="/reports" element={<ReportsPage />} />

            {/* Settings */}
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  )
}
