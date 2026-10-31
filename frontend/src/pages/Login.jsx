import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AuthLayout } from '../layouts/AuthLayout';
import { Mail, Lock, ArrowRight, AlertCircle, Eye, EyeOff, Loader2 } from 'lucide-react';

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(form.email, form.password);
      if (user.role === 'admin') navigate('/admin');
      else if (user.role === 'staff') navigate('/staff');
      else navigate('/portal');
    } catch (err) {
      const data = err.response?.data;
      const message =
        data?.error ||
        data?.detail ||
        (typeof data === 'string' && !data.includes('<!doctype') ? data : null) ||
        'Invalid credentials. Please verify your email and password.';
      setError(typeof message === 'object' ? JSON.stringify(message) : message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Log in to manage your billing, subscriptions, and financial logs."
      quote="Replacing disjointed spreadsheets with Brightloop reduced invoice errors by 100%."
      quoteAuthor="Finance Department"
      quoteRole="Brightloop Software"
    >
      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200/80 flex items-start gap-3 text-sm text-red-700 animate-in fade-in duration-200">
          <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <div className="flex-1 leading-relaxed">{error}</div>
        </div>
      )}

      <form onSubmit={submit} className="space-y-4">
        {/* Email field */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
            Business Email
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Mail className="w-4 h-4" />
            </div>
            <input
              name="email"
              type="email"
              required
              placeholder="name@company.com"
              value={form.email}
              onChange={handle}
              className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-600/20 focus:border-indigo-600 transition shadow-sm"
            />
          </div>
        </div>

        {/* Password field */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Password
            </label>
            <Link
              to="/forgot-password"
              className="text-xs font-medium text-indigo-600 hover:text-indigo-700 transition"
            >
              Forgot password?
            </Link>
          </div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Lock className="w-4 h-4" />
            </div>
            <input
              name="password"
              type={showPassword ? 'text' : 'password'}
              required
              placeholder="••••••••••••"
              value={form.password}
              onChange={handle}
              className="w-full pl-10 pr-11 py-2.5 bg-white border border-slate-200 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-600/20 focus:border-indigo-600 transition shadow-sm"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 transition"
              tabIndex={-1}
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full mt-2 inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-medium text-sm transition-all shadow-md shadow-indigo-600/20 disabled:opacity-60 disabled:cursor-not-allowed group cursor-pointer"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Signing in...
            </>
          ) : (
            <>
              Sign in to Workspace
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </>
          )}
        </button>
      </form>

      {/* Alternative actions */}
      <div className="mt-8 text-center text-xs text-slate-500">
        Don't have an account yet?{' '}
        <Link to="/register" className="font-semibold text-indigo-600 hover:text-indigo-700 transition">
          Create customer account
        </Link>
      </div>
    </AuthLayout>
  );
}
