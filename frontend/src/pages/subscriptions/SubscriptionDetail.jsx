import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { subscriptionService } from '../../services/subscriptionService'
import { useAuth } from '../../context/AuthContext'
import StatusBadge from '../../components/StatusBadge'
import {
  ArrowLeft,
  PauseCircle,
  PlayCircle,
  RefreshCw,
  XCircle,
  Loader2,
  AlertCircle,
  CheckCircle,
  Layers,
  Calendar,
  User,
  Clock,
  FileText,
} from 'lucide-react'

export default function SubscriptionDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const [subscription, setSubscription] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  const isStaffOrAdmin = user?.role === 'admin' || user?.role === 'staff'

  const fetchDetail = async () => {
    try {
      setLoading(true)
      const res = await subscriptionService.getSubscription(id)
      setSubscription(res.data.data)
    } catch (err) {
      setError('Failed to fetch subscription details.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDetail()
  }, [id])

  const handleAction = async (actionFn, successText) => {
    try {
      setActionLoading(true)
      setError('')
      setSuccessMsg('')
      const res = await actionFn(id)
      setSubscription(res.data.data)
      setSuccessMsg(successText)
    } catch (err) {
      setError(err.response?.data?.error || 'Operation failed.')
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="p-12 flex flex-col items-center justify-center text-slate-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
        <p className="text-xs">Loading subscription details...</p>
      </div>
    )
  }

  if (!subscription) {
    return (
      <div className="p-8 text-center text-slate-500">
        <p>Subscription not found.</p>
        <Link to="/subscriptions" className="text-indigo-600 font-semibold text-xs mt-2 inline-block">
          Return to list
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/subscriptions"
            className="p-2 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                {subscription.subscription_number}
              </h2>
              <StatusBadge status={subscription.status} />
            </div>
            <p className="text-xs text-slate-500">Active contract for {subscription.customer_email}</p>
          </div>
        </div>

        {/* Action Controls (Pause, Resume, Renew, Close) */}
        {isStaffOrAdmin && (
          <div className="flex flex-wrap items-center gap-2">
            {subscription.status === 'active' && (
              <button
                onClick={() =>
                  handleAction(subscriptionService.pauseSubscription, 'Subscription successfully paused.')
                }
                disabled={actionLoading}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-amber-200 text-amber-700 bg-amber-50 hover:bg-amber-100/80 text-xs font-semibold transition"
              >
                <PauseCircle className="w-3.5 h-3.5" />
                Pause
              </button>
            )}

            {subscription.status === 'paused' && (
              <button
                onClick={() =>
                  handleAction(subscriptionService.resumeSubscription, 'Subscription resumed to active.')
                }
                disabled={actionLoading}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-emerald-200 text-emerald-700 bg-emerald-50 hover:bg-emerald-100/80 text-xs font-semibold transition"
              >
                <PlayCircle className="w-3.5 h-3.5" />
                Resume
              </button>
            )}

            {subscription.status !== 'cancelled' && (
              <button
                onClick={() =>
                  handleAction(
                    subscriptionService.renewSubscription,
                    'Billing period extended and subscription renewed!'
                  )
                }
                disabled={actionLoading}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-indigo-200 text-indigo-700 bg-indigo-50 hover:bg-indigo-100/80 text-xs font-semibold transition"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Renew Cycle
              </button>
            )}

            {subscription.status !== 'cancelled' && (
              <button
                onClick={() =>
                  handleAction(
                    subscriptionService.closeSubscription,
                    'Subscription terminated and closed.'
                  )
                }
                disabled={actionLoading}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-rose-200 text-rose-700 bg-rose-50 hover:bg-rose-100/80 text-xs font-semibold transition"
              >
                <XCircle className="w-3.5 h-3.5" />
                Close / Cancel
              </button>
            )}
          </div>
        )}
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

      {/* Meta Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-sm">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <User className="w-3.5 h-3.5" /> Client
          </span>
          <p className="text-xs font-bold text-slate-900 mt-1 truncate">{subscription.customer_email}</p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-sm">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" /> Billing Cycle
          </span>
          <p className="text-xs font-bold capitalize text-slate-900 mt-1">{subscription.billing_interval}</p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-sm">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5" /> Next Billing
          </span>
          <p className="text-xs font-bold text-indigo-700 mt-1">{subscription.next_billing_date}</p>
        </div>

        <div className="p-4 bg-white border border-slate-200/80 rounded-2xl shadow-sm">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5" /> Recurring Rate
          </span>
          <p className="text-sm font-extrabold text-slate-900 mt-1">
            ${parseFloat(subscription.contracted_price).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Product Details Card */}
      <div className="p-6 bg-white border border-slate-200/80 rounded-2xl shadow-sm space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Subscribed Offering & License Details
        </h3>
        <div className="flex items-start justify-between border-b border-slate-100 pb-4">
          <div>
            <h4 className="text-base font-bold text-slate-900">{subscription.product_name}</h4>
            {subscription.variant_name ? (
              <span className="inline-block px-2.5 py-0.5 mt-1 rounded bg-indigo-50 border border-indigo-200/60 text-indigo-700 text-xs font-semibold">
                Edition: {subscription.variant_name}
              </span>
            ) : (
              <span className="text-xs text-slate-400 block mt-1">Standard Base Tier</span>
            )}
          </div>
          {subscription.quotation_number && (
            <Link
              to={`/quotations/${subscription.quotation}`}
              className="inline-flex items-center gap-1 text-xs text-indigo-600 font-semibold hover:underline"
            >
              <FileText className="w-3.5 h-3.5" />
              Source Quote: {subscription.quotation_number}
            </Link>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-slate-400 block text-[10px] font-bold uppercase">Contract Start Date</span>
            <span className="font-semibold text-slate-800">{subscription.start_date}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] font-bold uppercase">Last Renewal / Update</span>
            <span className="font-semibold text-slate-800">{new Date(subscription.updated_at).toLocaleString()}</span>
          </div>
        </div>

        {subscription.notes && (
          <div className="pt-3 border-t border-slate-100">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Operational Notes
            </span>
            <p className="text-xs text-slate-600 leading-relaxed">{subscription.notes}</p>
          </div>
        )}
      </div>
    </div>
  )
}
