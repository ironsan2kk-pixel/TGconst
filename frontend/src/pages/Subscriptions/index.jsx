import { useState, useEffect } from 'react'
import { Clock, XCircle, Plus } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog } from '../../components'

// Mock data
const mockSubscriptions = [
  { id: 1, user_name: 'Иван П.', tariff_name: 'Премиум', is_trial: false, starts_at: '2024-01-15', expires_at: '2024-02-15', is_active: true },
  { id: 2, user_name: 'Anna K.', tariff_name: 'VIP', is_trial: false, starts_at: '2024-01-20', expires_at: null, is_active: true },
  { id: 3, user_name: 'Сергей М.', tariff_name: 'Базовый', is_trial: true, starts_at: '2024-02-01', expires_at: '2024-02-04', is_active: false },
]

export default function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState(mockSubscriptions)
  const [loading, setLoading] = useState(false)
  const [extendModal, setExtendModal] = useState({ open: false, subscription: null })
  const [cancelDialog, setCancelDialog] = useState({ open: false, subscription: null })
  const [extendDays, setExtendDays] = useState(30)

  const handleExtend = async () => {
    try {
      setSubscriptions(subscriptions.map(s => {
        if (s.id === extendModal.subscription.id) {
          const currentExpires = s.expires_at ? new Date(s.expires_at) : new Date()
          currentExpires.setDate(currentExpires.getDate() + extendDays)
          return { ...s, expires_at: currentExpires.toISOString().split('T')[0], is_active: true }
        }
        return s
      }))
      setExtendModal({ open: false, subscription: null })
      setExtendDays(30)
    } catch (error) {
      console.error('Failed to extend:', error)
    }
  }

  const handleCancel = async () => {
    try {
      setSubscriptions(subscriptions.map(s => 
        s.id === cancelDialog.subscription.id ? { ...s, is_active: false } : s
      ))
      setCancelDialog({ open: false, subscription: null })
    } catch (error) {
      console.error('Failed to cancel:', error)
    }
  }

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'user_name', label: 'Пользователь' },
    { key: 'tariff_name', label: 'Тариф' },
    { 
      key: 'is_trial', 
      label: 'Тип',
      render: (val) => val ? (
        <span className="badge badge-warning">🎁 Пробный</span>
      ) : (
        <span className="badge badge-info">💳 Платный</span>
      )
    },
    { key: 'starts_at', label: 'Начало' },
    { 
      key: 'expires_at', 
      label: 'Окончание',
      render: (val) => val || '♾️ Навсегда'
    },
    { 
      key: 'is_active', 
      label: 'Статус',
      render: (val) => (
        <span className={`badge ${val ? 'badge-success' : 'badge-danger'}`}>
          {val ? 'Активна' : 'Истекла'}
        </span>
      )
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Подписки</h1>
          <p className="text-gray-500 dark:text-gray-400">
            Активных: {subscriptions.filter(s => s.is_active).length}
          </p>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={subscriptions}
        searchable={true}
        searchKeys={['user_name', 'tariff_name']}
        actions={(row) => (
          <>
            <button
              onClick={() => setExtendModal({ open: true, subscription: row })}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-blue-500"
              title="Продлить"
            >
              <Plus className="w-4 h-4" />
            </button>
            {row.is_active && (
              <button
                onClick={() => setCancelDialog({ open: true, subscription: row })}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-red-500"
                title="Отменить"
              >
                <XCircle className="w-4 h-4" />
              </button>
            )}
          </>
        )}
      />

      {/* Extend Modal */}
      <Modal
        isOpen={extendModal.open}
        onClose={() => setExtendModal({ open: false, subscription: null })}
        title="Продлить подписку"
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            Продлить подписку для {extendModal.subscription?.user_name}
          </p>
          <div>
            <label className="label">Количество дней</label>
            <input
              type="number"
              min="1"
              value={extendDays}
              onChange={(e) => setExtendDays(parseInt(e.target.value) || 0)}
              className="input"
            />
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <button onClick={() => setExtendModal({ open: false, subscription: null })} className="btn btn-secondary">
              Отмена
            </button>
            <button onClick={handleExtend} className="btn btn-primary">
              Продлить
            </button>
          </div>
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={cancelDialog.open}
        onClose={() => setCancelDialog({ open: false, subscription: null })}
        onConfirm={handleCancel}
        title="Отменить подписку"
        message="Вы уверены? Пользователь потеряет доступ к каналам."
      />
    </div>
  )
}
