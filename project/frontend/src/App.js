import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute, PublicOnlyRoute } from './routes/ProtectedRoute';
import { Toaster } from 'react-hot-toast';

// Pages
import LandingPage from './pages/student/LandingPage';
import StudentLogin from './pages/student/StudentLogin';
import StudentSignup from './pages/student/StudentSignup';
import ChatPage from './pages/student/ChatPage';
import AdminLogin from './pages/admin/AdminLogin';
import AdminDashboard from './pages/admin/AdminDashboard';
import FAQManager from './pages/admin/FAQManager';
import ProcedureManager from './pages/admin/ProcedureManager';
import DocumentUpload from './pages/admin/DocumentUpload';
import QueryLogs from './pages/admin/QueryLogs';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#16161f',
              color: '#f3f4f6',
              border: '1px solid rgba(255,255,255,0.1)',
              fontFamily: '"DM Sans", sans-serif',
              fontSize: '14px',
            },
            success: { iconTheme: { primary: '#10b981', secondary: '#0a0a0f' } },
            error: { iconTheme: { primary: '#f43f5e', secondary: '#0a0a0f' } },
          }}
        />
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<PublicOnlyRoute><LandingPage /></PublicOnlyRoute>} />
          <Route path="/login" element={<PublicOnlyRoute><StudentLogin /></PublicOnlyRoute>} />
          <Route path="/signup" element={<PublicOnlyRoute><StudentSignup /></PublicOnlyRoute>} />
          <Route path="/admin/login" element={<PublicOnlyRoute><AdminLogin /></PublicOnlyRoute>} />

          {/* Student protected routes */}
          <Route path="/chat" element={<ProtectedRoute requiredRole="student"><ChatPage /></ProtectedRoute>} />

          {/* Admin protected routes */}
          <Route path="/admin/dashboard" element={<ProtectedRoute requiredRole="admin"><AdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/faqs" element={<ProtectedRoute requiredRole="admin"><FAQManager /></ProtectedRoute>} />
          <Route path="/admin/procedures" element={<ProtectedRoute requiredRole="admin"><ProcedureManager /></ProtectedRoute>} />
          <Route path="/admin/documents" element={<ProtectedRoute requiredRole="admin"><DocumentUpload /></ProtectedRoute>} />
          <Route path="/admin/logs" element={<ProtectedRoute requiredRole="admin"><QueryLogs /></ProtectedRoute>} />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
