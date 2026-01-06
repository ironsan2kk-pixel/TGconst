import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Copy, Link } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog } from '../../components'
import { tariffsAPI, channelsAPI } from '../../api/client'

export default function Tariffs() {
  const [tariffs, setTariffs] = useState([])
  const [channels, setChannels] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [selectedTariff, setSelectedTariff] = useState(null)
  const [formData, setFormData] = useState({
    name_ru: '',
    name_en: '',
    description_ru: '',
    description_en: '',
    price: '',
    duration_days: '',
    trial_days: '0',
    is_active: true,
    sort_order: 0,
    channel_ids: []
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [tariffsRes, channelsRes] = await Promise.all([
        tariffsAPI.getAll(),
        channelsAPI.getAll()
      ])
      setTariffs(tariffsRes.data)
      setChannels(channelsRes.data)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    try {
      const data = {
        ...formData,
        price: parseFloat(formData.price),
        duration_days: parseInt(formData.duration_days) || 0,
        trial_days: parseInt(formData.trial_days) || 0
      }
      if (selectedTariff) {
        await tariffsAPI.update(selectedTariff.id, data)
      } else {
        await tariffsAPI.create(data)
      }
      setIsModalOpen(false)
      resetForm()
      loadData()
    } catch (error) {
      console.error('Error saving tariff:', error)
    }
  }

  const handleDelete = async () => {
    try {
      await tariffsAPI.delete(selectedTariff.id)
      setIsDeleteOpen(false)
      setSelectedTariff(null)
      loadData()
    } catch (error) {
      console.error('Error deleting tariff:', error)
    }
  }

  const openEditModal = (tariff) => {
    setSelectedTariff(tariff)
    setFormData({
      name_ru: tariff.name_ru,
      name_en: tariff.name_en || '',
      description_ru: tariff.description_ru || '',
      description_en: tariff.description_en || '',
      price: tariff.price.toString(),
      duration_days: tariff.duration_days.toString(),
      trial_days: (tariff.trial_days || 0).toString(),
      is_active: tariff.is_active,
      sort_order: tariff.sort_order || 0,
      channel_ids: tariff.channel_ids || []
    })
    setIsModalOpen(true)
  }

  const resetForm = () => {
    setSelectedTariff(null)
    setFormData({
      name_ru: '',
      name_en: '',
      description_ru: '',
      description_en: '',
      price: '',
      duration_days: '',
      trial_days: '0',
      is_active: true,
      sort_order: 0,
      channel_ids: []
    })
  }

  const copyDeepLink = (tariffId) => {
    const link = `t.me/YOUR_BOT?start=tariff_${tariffId}`
    navigator.clipboard.writeText(link)
  }

  const columns = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name_ru', label: 'Название', sortable: true },
    { 
      key: 'price', 
      label: 'Цена',
      sortable: true,
      render: (value) => `$${value}`
    },
    { 
      key: 'duration_days', 
      label: 'Срок',
      render: (value) => value === 0 ? 'Навсегда' : `${value} дн.`
    },
    { 
      key: 'trial_days', 
      label: 'Пробный',
      render: (value) => value > 0 ? `${value} дн.` : '—'
    },
    {
      key: 'channels_count',
      label: 'Каналов',
      render: (_, row) => row.channel_ids?.length || 0
    },
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
      icon: Link,
      label: 'Копировать ссылку',
      onClick: (row) => copyDeepLink(row.id)
    },
    {
      icon: Edit,
      label: 'Редактировать',
      onClick: openEditModal
    },
    {
      icon: Trash2,
      label: 'Удалить',
      onClick: (row) => {
        setSelectedTariff(row)
        setIsDeleteOpen(true)
      },
      className: 'text-red-600 hover:text-red-700'
    }
  ]

  const handleChannelToggle = (channelId) => {
    setFormData(prev => ({
      ...prev,
      channel_ids: prev.channel_ids.includes(channelId)
        ? prev.channel_ids.filter(id => id !== channelId)
        : [...prev.channel_ids, channelId]
    }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Тарифы</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Управление тарифными планами
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
          Добавить тариф
        </button>
      </div>

      <DataTable
        data={tariffs}
        columns={columns}
        actions={actions}
        loading={loading}
        searchKeys={['name_ru', 'name_en']}
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          resetForm()
        }}
        title={selectedTariff ? 'Редактировать тариф' : 'Добавить тариф'}
        size="lg"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Название (RU) *</label>
              <input
                type="text"
                value={formData.name_ru}
                onChange={(e) => setFormData({ ...formData, name_ru: e.target.value })}
                className="input"
                placeholder="Базовый"
                required
              />
            </div>
            <div>
              <label className="label">Название (EN)</label>
              <input
                type="text"
                value={formData.name_en}
                onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
                className="input"
                placeholder="Basic"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Описание (RU)</label>
              <textarea
                value={formData.description_ru}
                onChange={(e) => setFormData({ ...formData, description_ru: e.target.value })}
                className="input"
                rows={2}
              />
            </div>
            <div>
              <label className="label">Описание (EN)</label>
              <textarea
                value={formData.description_en}
                onChange={(e) => setFormData({ ...formData, description_en: e.target.value })}
                className="input"
                rows={2}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">Цена (USDT) *</label>
              <input
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="input"
                placeholder="10.00"
                required
              />
            </div>
            <div>
              <label className="label">Срок (дней)</label>
              <input
                type="number"
                value={formData.duration_days}
                onChange={(e) => setFormData({ ...formData, duration_days: e.target.value })}
                className="input"
                placeholder="30 (0 = навсегда)"
              />
            </div>
            <div>
              <label className="label">Пробный (дней)</label>
              <input
                type="number"
                value={formData.trial_days}
                onChange={(e) => setFormData({ ...formData, trial_days: e.target.value })}
                className="input"
                placeholder="0"
              />
            </div>
          </div>

          <div>
            <label className="label">Каналы</label>
            <div className="space-y-2 max-h-40 overflow-y-auto border rounded-lg p-3 dark:border-gray-600">
              {channels.length === 0 ? (
                <p className="text-gray-500 text-sm">Нет доступных каналов</p>
              ) : (
                channels.map(channel => (
                  <label key={channel.id} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.channel_ids.includes(channel.id)}
                      onChange={() => handleChannelToggle(channel.id)}
                      className="w-4 h-4 rounded"
                    />
                    <span className="text-sm">{channel.title}</span>
                    {channel.username && (
                      <span className="text-xs text-gray-500">@{channel.username}</span>
                    )}
                  </label>
                ))
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="tariff_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-4 h-4 rounded"
            />
            <label htmlFor="tariff_active" className="text-sm">Активен</label>
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => { setIsModalOpen(false); resetForm() }} className="btn-secondary">
            Отмена
          </button>
          <button onClick={handleSubmit} className="btn-primary">
            {selectedTariff ? 'Сохранить' : 'Добавить'}
          </button>
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={handleDelete}
        title="Удалить тариф"
        message={`Вы уверены что хотите удалить тариф "${selectedTariff?.name_ru}"?`}
        confirmText="Удалить"
        danger
      />
    </div>
  )
}
