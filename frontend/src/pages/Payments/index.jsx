import { useState, useEffect } from 'react'
import { Check, X, Eye, Plus, Download } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog, ExportButton, downloadBlob } from '../../components'

// Mock data
const mockPayments = [
  { id: 1, user_name: 'Иван П.', tariff_name: 'Премиум', amount: 25, original_amount: 25, status: 'paid', payment_method: 'cryptobot', created_at: '2024-01-15 12:30' },
  { id: 2, user_name: 'Anna K.', tariff_name: 'VIP', amount: 99, original_amount: 99, status: 'paid', payment_method: 'cryptobot', created_at: '2024-01-20 14:45' },
  { id: 3, user_name: 'Сергей М.', tariff_name: 'Базовый', amount: 10, original_amount: 10, status: 'pending', payment_method: 'cryptobot', invoice_id: 'INV123', created_at: '2024-02-01 09:15' },
  { id: 4, user_name: 'Maria L.', tariff_name: 'Премиум', amount: 20, original_amount: 25, status: 'paid', payment_method: 'manual', promocode: 'SAVE20', created_at: '2024-02-05 16:00' },
]

const mockTariffs = [
  { id: 1, name_ru: 'Базовый', price: 10 },
  { id: 2, name_ru: 'Премиум', price: 25 },
  { id: 3, name_ru: 'VIP', price: 99 },
]

const mockUsers = [
  { id: 1, name: 'Иван П.', telegram_id: 123456789 },
  { id: 2, name: 'Anna K.', telegram_id: 987654321 },
]

export default function Payments() {
  const [payments, setPayments] = useState(mockPayments)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)
  
  const [viewModal, setViewModal] = useState({ open: false, payment: null })
  const [manualModal, setManualModal] = useState(false)
  const [confirmDialog, setConfirmDialog] = useState({ open: false, payment: null })
  
  const [manualForm, setManualForm] = useState({
    user_id: '',
    tariff_id: '',
    amount: ''
  })

  const handleConfirmPayment = async () => {
    try {
      setPayments(payments.map(p => 
        p.id === confirmDialog.payment.id 
          ? { ...p, status: 'paid', payment_method: 'manual' } 
          : p
      ))
      setConfirmDialog({ open: false, payment: null })
    } catch (error) {
      console.error('Failed to confirm:', error)
    }
  }

  const handleCreateManual = async (e) => {
    e.preventDefault()
    try {
      const newPayment = {
        id: Date.now(),
        user_name: mockUsers.find(u => u.id === parseInt(manualForm.user_id))?.name || 'Unknown',
        tariff_name: mockTariffs.find(t => t.id === parseInt(manualForm.tariff_id))?.name_ru || 'Unknown',
        amount: parseFloat(manualForm.amount),
        original_amount: parseFloat(manualForm.amount),
        status: 'paid',
        payment_method: 'manual',
        created_at: new Date().toLocaleString('ru-RU')
      }
      setPayments([newPayment, ...payments])
      setManualModal(false)
      setManualForm({ user_id: '', tariff_id: '', amount: '' })
    } catch (error) {
      console.error('Failed to create manual payment:', error)
    }
  }

  const handleExport = async () => {
    try {
      setExporting(true)
      const csv = 'id,user,tariff,amount,status,method,date\n' + 
        payments.map(p => `${p.id},"${p.user_name}","${p.tariff_name}",${p.amount},${p.status},${p.payment_method},"${p.created_at}"`).join('\n')
      const blob = new Blob([csv], { type: 'text/csv' })
      downloadBlob(blob, 'payments.csv')
    } catch (error) {
      console.error('Failed to export:', error)
    } finally {
      setExporting(false)
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'paid': return <span className="badge badge-success">✓ Оплачен</span>
      case 'pending': return <span className="badge badge-warning">⏳ Ожидает</span>
      case 'expired': return <span className="badge badge-danger">✗ Истёк</span>
      case 'cancelled': return <span className="badge badge-danger">✗ Отменён</span>
      default: return <span className="badge badge-info">{status}</span>
    }
  }

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'user_name', label: 'Пользователь' },
    { key: 'tariff_name', label: 'Тариф' },
    { 
      key: 'amount', 
      label: 'Сумма',
      render: (val, row) => (
        <span>
          ${val}
          {row.original_amount !== val && (
            <span className="text-xs text-gray-500 line-through ml-1">${row.original_amount}</span>
          )}
        </span>
      )
    },
    { 
      key: 'status', 
      label: 'Статус',
      render: (val) => getStatusBadge(val)
    },
    { 
      key: 'payment_method', 
      label: 'Метод',
      render: (val) => val === 'cryptobot' ? '🤖 CryptoBot' : '✋ Вручную'
    },
    { key: 'created_at', label: 'Дата' }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Платежи</h1>
          <p className="text-gray-500 dark:text-gray-400">
            Всего: ${payments.filter(p => p.status === 'paid').reduce((sum, p) => sum + p.amount, 0).toFixed(2)}
          </p>
        </div>
        <div className="flex gap-3">
          <ExportButton onClick={handleExport} loading={exporting} />
          <button onClick={() => setManualModal(true)} className="btn btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Создать вручную
          </button>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={payments}
        searchable={true}
        searchKeys={['user_name', 'tariff_name']}
        actions={(row) => (
          <>
            <button
              onClick={() => setViewModal({ open: true, payment: row })}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"
              title="Подробнее"
            >
              <Eye className="w-4 h-4" />
            </button>
            {row.status === 'pending' && (
              <button
                onClick={() => setConfirmDialog({ open: true, payment: row })}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-green-500"
                title="Подтвердить оплату"
              >
                <Check className="w-4 h-4" />
              </button>
            )}
          </>
        )}
      />

      {/* View Modal */}
      <Modal
        isOpen={viewModal.open}
        onClose={() => setViewModal({ open: false, payment: null })}
        title="Детали платежа"
      >
        {viewModal.payment && (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">ID платежа</p>
                <p className="font-medium">{viewModal.payment.id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Статус</p>
                {getStatusBadge(viewModal.payment.status)}
              </div>
              <div>
                <p className="text-sm text-gray-500">Пользователь</p>
                <p className="font-medium">{viewModal.payment.user_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Тариф</p>
                <p className="font-medium">{viewModal.payment.tariff_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Сумма</p>
                <p className="font-medium">${viewModal.payment.amount}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Метод</p>
                <p className="font-medium">{viewModal.payment.payment_method}</p>
              </div>
              {viewModal.payment.invoice_id && (
                <div className="col-span-2">
                  <p className="text-sm text-gray-500">Invoice ID</p>
                  <code className="text-sm bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                    {viewModal.payment.invoice_id}
                  </code>
                </div>
              )}
              {viewModal.payment.promocode && (
                <div>
                  <p className="text-sm text-gray-500">Промокод</p>
                  <p className="font-medium">{viewModal.payment.promocode}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Manual Payment Modal */}
      <Modal
        isOpen={manualModal}
        onClose={() => setManualModal(false)}
        title="Создать платёж вручную"
      >
        <form onSubmit={handleCreateManual} className="space-y-4">
          <div>
            <label className="label">Пользователь</label>
            <select
              value={manualForm.user_id}
              onChange={(e) => setManualForm({ ...manualForm, user_id: e.target.value })}
              className="input"
              required
            >
              <option value="">Выберите пользователя...</option>
              {mockUsers.map(u => (
                <option key={u.id} value={u.id}>{u.name}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="label">Тариф</label>
            <select
              value={manualForm.tariff_id}
              onChange={(e) => {
                const tariff = mockTariffs.find(t => t.id === parseInt(e.target.value))
                setManualForm({ 
                  ...manualForm, 
                  tariff_id: e.target.value,
                  amount: tariff?.price.toString() || ''
                })
              }}
              className="input"
              required
            >
              <option value="">Выберите тариф...</option>
              {mockTariffs.map(t => (
                <option key={t.id} value={t.id}>{t.name_ru} (${t.price})</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="label">Сумма (USDT)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={manualForm.amount}
              onChange={(e) => setManualForm({ ...manualForm, amount: e.target.value })}
              className="input"
              required
            />
          </div>
          
          <div className="flex justify-end gap-3 pt-4">
            <button type="button" onClick={() => setManualModal(false)} className="btn btn-secondary">
              Отмена
            </button>
            <button type="submit" className="btn btn-success">
              Создать и активировать
            </button>
          </div>
        </form>
      </Modal>

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={confirmDialog.open}
        onClose={() => setConfirmDialog({ open: false, payment: null })}
        onConfirm={handleConfirmPayment}
        title="Подтвердить оплату"
        message={`Подтвердить оплату $${confirmDialog.payment?.amount} от ${confirmDialog.payment?.user_name}?`}
        variant="success"
        confirmText="Подтвердить"
      />
    </div>
  )
}
