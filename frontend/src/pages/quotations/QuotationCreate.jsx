import React, { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { subscriptionService } from '../../services/subscriptionService'
import { Plus, Trash2, ArrowLeft, Loader2, AlertCircle, Check } from 'lucide-react'

export default function QuotationCreate() {
  const navigate = useNavigate()
  const [customers, setCustomers] = useState([])
  const [catalog, setCatalog] = useState([])
  const [customerId, setCustomerId] = useState('')
  const [validUntil, setValidUntil] = useState('')
  const [notes, setNotes] = useState('')
  const [items, setItems] = useState([
    { product_id: '', variant_id: '', quantity: 1, unit_price: 0, subtotal: 0 },
  ])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const [custRes, catRes] = await Promise.all([
          subscriptionService.getCustomers(),
          subscriptionService.getCatalog(),
        ])
        setCustomers(custRes.data.data || [])
        setCatalog(catRes.data.data || [])
        if (custRes.data.data?.length > 0) {
          setCustomerId(custRes.data.data[0].id)
        }
      } catch (err) {
        setError('Failed to load initial customers or product catalog.')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const handleProductChange = (index, productId) => {
    const updated = [...items]
    const prod = catalog.find((c) => c.id === parseInt(productId))
    updated[index].product_id = productId
    updated[index].variant_id = ''
    if (prod) {
      const price = parseFloat(prod.sales_price)
      updated[index].unit_price = price
      updated[index].subtotal = price * updated[index].quantity
    } else {
      updated[index].unit_price = 0
      updated[index].subtotal = 0
    }
    setItems(updated)
  }

  const handleVariantChange = (index, variantId) => {
    const updated = [...items]
    updated[index].variant_id = variantId
    const prod = catalog.find((c) => c.id === parseInt(updated[index].product_id))
    if (prod) {
      if (variantId) {
        const v = prod.variants.find((vr) => vr.id === parseInt(variantId))
        const price = v ? parseFloat(v.final_price) : parseFloat(prod.sales_price)
        updated[index].unit_price = price
        updated[index].subtotal = price * updated[index].quantity
      } else {
        const price = parseFloat(prod.sales_price)
        updated[index].unit_price = price
        updated[index].subtotal = price * updated[index].quantity
      }
    }
    setItems(updated)
  }

  const handleQuantityChange = (index, qty) => {
    const updated = [...items]
    const q = Math.max(1, parseInt(qty) || 1)
    updated[index].quantity = q
    updated[index].subtotal = updated[index].unit_price * q
    setItems(updated)
  }

  const addItem = () => {
    setItems([...items, { product_id: '', variant_id: '', quantity: 1, unit_price: 0, subtotal: 0 }])
  }

  const removeItem = (index) => {
    if (items.length === 1) return
    setItems(items.filter((_, i) => i !== index))
  }

  const grandTotal = items.reduce((acc, curr) => acc + (curr.subtotal || 0), 0)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    const validItems = items.filter((i) => i.product_id)
    if (validItems.length === 0) {
      setError('Please select at least one product for the quotation.')
      return
    }

    try {
      setSubmitting(true)
      const payload = {
        customer_id: parseInt(customerId),
        valid_until: validUntil || null,
        notes: notes,
        items: validItems.map((i) => ({
          product_id: parseInt(i.product_id),
          variant_id: i.variant_id ? parseInt(i.variant_id) : null,
          quantity: i.quantity,
        })),
      }
      const res = await subscriptionService.createQuotation(payload)
      navigate(`/quotations/${res.data.data.id}`)
    } catch (err) {
      const msg = err.response?.data?.error
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg) || 'Failed to generate quotation.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="p-12 flex flex-col items-center justify-center text-slate-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
        <p className="text-xs">Loading form data...</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link
          to="/quotations"
          className="p-2 rounded-xl border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 transition"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Create Price Quotation</h2>
          <p className="text-xs text-slate-500">Configure products, select variants, and calculate customer terms.</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Customer & General Settings */}
        <div className="p-6 bg-white border border-slate-200/80 rounded-2xl shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider text-[11px] text-slate-400">
            Quotation Details
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Customer Recipient *
              </label>
              <select
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 text-xs bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 text-slate-800"
              >
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.email} (ID: {c.id})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Valid Until
              </label>
              <input
                type="date"
                value={validUntil}
                onChange={(e) => setValidUntil(e.target.value)}
                className="w-full px-3.5 py-2.5 text-xs bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 text-slate-800"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
              Internal & Customer Notes
            </label>
            <textarea
              rows={2}
              placeholder="e.g. Terms of billing, custom discount applied, special delivery clauses..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-3.5 py-2 text-xs bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 text-slate-800"
            />
          </div>
        </div>

        {/* Line Items Card */}
        <div className="p-6 bg-white border border-slate-200/80 rounded-2xl shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider text-[11px] text-slate-400">
              Quotation Line Items
            </h3>
            <button
              type="button"
              onClick={addItem}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-indigo-200 text-indigo-600 bg-indigo-50/50 hover:bg-indigo-100/70 text-xs font-semibold transition"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Product
            </button>
          </div>

          <div className="space-y-3">
            {items.map((item, idx) => {
              const selectedProduct = catalog.find((c) => c.id === parseInt(item.product_id))
              const variants = selectedProduct?.variants || []

              return (
                <div
                  key={idx}
                  className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 flex flex-col sm:flex-row gap-3 items-end sm:items-center"
                >
                  <div className="flex-1 w-full sm:w-auto">
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                      Product
                    </label>
                    <select
                      value={item.product_id}
                      onChange={(e) => handleProductChange(idx, e.target.value)}
                      required
                      className="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-lg text-slate-800"
                    >
                      <option value="">Select a product...</option>
                      {catalog.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name} (${parseFloat(p.sales_price).toFixed(2)})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex-1 w-full sm:w-auto">
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                      Variant (Optional)
                    </label>
                    <select
                      value={item.variant_id}
                      disabled={variants.length === 0}
                      onChange={(e) => handleVariantChange(idx, e.target.value)}
                      className="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-lg text-slate-800 disabled:opacity-50"
                    >
                      <option value="">None / Base Variant</option>
                      {variants.map((v) => (
                        <option key={v.id} value={v.id}>
                          {v.name} (+${parseFloat(v.additional_price).toFixed(2)})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="w-24">
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                      Qty
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) => handleQuantityChange(idx, e.target.value)}
                      className="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-lg text-slate-800"
                    />
                  </div>

                  <div className="w-28 text-right">
                    <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                      Subtotal
                    </span>
                    <span className="text-xs font-bold text-slate-800">
                      ${item.subtotal.toFixed(2)}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={() => removeItem(idx)}
                    disabled={items.length === 1}
                    className="p-2 text-slate-400 hover:text-red-600 disabled:opacity-30 transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              )
            })}
          </div>

          <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Estimated Total Amount
            </span>
            <span className="text-xl font-extrabold text-slate-900 tracking-tight">
              ${grandTotal.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-3">
          <Link
            to="/quotations"
            className="px-5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-700 text-xs font-semibold hover:bg-slate-50 transition"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-semibold shadow-md shadow-indigo-500/20 hover:bg-indigo-700 disabled:opacity-60 transition"
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating Quotation...
              </>
            ) : (
              <>
                <Check className="w-4 h-4" />
                Create Quotation
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
