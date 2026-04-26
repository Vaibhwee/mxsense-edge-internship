import { Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from './components/AppLayout.jsx'
import { ProtectedRoute } from './components/ProtectedRoute.jsx'
import Dashboard from './pages/Dashboard.jsx'
import DeviceDetail from './pages/DeviceDetail.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="devices/:deviceId" element={<DeviceDetail />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
