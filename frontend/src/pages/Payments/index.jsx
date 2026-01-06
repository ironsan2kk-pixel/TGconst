import { useState, useEffect } from 'react'
import { Eye, CheckCircle, Plus } from 'lucide-react'
import { DataTable, Modal, ExportButton } from '../../components'
import { paymentsAPI, usersAPI, tariffsAPI } from '../../api/client'

export default function Payments() {
  const [payments, setPayments] = useState([])
  const [users, setUsers] = useState([])
  const [tariffs, setTariffs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedPayment, setSelectedPayment] = useState(null)
  const [isViewOpen, setIsViewOpen] = useState(false)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [createData, setCreateData] = useState({ user_id: '', tariff_id: '', amount: '' })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [paymentsRes, usersRes, tariffsRes] = await Promise.all([
        paymentsAPI.getAll(),
        usersAPI.getAll(),
        tariffsAPI.getAll()
      ])
      setPayments(paymentsRes.data)
      setUsers(usersRes.data)
      setTariffs(tariffsRes.data)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = async (payment) => {
    try {
      await paymentsAPI.confirm(payment.id)
      loadData()
    } catch (error) {
      console.error('Error confirming payment:', error)
    }
  }

  const handleCreateManual = async () => {
    try {
      await paymentsAPI.createManual({
        user_id: parseInt(createData.user_id),
        tariff_id: parseInt(createData.tariff_id),
        amount: parseFloat(createData.amount)
      })
      setIsCreateOpen(false)
      setCreateData({ user_id: '', tariff_id: '', amount: '' })
      loadData()
    } catch (error) {
      console.error('Error creating payment:', error)
    }
  }

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'badge-yellow',
      paid: 'badge-green',
      expired: 'badge-red',
      cancelled: 'badge-red',
      manual: 'badge-blue'
    }
    const labels = {
      pending: 'Ожидает',
      paid: 'Оплачен',
      expired: 'Истёк',
      cancelled: 'Отменён',
      manual: 'Вручную'
    }
    return <span className={styles[status]}>{labels[status]}</span>
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleString('ru-RU')
  }

  const columns = [
    { key: 'id', label: 'ID', sortable: true },
    { 
      key: 'user', 
      label: 'Пользователь',
      render: (_, row) => row.user?.username ? `@${row.user.username}` : row.user?.first_name || `ID: ${row.user_id}`
    },
    { 
      key: 'tariff', 
      label: 'Тариф',
      render: (_, row) => row.tariff?.name_ru || `ID: ${row.tariff_id}`
    },
    { 
      key: 'amount', 
      label: 'Сумма',
      sortable: true,
      render: (value, row) => (
        <span>
          {row.original_amount && row.original_amount !== value && (
            <span className="text-gray-400 line-through mr-1">${row.original_amount}</span>
          )}
          <span className="font-medium">${value}</span>
        </span>
      )
    },
    { 
      key: 'status', 
      label: 'Статус',
      render: (value) => getStatusBadge(value)
    },
    { 
      key: 'payment_method', 
      label: 'Метод',
      render: (value) => value === 'cryptobot' ? '💰 CryptoBot' : '✋ Вручную'
    },
    { 
      key: 'created_at', 
      label: 'Дата',
      render: formatDate
    }
  ]

  const actions = [
    {
      icon: Eye,
      label: 'Детали',
      onClick: (row) => {
        setSelectedPayment(row)
        setIsViewOpen(true)
      }
    },
    {
      icon: CheckCircle,
      label: 'Подтвердить',
      onClick: handleConfirm,
      className: 'text-green-600 hover:text-green-700',
      show: (row) => row.status === 'pending'
    }
  ]

  const totalRevenue = payments
    .filter(p => p.status === 'paid' || p.status === 'manual')
    .reduce((sum, p) => sum + p.amount, 0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Платежи</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Всего: {payments.length} | Выручка: ${totalRevenue.toFixed(2)}
          </p>
        </div>
        <div className="flex gap-2">
          <ExportButton
            data={payments}
            filename="payments"
            columns={['id', 'user_id', 'tariff_id', 'amount', 'status', 'payment_method', 'created_at']}
          />
          <button onClick={() => setIsCreateOpen(true)} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Создать вручную
          </button>
        </div>
      </div>

      <DataTable
        data={payments}
        columns={columns}
        actions={actions}
        loading={loading}
      />

      {/* View Modal */}
      <Modal
        isOpen={isViewOpen}
        onClose={() => setIsViewOpen(false)}
        title="Детали платежа"
      >
        {selectedPayment && (
          <div className="space-y-3 text-sm">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-gray-500">ID:</span>
                <span className="ml-2 font-medium">{selectedPayment.id}</span>
              </div>
              <div>
                <span className="text-gray-500">Статус:</span>
                <span className="ml-2">{getStatusBadge(selectedPayment.status)}</span>
              </div>
              <div>
                <span className="text-gray-500">Сумма:</span>
                <span className="ml-2 font-medium">${selectedPayment.amount}</span>
              </div>
              <div>
                <span className="text-gray-500">Метод:</span>
                <span className="ml-2">{selectedPayment.payment_method}</span>
              </div>
              {selectedPayment.invoice_id && (
                <div className="col-span-2">
                  <span className="text-gray-500">Invoice ID:</span>
                  <span className="ml-2 font-mono text-xs">{selectedPayment.invoice_id}</span>
                </div>
              )}
              {selectedPayment.promocode_id && (
                <div className="col-span-2">
                  <span className="text-gray-500">Промокод:</span>
                  <span className="ml-2">ID: {selectedPayment.promocode_id}</span>
                </div>
              )}
              <div>
                <span className="text-gray-500">Создан:</span>
                <span className="ml-2">{formatDate(selectedPayment.created_at)}</span>
              </div>
              <div>
                <span className="text-gray-500">Оплачен:</span>
                <span className="ml-2">{formatDate(selectedPayment.paid_at)}</span>
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Create Manual Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Создать платёж вручную"
      >
        <div className="space-y-4">
          <div>
            <label className="label">Пользователь</label>
            <select
              value={createData.user_id}
              onChange={(e) => setCreateData({ ...createData, user_id: e.target.value })}
              className="input"
            >
              <option value="">Выберите пользователя</option>
              {users.map(u => (
                <option key={u.id} value={u.id}>
                  {u.username ? `@${u.username}` : u.first_name} (ID: {u.telegram_id})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Тариф</label>
            <select
              value={createData.tariff_id}
              onChange={(e) => {
                const tariff = tariffs.find(t => t.id === parseInt(e.target.value))
                setCreateData({ 
                  ...createData, 
                  tariff_id: e.target.value,
                  amount: tariff ? tariff.price.toString() : ''
                })
              }}
              className="input"
            >
              <option value="">Выберите тариф</option>
              {tariffs.map(t => (
                <option key={t.id} value={t.id}>{t.name_ru} (${t.price})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Сумма (USDT)</label>
            <input
              type="number"
              step="0.01"
              value={createData.amount}
              onChange={(e) => setCreateData({ ...createData, amount: e.target.value })}
              className="input"
            />
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => setIsCreateOpen(false)} className="btn-secondary">Отмена</button>
          <button 
            onClick={handleCreateManual} 
            className="btn-primary"
            disabled={!createData.user_id || !createData.tariff_id || !createData.amount}
          >
            Создать
          </button>
        </div>
      </Modal>
    </div>
  )
}
