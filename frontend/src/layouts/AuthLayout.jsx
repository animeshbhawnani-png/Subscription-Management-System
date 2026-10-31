import React from 'react';

export function AuthLayout({ children, title, subtitle, quote, quoteAuthor, quoteRole }) {
  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-12 bg-slate-50 font-sans text-slate-800">
      {/* Left / Main form section */}
      <div className="lg:col-span-7 flex flex-col justify-between p-6 sm:p-12 lg:p-16">
        {/* Brand header */}
        <div className="flex items-center gap-2.5">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
              Brightloop
            </span>
            <span className="ml-1 text-[11px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">
              Billing OS
            </span>
          </div>
        </div>

        {/* Centered content box */}
        <div className="max-w-[420px] w-full mx-auto my-12">
          <div className="mb-8">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              {title}
            </h1>
            {subtitle && (
              <p className="mt-2 text-sm text-slate-500 leading-relaxed">
                {subtitle}
              </p>
            )}
          </div>
          {children}
        </div>

        {/* Footer info */}
        <div className="text-xs text-slate-400 flex flex-wrap items-center justify-between gap-4 border-t border-slate-200/60 pt-6">
          <p>© {new Date().getFullYear()} Brightloop Software Inc. All rights reserved.</p>
          <div className="flex gap-4">
            <span className="hover:text-slate-600 transition cursor-pointer">Security</span>
            <span className="hover:text-slate-600 transition cursor-pointer">Privacy</span>
            <span className="hover:text-slate-600 transition cursor-pointer">System Status</span>
          </div>
        </div>
      </div>

      {/* Right / Hero visual banner */}
      <div className="hidden lg:col-span-5 lg:flex flex-col justify-between p-12 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white relative overflow-hidden border-l border-slate-800">
        {/* Ambient background glows */}
        <div className="absolute -top-32 -right-32 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-violet-600/20 rounded-full blur-3xl pointer-events-none" />

        {/* Subtle decorative grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f293708_1px,transparent_1px),linear-gradient(to_bottom,#1f293708_1px,transparent_1px)] bg-[size:24px_24px] opacity-40 pointer-events-none" />

        {/* Top badge */}
        <div className="relative z-10 flex items-center justify-end">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/10 text-xs text-indigo-200">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            99.99% Uptime Engine
          </div>
        </div>

        {/* Interactive-looking mock metric card */}
        <div className="relative z-10 my-auto py-8">
          <div className="p-6 rounded-2xl bg-white/[0.07] backdrop-blur-xl border border-white/10 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <div>
                <p className="text-xs font-medium text-indigo-200">Monthly Recurring Revenue</p>
                <h4 className="text-2xl font-bold mt-1 tracking-tight text-white">₹8,42,500</h4>
              </div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                +18.4%
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4 pt-4 text-xs">
              <div>
                <p className="text-slate-400">Active Subscriptions</p>
                <p className="font-semibold text-white mt-0.5">1,248 clients</p>
              </div>
              <div>
                <p className="text-slate-400">Billing Cycle</p>
                <p className="font-semibold text-white mt-0.5">Automated Daily</p>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <p className="text-lg font-medium tracking-tight text-slate-200 leading-snug italic">
              "{quote || 'Centralized subscription workflows give complete transparency from first quotation to paid invoices.'}"
            </p>
            <div className="mt-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-400 flex items-center justify-center font-bold text-sm shadow">
                BL
              </div>
              <div>
                <p className="text-sm font-semibold text-white">{quoteAuthor || 'Brightloop Operations'}</p>
                <p className="text-xs text-indigo-300">{quoteRole || 'Automated Billing & Revenue Ops'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom micro-features */}
        <div className="relative z-10 pt-6 border-t border-white/10 flex items-center justify-between text-xs text-slate-400">
          <span>Enterprise Grade Security</span>
          <span>Zero Spreadsheets</span>
        </div>
      </div>
    </div>
  );
}

