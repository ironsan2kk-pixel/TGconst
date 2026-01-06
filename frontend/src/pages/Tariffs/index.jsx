import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, Copy } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog } from '../../components'
import { tariffsAPI, channelsAPI } from '../../api/client'

// Mock data
const mockTariffs = [
  { id: 1, name_ru: 'Базовый', name_en: 'Basic', price: 10, duration_days: 30, trial_days: 3, is_active: true, channels: [1] },
  { id: 2, name_ru: 'Премиум', name_en: 'Premium', price: 25, duration_days: 30, trial_days: 0, is_active: true, channels: [1, 2] },
  { id: 3, name_ru: 'VIP', name_en: 'VIP', price: 99, duration_days: 0, trial_days: 7, is_active: true, channels: [1, 2, 3] },
]

const mockChannels = [
  { id: 1, title: 'Premium Signals' },
  { id: 2, title: 'VIP Trading' },
  { id: 3, title: 'Crypto Alerts' },
]

export default function Tariffs() {
  const [tariffs, setTariffs] = useState(mockTariffs)
  const [channels, setChannels] = useState(mockChannels)
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [deleteDialog, setDeleteDialog] = useState({ open: false, tariff: null })
  const [editingTariff, setEditingTariff] = useState(null)
  const [form, setForm] = useState({
    name_ru: '',
    name_en: '',
    description_ru: '',
    description_en: '',
    price: '',
    duration_days: 30,
    trial_days: 0,
    is_active: true,
    channels: []
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      // const [tariffsRes, channelsRes] = await Promise.all([
      //   tariffsAPI.getAll(),
      //   channelsAPI.getAll()
      // ])
      // setTariffs(tariffsRes.data)
      // setChannels(channelsRes.data)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = { ...form, price: parseFloat(form.price) }
      if (editingTariff) {
        setTariffs(tariffs.map(t => t.id === editingTariff.id ? { ...t, ...data } : t))
      } else {
        const newTariff = { id: Date.now(), ...data }
        setTariffs([...tariffs, newTariff])
      }
      closeModal()
    } catch (error) {
      console.error('Failed to save tariff:', error)
    }
  }

  const handleDelete = async () => {
    try {
      setTariffs(tariffs.filter(t => t.id !== deleteDialog.tariff.id))
      setDeleteDialog({ open: false, tariff: null })
    } catch (error) {
      console.error('Failed to delete tariff:', error)
    }
  }

  const copyDeepLink = (tariffId) => {
    const link = `t.me/your_bot?start=tariff_${tariffId}`
    navigator.clipboard.writeText(link)
    // TODO: Show toast notification
  }

  const openModal = (tariff = null) => {
    if (tariff) {
      setEditingTariff(tariff)
      setForm({
        name_ru: tariff.name_ru,
        name_en: tariff.name_en || '',
        description_ru: tariff.description_ru || '',
        description_en: tariff.description_en || '',
        price: tariff.price.toString(),
        duration_days: tariff.duration_days,
        trial_days: tariff.trial_days || 0,
        is_active: tariff.is_active,
        channels: tariff.channels || []
      })
    } else {
      setEditingTariff(null)
      setForm({
        name_ru: '',
        name_en: '',
        description_ru: '',
        description_en: '',
        price: '',
        duration_days: 30,
        trial_days: 0,
        is_active: true,
        channels: []
      })
    }
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setEditingTariff(null)
  }

  const toggleChannel = (channelId) => {
    setForm(prev => ({
      ...prev,
      channels: prev.channels.includes(channelId)
        ? prev.channels.filter(id => id !== channelId)
        : [...prev.channels, channelId]
    }))
  }

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name_ru', label: 'Название' },
    { 
      key: 'price', 
      label: 'Цена',
      render: (val) => `$${val}`
    },
    { 
      key: 'duration_days', 
      label: 'Срок',
      render: (val) => val === 0 ? '♾️ Навсегда' : `${val} дн.`
    },
    { 
      key: 'trial_days', 
      label: 'Пробный',
      render: (val) => val > 0 ? `${val} дн.` : '-'
    },
    { 
      key: 'channels', 
      label: 'Каналов',
      render: (val) => val?.length || 0
    },
    { 
      key: 'is_active', 
      label: 'Статус',
      render: (val) => (
        <span className={`badge ${val ? 'badge-success' : 'badge-danger'}`}>
          {val ? 'Активен' : 'Неактивен'}
        </span>
      )
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Тарифы</h1>
          <p className="text-gray-500 dark:text-gray-400">Управление тарифами подписки</p>
        </div>
        <button onClick={() => openModal()} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Добавить тариф
        </button>
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        data={tariffs}
        searchable={true}
        searchKeys={['name_ru', 'name_en']}
        actions={(row) => (
          <>
            <button
              onClick={() => copyDeepLink(row.id)}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"
              title="Копировать deep link"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={() => openModal(row)}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setDeleteDialog({ open: true, tariff: row })}
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
        title={editingTariff ? 'Редактировать тариф' : 'Добавить тариф'}
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Название (RU)</label>
              <input
                type="text"
                value={form.name_ru}
                onChange={(e) => setForm({ ...form, name_ru: e.target.value })}
                placeholder="Базовый"
                className="input"
                required
              />
            </div>
            <div>
              <label className="label">Название (EN)</label>
              <input
                type="text"
                value={form.name_en}
                onChange={(e) => setForm({ ...form, name_en: e.target.value })}
                placeholder="Basic"
                className="input"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Описание (RU)</label>
              <textarea
                value={form.description_ru}
                onChange={(e) => setForm({ ...form, description_ru: e.target.value })}
                placeholder="Описание тарифа..."
                className="input"
                rows={3}
              />
            </div>
            <div>
              <label className="label">Описание (EN)</label>
              <textarea
                value={form.description_en}
                onChange={(e) => setForm({ ...form, description_en: e.target.value })}
                placeholder="Tariff description..."
                className="input"
                rows={3}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">Цена (USDT)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={form.price}
                onChange={(e) => setForm({ ...form, price: e.target.value })}
                placeholder="10.00"
                className="input"
                required
              />
            </div>
            <div>
              <label className="label">Срок (дней)</label>
              <input
                type="number"
                min="0"
                value={form.duration_days}
                onChange={(e) => setForm({ ...form, duration_days: parseInt(e.target.value) || 0 })}
                placeholder="30"
                className="input"
              />
              <p className="text-xs text-gray-500 mt-1">0 = навсегда</p>
            </div>
            <div>
              <label className="label">Пробный (дней)</label>
              <input
                type="number"
                min="0"
                value={form.trial_days}
                onChange={(e) => setForm({ ...form, trial_days: parseInt(e.target.value) || 0 })}
                placeholder="0"
                className="input"
              />
              <p className="text-xs text-gray-500 mt-1">0 = без пробного</p>
            </div>
          </div>

          {/* Channels */}
          <div>
            <label className="label">Каналы</label>
            <div className="space-y-2 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              {channels.map(channel => (
                <label key={channel.id} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.channels.includes(channel.id)}
                    onChange={() => toggleChannel(channel.id)}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-sm">{channel.title}</span>
                </label>
              ))}
              {channels.length === 0 && (
                <p className="text-sm text-gray-500">Нет доступных каналов</p>
              )}
            </div>
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
              {editingTariff ? 'Сохранить' : 'Добавить'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete confirmation */}
      <ConfirmDialog
        isOpen={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, tariff: null })}
        onConfirm={handleDelete}
        title="Удалить тариф"
        message={`Вы уверены, что хотите удалить тариф "${deleteDialog.tariff?.name_ru}"?`}
      />
    </div>
  )
}
