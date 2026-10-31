import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { subscriptionService } from '../../services/subscriptionService'
import { useAuth } from '../../context/AuthContext'
import StatusBadge from '../../components/StatusBadge'
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Repeat,
  Loader2,
  AlertCircle,
  FileText,
  Calendar,
  User,
  Shield,
  Layers,
} from 'lucide-react'

export default function QuotationDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [quotation, setQuotation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [billingInterval, setBillingInterval] = useState('monthly')

  const isStaffOrAdmin = user?.role === 'admin' || user?.role === 'staff'

  const fetchDetail = async () => {
    try {
      setLoading(true)
      const res = await subscriptionService.getQuotation(id)
      setQuotation(res.data.data)
    } catch (err) {
      setError('Failed to fetch quotation details.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDetail()
  }, [id])

  const handleAccept = async () => {
    try {
      setActionLoading(true)
      setError('')
      const res = await subscriptionService.acceptQuotation(id)
      setQuotation(res.data.data)
      setSuccessMsg('Quotation accepted successfully!')
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to accept quotation.')
    } finally {
      setActionLoading(false)
    }
  }

  const handleReject = async () => {
    try {
      setActionLoading(true)
      setError('')
      const res = await subscriptionService.rejectQuotation(id)
      setQuotation(res.data.data)
      setSuccessMsg('Quotation marked as rejected.')
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to reject quotation.')
    } finally {
      setActionLoading(false)
    }
  }

  const handleConvert = async () => {
    try {
      setActionLoading(true)
      setError('')
      const res = await subscriptionService.convertQuotation(id, { billing_interval: billingInterval })
      setSuccessMsg('Quotation successfully converted into an active Subscription!')
      navigate(`/subscriptions/${res.data.data.id}`)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to convert quotation to subscription.')
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="p-12 flex flex-col items-center justify-center text-slate-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
        <p className="text-xs">Loading quotation details...</p>
      </div>
    )
  }

  if (!quotation) {
    return (
      <div className="p-8 text-center text-slate-500">
        <p>Quotation not found.</p>
        <Link to="/quotations" className="text-indigo-600 font-semibold text-xs mt-2 inline-block">
          Return to list
        </Link>
      </div>
    )
  }

  const canAcceptOrReject =
    (user?.email === quotation.customer_email || isStaffOrAdmin) &&
    (quotation.status === 'draft' || quotation.status === 'sent')

  const canConvert = isStaffOrAdmin && quotation.status === 'accepted' && !quotation.has_subscription

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/quotations"
            className="p-2 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                {quotation.quotation_number}
              </h2>
              <StatusBadge status={quotation.status} />
            </div>
            <p className="text-xs text-slate-500">Created on {new Date(quotation.created_at).toLocaleDateString()}</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {canAcceptOrReject && (
            <>
              <button
                onClick={handleReject}
                disabled={actionLoading}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-rose-200 text-rose-600 bg-rose-50/50 hover:bg-rose-100/70 text-xs font-semibold transition"
              >
                <XCircle className="w-3.5 h-3.5" />
                Reject
              </button>
              <button
                onClick={handleAccept}
                disabled={actionLoading}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700 shadow-sm transition"
              >
                <CheckCircle className="w-3.5 h-3.5" />
                Accept Quote
              </button>
            </>
          )}

          {quotation.has_subscription && (
            <Link
              to={`/subscriptions/${quotation.subscription_id}`}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold hover:bg-indigo-100 transition"
            >
              <Layers className="w-3.5 h-3.5" />
              View Subscription ({quotation.subscription_number})
            </Link>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />
          {error}
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
          {successMsg}
        </div>
      )}

      {/* Conversion Banner if Accepted and not converted */}
      {canConvert && (
        <div className="p-5 rounded-2xl bg-indigo-900 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-lg shadow-indigo-950/10">
          <div>
            <h4 className="text-sm font-bold flex items-center gap-1.5">
              <Repeat className="w-4 h-4 text-indigo-300" />
              Ready to Convert to Live Subscription
            </h4>
            <p className="text-xs text-indigo-200/80 mt-0.5">
              This quotation was approved by the customer and can now be activated as a recurring subscription contract.
            </p>
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <select
              value={billingInterval}
              onChange={(e) => setBillingInterval(e.target.value)}
              className="px-3 py-2 bg-indigo-800 border border-indigo-700 rounded-xl text-xs text-white focus:outline-none"
            >
              <option value="monthly">Monthly Cycle</option>
              <option value="quarterly">Quarterly Cycle</option>
              <option value="yearly">Annual Cycle</option>
            </select>
            <button
              onClick={handleConvert}
              disabled={actionLoading}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white text-indigo-900 font-bold text-xs hover:bg-indigo-50 transition shadow"
            >
              {actionLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Repeat className="w-3.5 h-3.5" />}
              Convert Now
            </button>
          </div>
        </div>
      )}

      {/* Meta Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-sm">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <User className="w-3.5 h-3.5" /> Customer Account
          </span>
          <p className="text-sm font-bold text-slate-900 mt-1 truncate">{quotation.customer_email}</p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-sm">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5" /> Validity Deadline
          </span>
          <p className="text-sm font-bold text-slate-900 mt-1">{quotation.valid_until || 'No expiration set'}</p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-sm">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5" /> Created By
          </span>
          <p className="text-sm font-bold text-slate-900 mt-1 truncate">
            {quotation.created_by_email || 'Staff Operations'}
          </p>
        </div>
      </div>

      {/* Line Items Table */}
      <div className="bg-white border border-slate-200/80 rounded-2xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Quoted Line Items</h3>
          <span className="text-xs text-slate-500">{quotation.items.length} item(s)</span>
        </div>
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50/50 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <th className="py-3 px-6">Product & Edition</th>
              <th className="py-3 px-6 text-center">Quantity</th>
              <th className="py-3 px-6 text-right">Unit Price</th>
              <th className="py-3 px-6 text-right">Subtotal</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {quotation.items.map((item) => (
              <tr key={item.id}>
                <td className="py-3.5 px-6">
                  <p className="font-bold text-slate-900">{item.product_name}</p>
                  {item.variant_name && (
                    <span className="inline-block px-2 py-0.5 rounded text-[10px] bg-slate-100 text-slate-600 font-medium mt-0.5">
                      Variant: {item.variant_name}
                    </span>
                  )}
                </td>
                <td className="py-3.5 px-6 text-center text-slate-600">{item.quantity}</td>
                <td className="py-3.5 px-6 text-right text-slate-600">${parseFloat(item.unit_price).toFixed(2)}</td>
                <td className="py-3.5 px-6 text-right font-bold text-slate-900">
                  ${parseFloat(item.subtotal).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="bg-slate-50/50 font-bold border-t border-slate-200">
              <td colSpan={3} className="py-4 px-6 text-right text-slate-600 uppercase tracking-wider text-xs">
                Total Agreement Amount:
              </td>
              <td className="py-4 px-6 text-right text-base text-indigo-700">${parseFloat(quotation.total).toFixed(2)}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      {/* Notes */}
      {quotation.notes && (
        <div className="p-5 bg-white border border-slate-200/80 rounded-2xl shadow-sm">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Notes & Terms
          </span>
          <p className="text-xs text-slate-700 whitespace-pre-wrap leading-relaxed">{quotation.notes}</p>
        </div>
      )}
    </div>
  )
}
