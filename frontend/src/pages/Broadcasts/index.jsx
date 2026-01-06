import { useState, useEffect } from 'react'
import { Send, Plus, Pause, Play, X, Eye, Users } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog } from '../../components'
import { broadcastsAPI } from '../../api/client'

export default function Broadcasts() {
  const [broadcasts, setBroadcasts] = useState([])
  const [loading, setLoading] = useState(true)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [isViewOpen, setIsViewOpen] = useState(false)
  const [isConfirmOpen, setIsConfirmOpen] = useState(false)
  const [selectedBroadcast, setSelectedBroadcast] = useState(null)
  const [confirmAction, setConfirmAction] = useState(null)
  
  const [formData, setFormData] = useState({
    message_text: '',
    message_photo: '',
    buttons_json: '[]',
    filter_type: 'all',
    filter_language: 'all',
    scheduled_at: ''
  })

  useEffect(() => {
    loadBroadcasts()
  }, [])

  const loadBroadcasts = async () => {
    setLoading(true)
    try {
      const response = await broadcastsAPI.getAll()
      setBroadcasts(response.data)
    } catch (error) {
      console.error('Error loading broadcasts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      await broadcastsAPI.create(formData)
      setIsCreateOpen(false)
      resetForm()
      loadBroadcasts()
    } catch (error) {
      console.error('Error creating broadcast:', error)
    }
  }

  const handleAction = async () => {
    if (!selectedBroadcast || !confirmAction) return
    
    try {
      switch (confirmAction) {
        case 'start':
          await broadcastsAPI.start(selectedBroadcast.id)
          break
        case 'pause':
          await broadcastsAPI.pause(selectedBroadcast.id)
          break
        case 'cancel':
          await broadcastsAPI.cancel(selectedBroadcast.id)
          break
      }
      setIsConfirmOpen(false)
      loadBroadcasts()
    } catch (error) {
      console.error('Error:', error)
    }
  }

  const resetForm = () => {
    setFormData({
      message_text: '',
      message_photo: '',
      buttons_json: '[]',
      filter_type: 'all',
      filter_language: 'all',
      scheduled_at: ''
    })
  }

  const openConfirm = (broadcast, action) => {
    setSelectedBroadcast(broadcast)
    setConfirmAction(action)
    setIsConfirmOpen(true)
  }

  const getStatusBadge = (status) => {
    const styles = {
      draft: 'badge-yellow',
      running: 'badge-blue',
      paused: 'badge-yellow',
      completed: 'badge-green',
      cancelled: 'badge-red'
    }
    const labels = {
      draft: 'Черновик',
      running: 'Отправляется',
      paused: 'Приостановлено',
      completed: 'Завершено',
      cancelled: 'Отменено'
    }
    return <span className={styles[status]}>{labels[status]}</span>
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleString('ru-RU')
  }

  const columns = [
    {
      key: 'message_text',
      label: 'Сообщение',
      render: (_, row) => (
        <div className="max-w-xs">
          <p className="truncate text-sm">{row.message_text}</p>
        </div>
      )
    },
    {
      key: 'filter_type',
      label: 'Фильтр',
      render: (value) => {
        const labels = { all: 'Все', active: 'С подпиской', inactive: 'Без подписки' }
        return labels[value] || value
      }
    },
    {
      key: 'progress',
      label: 'Прогресс',
      render: (_, row) => (
        <div className="text-sm">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-gray-400" />
            <span>{row.sent_count || 0} / {row.total_users || 0}</span>
          </div>
          {row.total_users > 0 && (
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mt-1">
              <div 
                className="bg-primary-500 h-1.5 rounded-full" 
                style={{ width: `${((row.sent_count || 0) / row.total_users) * 100}%` }}
              />
            </div>
          )}
        </div>
      )
    },
    { key: 'status', label: 'Статус', render: (value) => getStatusBadge(value) },
    { key: 'created_at', label: 'Создано', render: formatDate }
  ]

  const actions = [
    {
      icon: Eye,
      label: 'Просмотр',
      onClick: (row) => {
        setSelectedBroadcast(row)
        setIsViewOpen(true)
      }
    },
    {
      icon: Play,
      label: 'Запустить',
      onClick: (row) => openConfirm(row, 'start'),
      show: (row) => row.status === 'draft' || row.status === 'paused'
    },
    {
      icon: Pause,
      label: 'Пауза',
      onClick: (row) => openConfirm(row, 'pause'),
      show: (row) => row.status === 'running'
    },
    {
      icon: X,
      label: 'Отменить',
      onClick: (row) => openConfirm(row, 'cancel'),
      className: 'text-red-600 hover:text-red-700',
      show: (row) => ['draft', 'running', 'paused'].includes(row.status)
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Рассылки</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Управление массовыми рассылками
          </p>
        </div>
        <button onClick={() => setIsCreateOpen(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Новая рассылка
        </button>
      </div>

      <DataTable data={broadcasts} columns={columns} actions={actions} loading={loading} searchable={false} />

      {/* Create Modal */}
      <Modal isOpen={isCreateOpen} onClose={() => { setIsCreateOpen(false); resetForm() }} title="Новая рассылка" size="lg">
        <div className="space-y-4">
          <div>
            <label className="label">Текст сообщения *</label>
            <textarea
              value={formData.message_text}
              onChange={(e) => setFormData({ ...formData, message_text: e.target.value })}
              className="input min-h-[120px]"
              placeholder="Введите текст рассылки..."
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Получатели</label>
              <select
                value={formData.filter_type}
                onChange={(e) => setFormData({ ...formData, filter_type: e.target.value })}
                className="input"
              >
                <option value="all">Все</option>
                <option value="active">С подпиской</option>
                <option value="inactive">Без подписки</option>
              </select>
            </div>
            <div>
              <label className="label">Язык</label>
              <select
                value={formData.filter_language}
                onChange={(e) => setFormData({ ...formData, filter_language: e.target.value })}
                className="input"
              >
                <option value="all">Все</option>
                <option value="ru">🇷🇺 Русский</option>
                <option value="en">🇬🇧 English</option>
              </select>
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => { setIsCreateOpen(false); resetForm() }} className="btn-secondary">Отмена</button>
          <button onClick={handleCreate} className="btn-primary flex items-center gap-2" disabled={!formData.message_text.trim()}>
            <Send className="w-4 h-4" />
            Создать
          </button>
        </div>
      </Modal>

      {/* View Modal */}
      <Modal isOpen={isViewOpen} onClose={() => setIsViewOpen(false)} title="Детали рассылки" size="lg">
        {selectedBroadcast && (
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p className="whitespace-pre-wrap">{selectedBroadcast.message_text}</p>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-gray-500">Статус:</span> {getStatusBadge(selectedBroadcast.status)}</div>
              <div><span className="text-gray-500">Получателей:</span> {selectedBroadcast.total_users}</div>
              <div><span className="text-gray-500">Отправлено:</span> <span className="text-green-600">{selectedBroadcast.sent_count}</span></div>
              <div><span className="text-gray-500">Ошибок:</span> <span className="text-red-600">{selectedBroadcast.failed_count}</span></div>
            </div>
          </div>
        )}
      </Modal>

      <ConfirmDialog
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={handleAction}
        title="Подтверждение"
        message={confirmAction === 'cancel' ? 'Отменить рассылку?' : confirmAction === 'start' ? 'Запустить рассылку?' : 'Приостановить рассылку?'}
        confirmText="Подтвердить"
        danger={confirmAction === 'cancel'}
      />
    </div>
  )
}
