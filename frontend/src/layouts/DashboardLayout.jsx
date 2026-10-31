import React from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  Building2, 
  Users, 
  Layers, 
  CreditCard, 
  Receipt, 
  Tag, 
  BarChart3, 
  LogOut, 
  ShieldCheck, 
  CheckCircle,
  Clock,
  Sparkles
} from 'lucide-react';

import { Link, useLocation } from 'react-router-dom';

export default function DashboardLayout({ title, subtitle, role, children }) {
  const { user, logout } = useAuth();
  const location = useLocation();

  const roleBadgeColors = {
    admin: 'bg-purple-50 text-purple-700 border-purple-200/80',
    staff: 'bg-blue-50 text-blue-700 border-blue-200/80',
    customer: 'bg-emerald-50 text-emerald-700 border-emerald-200/80',
  };

  const navItems = [
    { label: 'Overview', icon: BarChart3, path: user?.role === 'admin' ? '/admin' : user?.role === 'staff' ? '/staff' : '/portal' },
    { label: 'Quotations', icon: Receipt, path: '/quotations' },
    { label: 'Subscriptions', icon: Layers, path: '/subscriptions' },
    ...(role === 'admin' || role === 'staff'
      ? [
          { label: 'Customers', icon: Users, path: '#' },
          { label: 'Products & Variants', icon: Building2, path: '#' },
        ]
      : []),
  ];

  return (
    <div className="min-h-screen bg-slate-50/60 font-sans text-slate-800 flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-200/80 bg-white flex flex-col justify-between shrink-0">
        <div>
          {/* Brand header */}
          <div className="h-16 px-6 flex items-center gap-2.5 border-b border-slate-100">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-md shadow-indigo-500/20">
              <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
              </svg>
            </div>
            <div>
              <span className="font-bold text-slate-900 tracking-tight text-base">Brightloop</span>
              <span className="block text-[10px] text-slate-400 font-medium uppercase tracking-wider">Subscription Ops</span>
            </div>
          </div>

          {/* Nav links */}
          <div className="p-4 space-y-1">
            <p className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Main Navigation</p>
            {navItems.map((item, idx) => {
              const Icon = item.icon;
              const isActive = item.path !== '#' && (location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path)));
              return (
                <Link
                  key={idx}
                  to={item.path}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-700 shadow-sm'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>

        {/* User footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2.5 truncate">
              <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 font-bold text-xs flex items-center justify-center shrink-0">
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="truncate">
                <p className="text-xs font-semibold text-slate-900 truncate">{user?.email}</p>
                <span className={`inline-block text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${roleBadgeColors[user?.role] || roleBadgeColors.customer}`}>
                  {user?.role}
                </span>
              </div>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-semibold text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
          >
            <LogOut className="w-3.5 h-3.5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-8 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-slate-900 tracking-tight">{title}</h1>
            {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
          </div>

          <div className="flex items-center gap-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200/70 text-emerald-700 text-xs font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Module 1 Ready
            </div>
          </div>
        </header>

        {/* Page body */}
        <main className="p-8 flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}

