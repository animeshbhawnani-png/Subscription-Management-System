import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import DashboardLayout from './layouts/DashboardLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import { Shield, Sparkles, CheckCircle2, TrendingUp, Layers, Receipt } from 'lucide-react';

function ModuleOverview({ roleName, roleDesc }) {
  return (
    <div className="space-y-6 max-w-6xl">
      {/* Welcome Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-900 via-indigo-950 to-slate-900 text-white shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-radial-gradient from-indigo-500/20 to-transparent pointer-events-none" />
        <div className="relative z-10 max-w-2xl">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white/10 text-indigo-200 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            Module 1 Complete
          </span>
          <h2 className="text-2xl font-bold tracking-tight">Welcome to {roleName} Workspace</h2>
          <p className="mt-2 text-sm text-indigo-100/80 leading-relaxed">{roleDesc}</p>
        </div>
      </div>

      {/* Metric Cards Preview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Security Check</span>
            <Shield className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-extrabold text-slate-900 tracking-tight">Active</p>
          <p className="text-xs text-slate-400 mt-1">JWT Bearer Auth & Role Constraints Live</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Database Engine</span>
            <Layers className="w-4 h-4 text-indigo-600" />
          </div>
          <p className="text-2xl font-extrabold text-slate-900 tracking-tight">PostgreSQL</p>
          <p className="text-xs text-slate-400 mt-1">Connected via Supabase Transaction Pooler</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Next Milestone</span>
            <Receipt className="w-4 h-4 text-amber-500" />
          </div>
          <p className="text-2xl font-extrabold text-slate-900 tracking-tight">Module 2</p>
          <p className="text-xs text-slate-400 mt-1">Products & Variant Configuration</p>
        </div>
      </div>
    </div>
  );
}

const AdminDashboard = () => (
  <DashboardLayout title="Admin Control Center" subtitle="Complete administrative authority across customers, staff, and pricing plans." role="admin">
    <ModuleOverview roleName="Admin" roleDesc="You have full platform privilege: create internal staff accounts, configure product lines and variants, adjust global tax policies, and inspect financial reports." />
  </DashboardLayout>
);

const StaffDashboard = () => (
  <DashboardLayout title="Operations Workspace" subtitle="Day-to-day subscription and invoice pipeline operations." role="staff">
    <ModuleOverview roleName="Staff" roleDesc="Manage registered clients, dispatch subscription quotations, generate recurring invoices, and record manual payments against outstanding statements." />
  </DashboardLayout>
);

const CustomerPortal = () => (
  <DashboardLayout title="Customer Subscription Portal" subtitle="Self-serve billing dashboard and active license seats." role="customer">
    <ModuleOverview roleName="Customer" roleDesc="Review your current active software subscriptions, download PDF tax invoices, check outstanding statements, and renew or pause billing cycles." />
  </DashboardLayout>
);

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public auth pages */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* Protected role-specific portals */}
        <Route
          path="/admin/*"
          element={
            <PrivateRoute role="admin">
              <AdminDashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/staff/*"
          element={
            <PrivateRoute role="staff">
              <StaffDashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/portal/*"
          element={
            <PrivateRoute>
              <CustomerPortal />
            </PrivateRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </AuthProvider>
  );
}
