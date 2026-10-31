import React from 'react'

export function StatusBadge({ status }) {
  const styles = {
    draft: 'bg-slate-100 text-slate-700 border-slate-200',
    sent: 'bg-blue-50 text-blue-700 border-blue-200',
    accepted: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    rejected: 'bg-rose-50 text-rose-700 border-rose-200',
    expired: 'bg-amber-50 text-amber-700 border-amber-200',
    active: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    paused: 'bg-amber-50 text-amber-700 border-amber-200',
    cancelled: 'bg-rose-50 text-rose-700 border-rose-200',
  }

  const currentStyle = styles[status?.toLowerCase()] || 'bg-slate-100 text-slate-700 border-slate-200'

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${currentStyle}`}
    >
      {status}
    </span>
  )
}

export default StatusBadge
