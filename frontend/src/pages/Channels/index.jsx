import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, ExternalLink } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog } from '../../components'
import { channelsAPI } from '../../api/client'

export default function Channels() {
  const [channels, setChannels] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [selectedChannel, setSelectedChannel] = useState(null)
  const [formData, setFormData] = useState({
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
    setLoading(true)
    try {
      const response = await channelsAPI.getAll()
      setChannels(response.data)
    } catch (error) {
      console.error('Error loading channels:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    try {
      if (selectedChannel) {
        await channelsAPI.update(selectedChannel.id, formData)
      } else {
        await channelsAPI.create(formData)
      }
      setIsModalOpen(false)
      resetForm()
      loadChannels()
    } catch (error) {
      console.error('Error saving channel:', error)
    }
  }

  const handleDelete = async () => {
    try {
      await channelsAPI.delete(selectedChannel.id)
      setIsDeleteOpen(false)
      setSelectedChannel(null)
      loadChannels()
    } catch (error) {
      console.error('Error deleting channel:', error)
    }
  }

  const openEditModal = (channel) => {
    setSelectedChannel(channel)
    setFormData({
      channel_id: channel.channel_id,
      username: channel.username,
      title: channel.title,
      description: channel.description || '',
      invite_link: channel.invite_link || '',
      is_active: channel.is_active
    })
    setIsModalOpen(true)
  }

  const openDeleteDialog = (channel) => {
    setSelectedChannel(channel)
    setIsDeleteOpen(true)
  }

  const resetForm = () => {
    setSelectedChannel(null)
    setFormData({
      channel_id: '',
      username: '',
      title: '',
      description: '',
      invite_link: '',
      is_active: true
    })
  }

  const columns = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'channel_id', label: 'Channel ID', sortable: true },
    { 
      key: 'username', 
      label: 'Username',
      render: (value) => value ? (
        <a 
          href={`https://t.me/${value}`} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-primary-600 hover:text-primary-700 flex items-center gap-1"
        >
          @{value}
          <ExternalLink className="w-3 h-3" />
        </a>
      ) : '—'
    },
    { key: 'title', label: 'Название', sortable: true },
    { 
      key: 'is_active', 
      label: 'Статус',
      render: (value) => (
        <span className={value ? 'badge-green' : 'badge-red'}>
          {value ? 'Активен' : 'Отключен'}
        </span>
      )
    }
  ]

  const actions = [
    {
      icon: Edit,
      label: 'Редактировать',
      onClick: openEditModal
    },
    {
      icon: Trash2,
      label: 'Удалить',
      onClick: openDeleteDialog,
      className: 'text-red-600 hover:text-red-700'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Каналы</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Управление приватными каналами
          </p>
        </div>
        <button
          onClick={() => {
            resetForm()
            setIsModalOpen(true)
          }}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Добавить канал
        </button>
      </div>

      <DataTable
        data={channels}
        columns={columns}
        actions={actions}
        loading={loading}
        searchKeys={['username', 'title', 'channel_id']}
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          resetForm()
        }}
        title={selectedChannel ? 'Редактировать канал' : 'Добавить канал'}
      >
        <div className="space-y-4">
          <div>
            <label className="label">Channel ID *</label>
            <input
              type="text"
              value={formData.channel_id}
              onChange={(e) => setFormData({ ...formData, channel_id: e.target.value })}
              className="input"
              placeholder="-1001234567890"
              required
            />
          </div>
          <div>
            <label className="label">Username</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="input"
              placeholder="channel_username"
            />
          </div>
          <div>
            <label className="label">Название *</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="input"
              placeholder="Название канала"
              required
            />
          </div>
          <div>
            <label className="label">Описание</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input"
              rows={3}
              placeholder="Описание канала"
            />
          </div>
          <div>
            <label className="label">Invite Link</label>
            <input
              type="text"
              value={formData.invite_link}
              onChange={(e) => setFormData({ ...formData, invite_link: e.target.value })}
              className="input"
              placeholder="https://t.me/+ABC123"
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300"
            />
            <label htmlFor="is_active" className="text-sm">Активен</label>
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={() => {
              setIsModalOpen(false)
              resetForm()
            }}
            className="btn-secondary"
          >
            Отмена
          </button>
          <button onClick={handleSubmit} className="btn-primary">
            {selectedChannel ? 'Сохранить' : 'Добавить'}
          </button>
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={handleDelete}
        title="Удалить канал"
        message={`Вы уверены что хотите удалить канал "${selectedChannel?.title}"?`}
        confirmText="Удалить"
        danger
      />
    </div>
  )
}
