import { useState, useEffect } from 'react'
import { Eye, CheckCircle, Plus, Download } from 'lucide-react'
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
      // Handle paginated response
      const paymentsData = paymentsRes.data.items || paymentsRes.data
      const usersData = usersRes.data.items || usersRes.data
      const tariffsData = tariffsRes.data.items || tariffsRes.data
      setPayments(Array.isArray(paymentsData) ? paymentsData : [])
      setUsers(Array.isArray(usersData) ? usersData : [])
      setTariffs(Array.isArray(tariffsData) ? tariffsData : [])
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

  const getUserName = (userId) => {
    const user = users.find(u => u.id === userId)
    return user ? (user.username ? `@${user.username}` : user.first_name || `ID: ${user.telegram_id}`) : `User #${userId}`
  }

  const getTariffName = (tariffId) => {
    const tariff = tariffs.find(t => t.id === tariffId)
    return tariff ? tariff.name_ru : `Tariff #${tariffId}`
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
      manual: 'Ручной'
    }
    return <span className={styles[status] || 'badge-gray'}>{labels[status] || status}</span>
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleString('ru-RU')
  }

  const totalRevenue = payments
    .filter(p => p.status === 'paid' || p.status === 'manual')
    .reduce((sum, p) => sum + (p.amount || 0), 0)

  const columns = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'user_id', label: 'Пользователь', render: getUserName },
    { key: 'tariff_id', label: 'Тариф', render: getTariffName },
    { key: 'amount', label: 'Сумма', sortable: true, render: (v) => `$${v?.toFixed(2) || '0.00'}` },
    { key: 'status', label: 'Статус', render: getStatusBadge },
    { key: 'payment_method', label: 'Метод', render: (v) => v === 'manual' ? '✋ Ручной' : '🤖 CryptoBot' },
    { key: 'created_at', label: 'Создан', render: formatDate }
  ]

  const actions = [
    { icon: Eye, label: 'Просмотр', onClick: (row) => { setSelectedPayment(row); setIsViewOpen(true) } },
    { 
      icon: CheckCircle, 
      label: 'Подтвердить', 
      onClick: handleConfirm,
      className: 'text-green-600 hover:text-green-700',
      show: (row) => row.status === 'pending'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Платежи</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Всего: {payments.length} | Доход: ${totalRevenue.toFixed(2)}
          </p>
        </div>
        <div className="flex gap-2">
          <ExportButton data={payments} filename="payments" columns={['id', 'user_id', 'tariff_id', 'amount', 'status', 'payment_method', 'created_at']} />
          <button onClick={() => setIsCreateOpen(true)} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" /> Ручной платёж
          </button>
        </div>
      </div>

      <DataTable data={payments} columns={columns} actions={actions} loading={loading} searchKeys={['id', 'invoice_id']} />

      {/* View Modal */}
      <Modal isOpen={isViewOpen} onClose={() => setIsViewOpen(false)} title="Детали платежа">
        {selectedPayment && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-gray-500">ID:</span> <span className="ml-2 font-medium">{selectedPayment.id}</span></div>
              <div><span className="text-gray-500">Invoice ID:</span> <span className="ml-2 font-mono">{selectedPayment.invoice_id || '—'}</span></div>
              <div><span className="text-gray-500">Пользователь:</span> <span className="ml-2">{getUserName(selectedPayment.user_id)}</span></div>
              <div><span className="text-gray-500">Тариф:</span> <span className="ml-2">{getTariffName(selectedPayment.tariff_id)}</span></div>
              <div><span className="text-gray-500">Сумма:</span> <span className="ml-2 font-medium">${selectedPayment.amount?.toFixed(2)}</span></div>
              <div><span className="text-gray-500">Статус:</span> <span className="ml-2">{getStatusBadge(selectedPayment.status)}</span></div>
              <div><span className="text-gray-500">Метод:</span> <span className="ml-2">{selectedPayment.payment_method}</span></div>
              <div><span className="text-gray-500">Создан:</span> <span className="ml-2">{formatDate(selectedPayment.created_at)}</span></div>
              {selectedPayment.paid_at && <div><span className="text-gray-500">Оплачен:</span> <span className="ml-2">{formatDate(selectedPayment.paid_at)}</span></div>}
            </div>
          </div>
        )}
      </Modal>

      {/* Create Manual Payment Modal */}
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Ручной платёж">
        <div className="space-y-4">
          <div>
            <label className="label">Пользователь</label>
            <select value={createData.user_id} onChange={(e) => setCreateData({ ...createData, user_id: e.target.value })} className="input">
              <option value="">Выберите пользователя</option>
              {users.map(u => (<option key={u.id} value={u.id}>{u.username ? `@${u.username}` : u.first_name} (ID: {u.telegram_id})</option>))}
            </select>
          </div>
          <div>
            <label className="label">Тариф</label>
            <select value={createData.tariff_id} onChange={(e) => setCreateData({ ...createData, tariff_id: e.target.value, amount: tariffs.find(t => t.id === parseInt(e.target.value))?.price || '' })} className="input">
              <option value="">Выберите тариф</option>
              {tariffs.map(t => (<option key={t.id} value={t.id}>{t.name_ru} (${t.price})</option>))}
            </select>
          </div>
          <div>
            <label className="label">Сумма (USDT)</label>
            <input type="number" step="0.01" value={createData.amount} onChange={(e) => setCreateData({ ...createData, amount: e.target.value })} className="input" />
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => setIsCreateOpen(false)} className="btn-secondary">Отмена</button>
          <button onClick={handleCreateManual} className="btn-primary" disabled={!createData.user_id || !createData.tariff_id || !createData.amount}>Создать</button>
        </div>
      </Modal>
    </div>
  )
}
