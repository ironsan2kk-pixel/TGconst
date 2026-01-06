import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, ExternalLink } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog } from '../../components'
import { channelsAPI } from '../../api/client'

// Mock data
const mockChannels = [
  { id: 1, channel_id: -1001234567890, username: 'premium_signals', title: 'Premium Signals', is_active: true, created_at: '2024-01-15' },
  { id: 2, channel_id: -1001234567891, username: 'vip_trading', title: 'VIP Trading', is_active: true, created_at: '2024-01-20' },
  { id: 3, channel_id: -1001234567892, username: 'crypto_alerts', title: 'Crypto Alerts', is_active: false, created_at: '2024-02-01' },
]

export default function Channels() {
  const [channels, setChannels] = useState(mockChannels)
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [deleteDialog, setDeleteDialog] = useState({ open: false, channel: null })
  const [editingChannel, setEditingChannel] = useState(null)
  const [form, setForm] = useState({
    channel_id: '',
    username: '',
    title: '',
    description: '',
    invite_link: '',
    is_active: true
  })

  useEffect(() => {
    loadChannels()
  }, [])

  const loadChannels = async () => {
    try {
      setLoading(true)
      // const response = await channelsAPI.getAll()
      // setChannels(response.data)
    } catch (error) {
      console.error('Failed to load channels:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingChannel) {
        // await channelsAPI.update(editingChannel.id, form)
        setChannels(channels.map(c => c.id === editingChannel.id ? { ...c, ...form } : c))
      } else {
        // const response = await channelsAPI.create(form)
        const newChannel = { id: Date.now(), ...form, created_at: new Date().toISOString().split('T')[0] }
        setChannels([...channels, newChannel])
      }
      closeModal()
    } catch (error) {
      console.error('Failed to save channel:', error)
    }
  }

  const handleDelete = async () => {
    try {
      // await channelsAPI.delete(deleteDialog.channel.id)
      setChannels(channels.filter(c => c.id !== deleteDialog.channel.id))
      setDeleteDialog({ open: false, channel: null })
    } catch (error) {
      console.error('Failed to delete channel:', error)
    }
  }

  const openModal = (channel = null) => {
    if (channel) {
      setEditingChannel(channel)
      setForm({
        channel_id: channel.channel_id,
        username: channel.username,
        title: channel.title,
        description: channel.description || '',
        invite_link: channel.invite_link || '',
        is_active: channel.is_active
      })
    } else {
      setEditingChannel(null)
      setForm({
        channel_id: '',
        username: '',
        title: '',
        description: '',
        invite_link: '',
        is_active: true
      })
    }
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setEditingChannel(null)
  }

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'title', label: 'Название' },
    { 
      key: 'username', 
      label: 'Username',
      render: (val) => val ? `@${val}` : '-'
    },
    { 
      key: 'channel_id', 
      label: 'Channel ID',
      render: (val) => <code className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{val}</code>
    },
    { 
      key: 'is_active', 
      label: 'Статус',
      render: (val) => (
        <span className={`badge ${val ? 'badge-success' : 'badge-danger'}`}>
          {val ? 'Активен' : 'Неактивен'}
        </span>
      )
    },
    { key: 'created_at', label: 'Создан' }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Каналы</h1>
          <p className="text-gray-500 dark:text-gray-400">Управление привязанными каналами</p>
        </div>
        <button onClick={() => openModal()} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Добавить канал
        </button>
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        data={channels}
        searchable={true}
        searchKeys={['title', 'username']}
        actions={(row) => (
          <>
            {row.username && (
              <a
                href={`https://t.me/${row.username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
            <button
              onClick={() => openModal(row)}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setDeleteDialog({ open: true, channel: row })}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-red-500"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </>
        )}
      />

      {/* Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={closeModal}
        title={editingChannel ? 'Редактировать канал' : 'Добавить канал'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Channel ID</label>
            <input
              type="number"
              value={form.channel_id}
              onChange={(e) => setForm({ ...form, channel_id: e.target.value })}
              placeholder="-1001234567890"
              className="input"
              required
            />
            <p className="text-xs text-gray-500 mt-1">Telegram ID канала (начинается с -100)</p>
          </div>

          <div>
            <label className="label">Username</label>
            <input
              type="text"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              placeholder="premium_channel"
              className="input"
            />
          </div>

          <div>
            <label className="label">Название</label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Premium Channel"
              className="input"
              required
            />
          </div>

          <div>
            <label className="label">Описание</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Описание канала..."
              className="input"
              rows={3}
            />
          </div>

          <div>
            <label className="label">Invite Link</label>
            <input
              type="url"
              value={form.invite_link}
              onChange={(e) => setForm({ ...form, invite_link: e.target.value })}
              placeholder="https://t.me/+..."
              className="input"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={form.is_active}
              onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
              className="w-4 h-4 rounded"
            />
            <label htmlFor="is_active" className="text-sm">Активен</label>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button type="button" onClick={closeModal} className="btn btn-secondary">
              Отмена
            </button>
            <button type="submit" className="btn btn-primary">
              {editingChannel ? 'Сохранить' : 'Добавить'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete confirmation */}
      <ConfirmDialog
        isOpen={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, channel: null })}
        onConfirm={handleDelete}
        title="Удалить канал"
        message={`Вы уверены, что хотите удалить канал "${deleteDialog.channel?.title}"?`}
      />
    </div>
  )
}
