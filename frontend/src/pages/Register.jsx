import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { AuthLayout } from '../layouts/AuthLayout';
import { Mail, Lock, ArrowRight, AlertCircle, CheckCircle2, Check, X, Loader2, Eye, EyeOff } from 'lucide-react';

export default function Register() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  // Real-time password criteria verification
  const rules = [
    { label: 'At least 9 characters long', valid: form.password.length >= 9 },
    { label: 'One uppercase letter', valid: /[A-Z]/.test(form.password) },
    { label: 'One lowercase letter', valid: /[a-z]/.test(form.password) },
    { label: 'One special symbol or number', valid: /[^a-zA-Z]/.test(form.password) },
  ];

  const allRulesPassed = rules.every((r) => r.valid);

  async function submit(e) {
    e.preventDefault();
    setError('');
    if (!allRulesPassed) {
      setError('Please satisfy all password security criteria before registering.');
      return;
    }

    setLoading(true);
    try {
      await api.post('/auth/register/', form);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 1800);
    } catch (err) {
      const errData = err.response?.data?.error;
      if (typeof errData === 'object') {
        const msg = Object.entries(errData)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(' ') : v}`)
          .join('\n');
        setError(msg);
      } else {
        setError(errData || 'Registration failed. Please try another email.');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Register as a customer to browse plans, manage active seats, and inspect billing records."
      quote="Transparent billing cycle logs allow us to track every single subscription renewal effortlessly."
      quoteAuthor="Customer Portal Experience"
      quoteRole="Self-Serve Operations"
    >
      {success && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200/80 flex items-start gap-3 text-sm text-emerald-800 animate-in fade-in duration-200">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
          <div className="flex-1 leading-relaxed">
            Account created successfully! Transferring you to login...
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200/80 flex items-start gap-3 text-sm text-red-700 animate-in fade-in duration-200">
          <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <div className="flex-1 leading-relaxed whitespace-pre-line">{error}</div>
        </div>
      )}

      <form onSubmit={submit} className="space-y-4">
        {/* Email field */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
            Work Email Address
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Mail className="w-4 h-4" />
            </div>
            <input
              name="email"
              type="email"
              required
              placeholder="alex@brightloop.io"
              value={form.email}
              onChange={handle}
              className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-600/20 focus:border-indigo-600 transition shadow-sm"
            />
          </div>
        </div>

        {/* Password field */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
            Choose Password
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Lock className="w-4 h-4" />
            </div>
            <input
              name="password"
              type={showPassword ? 'text' : 'password'}
              required
              placeholder="Create strong passphrase"
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

        {/* Live criteria checklist */}
        <div className="p-3.5 bg-slate-100/70 rounded-xl border border-slate-200/60 space-y-2">
          <p className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider">
            Password Requirements
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
            {rules.map((rule, idx) => (
              <div
                key={idx}
                className={`flex items-center gap-1.5 transition-colors ${
                  rule.valid ? 'text-emerald-700 font-medium' : 'text-slate-400'
                }`}
              >
                {rule.valid ? (
                  <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                ) : (
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-300 ml-1 mr-1" />
                )}
                <span>{rule.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !allRulesPassed}
          className="w-full mt-2 inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-medium text-sm transition-all shadow-md shadow-indigo-600/20 disabled:opacity-60 disabled:cursor-not-allowed group cursor-pointer"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Creating profile...
            </>
          ) : (
            <>
              Register Customer Account
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </>
          )}
        </button>
      </form>

      <div className="mt-8 text-center text-xs text-slate-500">
        Already registered with Brightloop?{' '}
        <Link to="/login" className="font-semibold text-indigo-600 hover:text-indigo-700 transition">
          Sign in here
        </Link>
      </div>
    </AuthLayout>
  );
}
