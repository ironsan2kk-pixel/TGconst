import { useState, useEffect } from 'react'
import { Eye, UserPlus, UserMinus, Ban, CheckCircle, Download } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog, ExportButton } from '../../components'
import { usersAPI, tariffsAPI } from '../../api/client'

export default function Users() {
  const [users, setUsers] = useState([])
  const [tariffs, setTariffs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedUser, setSelectedUser] = useState(null)
  const [isViewOpen, setIsViewOpen] = useState(false)
  const [isGrantOpen, setIsGrantOpen] = useState(false)
  const [isRevokeOpen, setIsRevokeOpen] = useState(false)
  const [isBanOpen, setIsBanOpen] = useState(false)
  const [grantData, setGrantData] = useState({ tariff_id: '', days: '30' })
  const [banReason, setBanReason] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [usersRes, tariffsRes] = await Promise.all([
        usersAPI.getAll(),
        tariffsAPI.getAll()
      ])
      // Handle paginated response
      const usersData = usersRes.data.items || usersRes.data
      const tariffsData = tariffsRes.data.items || tariffsRes.data
      setUsers(Array.isArray(usersData) ? usersData : [])
      setTariffs(Array.isArray(tariffsData) ? tariffsData : [])
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGrant = async () => {
    try {
      await usersAPI.grantAccess(selectedUser.id, {
        tariff_id: parseInt(grantData.tariff_id),
        days: parseInt(grantData.days)
      })
      setIsGrantOpen(false)
      setGrantData({ tariff_id: '', days: '30' })
      loadData()
    } catch (error) {
      console.error('Error granting access:', error)
    }
  }

  const handleRevoke = async () => {
    try {
      // Need to get active subscription tariff_id
      const tariffId = selectedUser.active_tariff_id || grantData.tariff_id
      if (tariffId) {
        await usersAPI.revokeAccess(selectedUser.id, tariffId)
      }
      setIsRevokeOpen(false)
      loadData()
    } catch (error) {
      console.error('Error revoking access:', error)
    }
  }

  const handleBan = async () => {
    try {
      await usersAPI.ban(selectedUser.id, banReason)
      setIsBanOpen(false)
      setBanReason('')
      loadData()
    } catch (error) {
      console.error('Error banning user:', error)
    }
  }

  const handleUnban = async (user) => {
    try {
      await usersAPI.unban(user.id)
      loadData()
    } catch (error) {
      console.error('Error unbanning user:', error)
    }
  }

  const columns = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'telegram_id', label: 'Telegram ID', sortable: true },
    { 
      key: 'username', 
      label: 'Username',
      render: (value) => value ? `@${value}` : '—'
    },
    { key: 'first_name', label: 'Имя', sortable: true },
    { 
      key: 'language', 
      label: 'Язык',
      render: (value) => value === 'ru' ? '🇷🇺' : '🇬🇧'
    },
    { 
      key: 'active_subscriptions_count', 
      label: 'Подписка',
      render: (value) => (
        <span className={value > 0 ? 'badge-green' : 'badge-yellow'}>
          {value > 0 ? 'Активна' : 'Нет'}
        </span>
      )
    },
    { 
      key: 'is_banned', 
      label: 'Статус',
      render: (value) => value ? (
        <span className="badge-red">Забанен</span>
      ) : (
        <span className="badge-green">Активен</span>
      )
    }
  ]

  const actions = [
    {
      icon: Eye,
      label: 'Просмотр',
      onClick: (row) => {
        setSelectedUser(row)
        setIsViewOpen(true)
      }
    },
    {
      icon: UserPlus,
      label: 'Выдать доступ',
      onClick: (row) => {
        setSelectedUser(row)
        setIsGrantOpen(true)
      }
    },
    {
      icon: UserMinus,
      label: 'Забрать доступ',
      onClick: (row) => {
        setSelectedUser(row)
        setIsRevokeOpen(true)
      },
      show: (row) => row.active_subscriptions_count > 0
    },
    {
      icon: Ban,
      label: 'Забанить',
      onClick: (row) => {
        setSelectedUser(row)
        setIsBanOpen(true)
      },
      className: 'text-red-600 hover:text-red-700',
      show: (row) => !row.is_banned
    },
    {
      icon: CheckCircle,
      label: 'Разбанить',
      onClick: handleUnban,
      className: 'text-green-600 hover:text-green-700',
      show: (row) => row.is_banned
    }
  ]

  const formatDate = (dateStr) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleString('ru-RU')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Пользователи</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Всего: {users.length}
          </p>
        </div>
        <ExportButton
          data={users}
          filename="users"
          columns={['id', 'telegram_id', 'username', 'first_name', 'last_name', 'language', 'is_banned', 'created_at']}
        />
      </div>

      <DataTable
        data={users}
        columns={columns}
        actions={actions}
        loading={loading}
        searchKeys={['username', 'first_name', 'last_name', 'telegram_id']}
      />

      {/* View Modal */}
      <Modal isOpen={isViewOpen} onClose={() => setIsViewOpen(false)} title="Информация о пользователе">
        {selectedUser && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-gray-500">ID:</span> <span className="ml-2 font-medium">{selectedUser.id}</span></div>
              <div><span className="text-gray-500">Telegram ID:</span> <span className="ml-2 font-medium">{selectedUser.telegram_id}</span></div>
              <div><span className="text-gray-500">Username:</span> <span className="ml-2 font-medium">{selectedUser.username || '—'}</span></div>
              <div><span className="text-gray-500">Имя:</span> <span className="ml-2 font-medium">{selectedUser.first_name} {selectedUser.last_name}</span></div>
              <div><span className="text-gray-500">Язык:</span> <span className="ml-2">{selectedUser.language === 'ru' ? '🇷🇺 Русский' : '🇬🇧 English'}</span></div>
              <div><span className="text-gray-500">Регистрация:</span> <span className="ml-2">{formatDate(selectedUser.created_at)}</span></div>
            </div>
          </div>
        )}
      </Modal>

      {/* Grant Access Modal */}
      <Modal isOpen={isGrantOpen} onClose={() => setIsGrantOpen(false)} title="Выдать доступ">
        <div className="space-y-4">
          <div>
            <label className="label">Тариф</label>
            <select value={grantData.tariff_id} onChange={(e) => setGrantData({ ...grantData, tariff_id: e.target.value })} className="input">
              <option value="">Выберите тариф</option>
              {tariffs.map(t => (<option key={t.id} value={t.id}>{t.name_ru} (${t.price})</option>))}
            </select>
          </div>
          <div>
            <label className="label">Срок (дней)</label>
            <input type="number" value={grantData.days} onChange={(e) => setGrantData({ ...grantData, days: e.target.value })} className="input" />
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => setIsGrantOpen(false)} className="btn-secondary">Отмена</button>
          <button onClick={handleGrant} className="btn-primary" disabled={!grantData.tariff_id}>Выдать</button>
        </div>
      </Modal>

      {/* Revoke Confirm */}
      <ConfirmDialog isOpen={isRevokeOpen} onClose={() => setIsRevokeOpen(false)} onConfirm={handleRevoke} title="Забрать доступ" message={`Забрать доступ у ${selectedUser?.username || selectedUser?.first_name}?`} confirmText="Забрать" danger />

      {/* Ban Modal */}
      <Modal isOpen={isBanOpen} onClose={() => setIsBanOpen(false)} title="Забанить пользователя">
        <div>
          <label className="label">Причина бана</label>
          <textarea value={banReason} onChange={(e) => setBanReason(e.target.value)} className="input" rows={3} placeholder="Укажите причину..." />
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => setIsBanOpen(false)} className="btn-secondary">Отмена</button>
          <button onClick={handleBan} className="btn-primary bg-red-600 hover:bg-red-700">Забанить</button>
        </div>
      </Modal>
    </div>
  )
}
