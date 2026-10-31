import React, { useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import { AuthLayout } from '../layouts/AuthLayout';
import { Lock, ArrowRight, AlertCircle, CheckCircle2, Check, Loader2, Eye, EyeOff } from 'lucide-react';

export default function ResetPassword() {
  const [params] = useSearchParams();
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const rules = [
    { label: 'At least 9 characters long', valid: password.length >= 9 },
    { label: 'One uppercase letter', valid: /[A-Z]/.test(password) },
    { label: 'One lowercase letter', valid: /[a-z]/.test(password) },
    { label: 'One special symbol or number', valid: /[^a-zA-Z]/.test(password) },
  ];

  const allRulesPassed = rules.every((r) => r.valid);

  async function submit(e) {
    e.preventDefault();
    setError('');
    if (!allRulesPassed) {
      setError('Please satisfy all password security criteria before continuing.');
      return;
    }

    setLoading(true);
    try {
      await api.post('/auth/password-reset/confirm/', {
        uid: params.get('uid'),
        token: params.get('token'),
        new_password: password,
      });
      setDone(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Password update failed. The token may be expired.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Establish new password"
      subtitle="Enter a new strong passphrase to regain secure access to your account."
      quote="End-to-end token verification preserves audit integrity across all client logins."
      quoteAuthor="Zero Trust Architecture"
      quoteRole="Brightloop Platform"
    >
      {done ? (
        <div className="p-6 rounded-2xl bg-emerald-50 border border-emerald-200/80 text-emerald-900 space-y-4 animate-in fade-in duration-200">
          <div className="flex items-center gap-2 font-semibold">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            Password successfully refreshed
          </div>
          <p className="text-sm text-emerald-800 leading-relaxed">
            Your login credentials have been saved. Forwarding you to the sign-in portal...
          </p>
        </div>
      ) : (
        <>
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200/80 flex items-start gap-3 text-sm text-red-700">
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <div className="flex-1 leading-relaxed">{error}</div>
            </div>
          )}

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                New Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  placeholder="Enter strong passphrase"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
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

            <button
              type="submit"
              disabled={loading || !allRulesPassed}
              className="w-full inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-medium text-sm transition-all shadow-md shadow-indigo-600/20 disabled:opacity-60 disabled:cursor-not-allowed group cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving updates...
                </>
              ) : (
                <>
                  Update Password & Continue
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 text-center">
            <Link to="/login" className="text-xs font-semibold text-slate-600 hover:text-indigo-600 transition">
              Cancel and return to login
            </Link>
          </div>
        </>
      )}
    </AuthLayout>
  );
}
