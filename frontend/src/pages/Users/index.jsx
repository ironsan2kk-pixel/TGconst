import { useState, useEffect } from 'react'
import { Search, UserPlus, Ban, UserCheck, Eye, Download } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog, ExportButton, downloadBlob } from '../../components'
import { usersAPI, tariffsAPI } from '../../api/client'

// Mock data
const mockUsers = [
  { id: 1, telegram_id: 123456789, username: 'ivan_p', first_name: 'Иван', language: 'ru', is_banned: false, has_subscription: true, created_at: '2024-01-15' },
  { id: 2, telegram_id: 987654321, username: 'anna_k', first_name: 'Anna', language: 'en', is_banned: false, has_subscription: true, created_at: '2024-01-20' },
  { id: 3, telegram_id: 456789123, username: 'sergey_m', first_name: 'Сергей', language: 'ru', is_banned: true, ban_reason: 'Спам', has_subscription: false, created_at: '2024-02-01' },
  { id: 4, telegram_id: 789123456, username: null, first_name: 'Maria', language: 'en', is_banned: false, has_subscription: false, created_at: '2024-02-10' },
]

const mockTariffs = [
  { id: 1, name_ru: 'Базовый', price: 10 },
  { id: 2, name_ru: 'Премиум', price: 25 },
  { id: 3, name_ru: 'VIP', price: 99 },
]

export default function Users() {
  const [users, setUsers] = useState(mockUsers)
  const [tariffs, setTariffs] = useState(mockTariffs)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)
  
  // Modals
  const [grantModal, setGrantModal] = useState({ open: false, user: null })
  const [banModal, setBanModal] = useState({ open: false, user: null })
  const [viewModal, setViewModal] = useState({ open: false, user: null })
  const [confirmDialog, setConfirmDialog] = useState({ open: false, action: null, user: null })
  
  // Forms
  const [grantForm, setGrantForm] = useState({ tariff_id: '', days: 30 })
  const [banReason, setBanReason] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      // const [usersRes, tariffsRes] = await Promise.all([
      //   usersAPI.getAll(),
      //   tariffsAPI.getAll()
      // ])
      // setUsers(usersRes.data)
      // setTariffs(tariffsRes.data)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGrantAccess = async () => {
    try {
      // await usersAPI.grantAccess(grantModal.user.id, grantForm)
      setUsers(users.map(u => 
        u.id === grantModal.user.id ? { ...u, has_subscription: true } : u
      ))
      setGrantModal({ open: false, user: null })
      setGrantForm({ tariff_id: '', days: 30 })
    } catch (error) {
      console.error('Failed to grant access:', error)
    }
  }

  const handleRevokeAccess = async () => {
    try {
      // await usersAPI.revokeAccess(confirmDialog.user.id)
      setUsers(users.map(u => 
        u.id === confirmDialog.user.id ? { ...u, has_subscription: false } : u
      ))
      setConfirmDialog({ open: false, action: null, user: null })
    } catch (error) {
      console.error('Failed to revoke access:', error)
    }
  }

  const handleBan = async () => {
    try {
      // await usersAPI.ban(banModal.user.id, banReason)
      setUsers(users.map(u => 
        u.id === banModal.user.id ? { ...u, is_banned: true, ban_reason: banReason } : u
      ))
      setBanModal({ open: false, user: null })
      setBanReason('')
    } catch (error) {
      console.error('Failed to ban user:', error)
    }
  }

  const handleUnban = async () => {
    try {
      // await usersAPI.unban(confirmDialog.user.id)
      setUsers(users.map(u => 
        u.id === confirmDialog.user.id ? { ...u, is_banned: false, ban_reason: null } : u
      ))
      setConfirmDialog({ open: false, action: null, user: null })
    } catch (error) {
      console.error('Failed to unban user:', error)
    }
  }

  const handleExport = async () => {
    try {
      setExporting(true)
      // const response = await usersAPI.export('csv')
      // downloadBlob(response.data, 'users.csv')
      
      // Mock export
      const csv = 'id,telegram_id,username,first_name\n' + 
        users.map(u => `${u.id},${u.telegram_id},${u.username || ''},${u.first_name}`).join('\n')
      const blob = new Blob([csv], { type: 'text/csv' })
      downloadBlob(blob, 'users.csv')
    } catch (error) {
      console.error('Failed to export:', error)
    } finally {
      setExporting(false)
    }
  }

  const columns = [
    { key: 'id', label: 'ID' },
    { 
      key: 'telegram_id', 
      label: 'Telegram ID',
      render: (val) => <code className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{val}</code>
    },
    { 
      key: 'username', 
      label: 'Username',
      render: (val, row) => val ? `@${val}` : row.first_name
    },
    { 
      key: 'language', 
      label: 'Язык',
      render: (val) => val?.toUpperCase() || '-'
    },
    { 
      key: 'has_subscription', 
      label: 'Подписка',
      render: (val) => (
        <span className={`badge ${val ? 'badge-success' : 'badge-info'}`}>
          {val ? '👑 Активна' : 'Нет'}
        </span>
      )
    },
    { 
      key: 'is_banned', 
      label: 'Статус',
      render: (val, row) => val ? (
        <span className="badge badge-danger" title={row.ban_reason}>🚫 Забанен</span>
      ) : (
        <span className="badge badge-success">✓ Активен</span>
      )
    },
    { key: 'created_at', label: 'Регистрация' }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Пользователи</h1>
          <p className="text-gray-500 dark:text-gray-400">
            Всего: {users.length} | С подпиской: {users.filter(u => u.has_subscription).length}
          </p>
        </div>
        <ExportButton onClick={handleExport} loading={exporting} />
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        data={users}
        searchable={true}
        searchKeys={['username', 'first_name', 'telegram_id']}
        actions={(row) => (
          <>
            <button
              onClick={() => setViewModal({ open: true, user: row })}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"
              title="Подробнее"
            >
              <Eye className="w-4 h-4" />
            </button>
            
            {!row.has_subscription ? (
              <button
                onClick={() => setGrantModal({ open: true, user: row })}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-green-500"
                title="Выдать доступ"
              >
                <UserPlus className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={() => setConfirmDialog({ open: true, action: 'revoke', user: row })}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-yellow-500"
                title="Забрать доступ"
              >
                <UserCheck className="w-4 h-4" />
              </button>
            )}
            
            {!row.is_banned ? (
              <button
                onClick={() => setBanModal({ open: true, user: row })}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-red-500"
                title="Забанить"
              >
                <Ban className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={() => setConfirmDialog({ open: true, action: 'unban', user: row })}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-green-500"
                title="Разбанить"
              >
                <UserCheck className="w-4 h-4" />
              </button>
            )}
          </>
        )}
      />

      {/* Grant Access Modal */}
      <Modal
        isOpen={grantModal.open}
        onClose={() => setGrantModal({ open: false, user: null })}
        title={`Выдать доступ: ${grantModal.user?.username || grantModal.user?.first_name}`}
      >
        <div className="space-y-4">
          <div>
            <label className="label">Тариф</label>
            <select
              value={grantForm.tariff_id}
              onChange={(e) => setGrantForm({ ...grantForm, tariff_id: e.target.value })}
              className="input"
              required
            >
              <option value="">Выберите тариф...</option>
              {tariffs.map(t => (
                <option key={t.id} value={t.id}>{t.name_ru} (${t.price})</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="label">Срок (дней)</label>
            <input
              type="number"
              min="0"
              value={grantForm.days}
              onChange={(e) => setGrantForm({ ...grantForm, days: parseInt(e.target.value) || 0 })}
              className="input"
            />
            <p className="text-xs text-gray-500 mt-1">0 = навсегда</p>
          </div>
          
          <div className="flex justify-end gap-3 pt-4">
            <button onClick={() => setGrantModal({ open: false, user: null })} className="btn btn-secondary">
              Отмена
            </button>
            <button onClick={handleGrantAccess} className="btn btn-success">
              Выдать доступ
            </button>
          </div>
        </div>
      </Modal>

      {/* Ban Modal */}
      <Modal
        isOpen={banModal.open}
        onClose={() => setBanModal({ open: false, user: null })}
        title={`Забанить: ${banModal.user?.username || banModal.user?.first_name}`}
      >
        <div className="space-y-4">
          <div>
            <label className="label">Причина бана</label>
            <textarea
              value={banReason}
              onChange={(e) => setBanReason(e.target.value)}
              placeholder="Укажите причину..."
              className="input"
              rows={3}
            />
          </div>
          
          <div className="flex justify-end gap-3 pt-4">
            <button onClick={() => setBanModal({ open: false, user: null })} className="btn btn-secondary">
              Отмена
            </button>
            <button onClick={handleBan} className="btn btn-danger">
              Забанить
            </button>
          </div>
        </div>
      </Modal>

      {/* View User Modal */}
      <Modal
        isOpen={viewModal.open}
        onClose={() => setViewModal({ open: false, user: null })}
        title="Информация о пользователе"
      >
        {viewModal.user && (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Telegram ID</p>
                <p className="font-medium">{viewModal.user.telegram_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Username</p>
                <p className="font-medium">{viewModal.user.username ? `@${viewModal.user.username}` : '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Имя</p>
                <p className="font-medium">{viewModal.user.first_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Язык</p>
                <p className="font-medium">{viewModal.user.language?.toUpperCase()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Регистрация</p>
                <p className="font-medium">{viewModal.user.created_at}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Статус</p>
                <p className="font-medium">
                  {viewModal.user.is_banned ? '🚫 Забанен' : '✓ Активен'}
                </p>
              </div>
            </div>
            {viewModal.user.ban_reason && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <p className="text-sm text-red-600 dark:text-red-400">
                  Причина бана: {viewModal.user.ban_reason}
                </p>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Confirm Dialogs */}
      <ConfirmDialog
        isOpen={confirmDialog.open && confirmDialog.action === 'revoke'}
        onClose={() => setConfirmDialog({ open: false, action: null, user: null })}
        onConfirm={handleRevokeAccess}
        title="Забрать доступ"
        message={`Забрать доступ у ${confirmDialog.user?.username || confirmDialog.user?.first_name}?`}
        variant="danger"
      />
      
      <ConfirmDialog
        isOpen={confirmDialog.open && confirmDialog.action === 'unban'}
        onClose={() => setConfirmDialog({ open: false, action: null, user: null })}
        onConfirm={handleUnban}
        title="Разбанить пользователя"
        message={`Разбанить ${confirmDialog.user?.username || confirmDialog.user?.first_name}?`}
        variant="success"
        confirmText="Разбанить"
      />
    </div>
  )
}
