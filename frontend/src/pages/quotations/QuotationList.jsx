import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { subscriptionService } from '../../services/subscriptionService'
import { useAuth } from '../../context/AuthContext'
import StatusBadge from '../../components/StatusBadge'
import { Plus, Search, FileText, ArrowRight, Loader2, AlertCircle } from 'lucide-react'

export default function QuotationList() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [quotations, setQuotations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const isStaffOrAdmin = user?.role === 'admin' || user?.role === 'staff'

  const fetchQuotations = async () => {
    try {
      setLoading(true)
      const params = {}
      if (search) params.search = search
      if (statusFilter) params.status = statusFilter
      const res = await subscriptionService.getQuotations(params)
      setQuotations(res.data.data || [])
    } catch (err) {
      setError('Failed to load quotations.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchQuotations()
  }, [statusFilter])

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    fetchQuotations()
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Quotations</h2>
          <p className="text-xs text-slate-500">
            {isStaffOrAdmin
              ? 'Prepare, dispatch, and convert price quotes into software subscriptions.'
              : 'Review quotations prepared for your organization and accept terms.'}
          </p>
        </div>
        {isStaffOrAdmin && (
          <Link
            to="/quotations/new"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-semibold shadow-sm hover:bg-indigo-700 transition"
          >
            <Plus className="w-4 h-4" />
            Create Quotation
          </Link>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />
          {error}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search quotation #..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
          />
        </form>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 text-slate-700"
          >
            <option value="">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="accepted">Accepted</option>
            <option value="rejected">Rejected</option>
            <option value="expired">Expired</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white border border-slate-200/80 rounded-2xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 flex flex-col items-center justify-center text-slate-400 gap-3">
            <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
            <p className="text-xs">Loading quotations...</p>
          </div>
        ) : quotations.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <FileText className="w-10 h-10 mx-auto text-slate-300 mb-3" />
            <p className="text-sm font-semibold text-slate-700">No quotations found</p>
            <p className="text-xs text-slate-400 mt-1">
              {isStaffOrAdmin
                ? 'Get started by creating a new price quotation.'
                : 'You have no quotations issued at this time.'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/50 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-6">Quote #</th>
                  <th className="py-3 px-6">Customer</th>
                  <th className="py-3 px-6">Status</th>
                  <th className="py-3 px-6">Valid Until</th>
                  <th className="py-3 px-6 text-right">Total Amount</th>
                  <th className="py-3 px-6 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {quotations.map((q) => (
                  <tr key={q.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-6 font-semibold text-slate-900 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-indigo-500" />
                      {q.quotation_number}
                    </td>
                    <td className="py-3.5 px-6 text-slate-600">{q.customer_email}</td>
                    <td className="py-3.5 px-6">
                      <StatusBadge status={q.status} />
                    </td>
                    <td className="py-3.5 px-6 text-slate-500">{q.valid_until || '—'}</td>
                    <td className="py-3.5 px-6 text-right font-bold text-slate-900">
                      ${parseFloat(q.total).toFixed(2)}
                    </td>
                    <td className="py-3.5 px-6 text-center">
                      <Link
                        to={`/quotations/${q.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-indigo-600 hover:bg-indigo-50 font-medium transition"
                      >
                        View Details
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
