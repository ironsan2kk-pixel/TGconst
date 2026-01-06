import { useState, useEffect } from 'react'
import { Clock, XCircle } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog } from '../../components'
import { subscriptionsAPI } from '../../api/client'

export default function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedSub, setSelectedSub] = useState(null)
  const [isExtendOpen, setIsExtendOpen] = useState(false)
  const [isCancelOpen, setIsCancelOpen] = useState(false)
  const [extendDays, setExtendDays] = useState('30')

  useEffect(() => {
    loadSubscriptions()
  }, [])

  const loadSubscriptions = async () => {
    setLoading(true)
    try {
      const response = await subscriptionsAPI.getAll()
      const data = response.data.items || response.data; setSubscriptions(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error loading subscriptions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExtend = async () => {
    try {
      await subscriptionsAPI.extend(selectedSub.id, parseInt(extendDays))
      setIsExtendOpen(false)
      setExtendDays('30')
      loadSubscriptions()
    } catch (error) {
      console.error('Error extending subscription:', error)
    }
  }

  const handleCancel = async () => {
    try {
      await subscriptionsAPI.cancel(selectedSub.id)
      setIsCancelOpen(false)
      loadSubscriptions()
    } catch (error) {
      console.error('Error cancelling subscription:', error)
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Навсегда'
    return new Date(dateStr).toLocaleDateString('ru-RU')
  }

  const getStatusBadge = (sub) => {
    if (!sub.is_active) return <span className="badge-red">Отменена</span>
    if (sub.expires_at && new Date(sub.expires_at) < new Date()) {
      return <span className="badge-red">Истекла</span>
    }
    return <span className="badge-green">Активна</span>
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
      key: 'is_trial', 
      label: 'Тип',
      render: (value) => value ? (
        <span className="badge-yellow">Пробный</span>
      ) : (
        <span className="badge-blue">Оплачен</span>
      )
    },
    { 
      key: 'starts_at', 
      label: 'Начало',
      render: formatDate
    },
    { 
      key: 'expires_at', 
      label: 'Окончание',
      render: formatDate
    },
    { 
      key: 'status', 
      label: 'Статус',
      render: (_, row) => getStatusBadge(row)
    }
  ]

  const actions = [
    {
      icon: Clock,
      label: 'Продлить',
      onClick: (row) => {
        setSelectedSub(row)
        setIsExtendOpen(true)
      },
      show: (row) => row.is_active
    },
    {
      icon: XCircle,
      label: 'Отменить',
      onClick: (row) => {
        setSelectedSub(row)
        setIsCancelOpen(true)
      },
      className: 'text-red-600 hover:text-red-700',
      show: (row) => row.is_active
    }
  ]

  const activeCount = subscriptions.filter(s => s.is_active).length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Подписки</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Активных: {activeCount} из {subscriptions.length}
          </p>
        </div>
      </div>

      <DataTable
        data={subscriptions}
        columns={columns}
        actions={actions}
        loading={loading}
      />

      {/* Extend Modal */}
      <Modal
        isOpen={isExtendOpen}
        onClose={() => setIsExtendOpen(false)}
        title="Продлить подписку"
      >
        <div>
          <label className="label">Количество дней</label>
          <input
            type="number"
            value={extendDays}
            onChange={(e) => setExtendDays(e.target.value)}
            className="input"
            min="1"
          />
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => setIsExtendOpen(false)} className="btn-secondary">
            Отмена
          </button>
          <button onClick={handleExtend} className="btn-primary">
            Продлить
          </button>
        </div>
      </Modal>

      {/* Cancel Confirm */}
      <ConfirmDialog
        isOpen={isCancelOpen}
        onClose={() => setIsCancelOpen(false)}
        onConfirm={handleCancel}
        title="Отменить подписку"
        message="Вы уверены что хотите отменить эту подписку?"
        confirmText="Отменить"
        danger
      />
    </div>
  )
}
