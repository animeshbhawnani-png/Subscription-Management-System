import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/** Redirects unauthenticated users to /login. Optionally restricts to a role or array of roles. */
export default function PrivateRoute({ children, role, roles }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="p-8 text-gray-400">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  if (role && user.role !== role) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/login" replace />
  return children
}

