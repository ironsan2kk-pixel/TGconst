import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Copy } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog } from '../../components'
import { promocodesAPI } from '../../api/client'

export default function Promocodes() {
  const [promocodes, setPromocodes] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [selectedPromo, setSelectedPromo] = useState(null)
  const [formData, setFormData] = useState({
    code: '',
    discount_percent: '',
    discount_amount: '',
    max_uses: '',
    valid_until: '',
    tariff_id: '',
    is_active: true
  })

  useEffect(() => {
    loadPromocodes()
  }, [])

  const loadPromocodes = async () => {
    setLoading(true)
    try {
      const response = await promocodesAPI.getAll()
      const data = response.data.items || response.data; setPromocodes(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error loading promocodes:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    try {
      const data = {
        ...formData,
        discount_percent: formData.discount_percent ? parseInt(formData.discount_percent) : null,
        discount_amount: formData.discount_amount ? parseFloat(formData.discount_amount) : null,
        max_uses: formData.max_uses ? parseInt(formData.max_uses) : null,
        tariff_id: formData.tariff_id ? parseInt(formData.tariff_id) : null
      }
      if (selectedPromo) {
        await promocodesAPI.update(selectedPromo.id, data)
      } else {
        await promocodesAPI.create(data)
      }
      setIsModalOpen(false)
      resetForm()
      loadPromocodes()
    } catch (error) {
      console.error('Error saving promocode:', error)
    }
  }

  const handleDelete = async () => {
    try {
      await promocodesAPI.delete(selectedPromo.id)
      setIsDeleteOpen(false)
      loadPromocodes()
    } catch (error) {
      console.error('Error deleting promocode:', error)
    }
  }

  const openEditModal = (promo) => {
    setSelectedPromo(promo)
    setFormData({
      code: promo.code,
      discount_percent: promo.discount_percent?.toString() || '',
      discount_amount: promo.discount_amount?.toString() || '',
      max_uses: promo.max_uses?.toString() || '',
      valid_until: promo.valid_until ? promo.valid_until.slice(0, 16) : '',
      tariff_id: promo.tariff_id?.toString() || '',
      is_active: promo.is_active
    })
    setIsModalOpen(true)
  }

  const resetForm = () => {
    setSelectedPromo(null)
    setFormData({
      code: '',
      discount_percent: '',
      discount_amount: '',
      max_uses: '',
      valid_until: '',
      tariff_id: '',
      is_active: true
    })
  }

  const generateCode = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    let code = ''
    for (let i = 0; i < 8; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    setFormData({ ...formData, code })
  }

  const copyCode = (code) => {
    navigator.clipboard.writeText(code)
  }

  const getStatusBadge = (promo) => {
    if (!promo.is_active) return <span className="badge-red">Отключен</span>
    if (promo.valid_until && new Date(promo.valid_until) < new Date()) {
      return <span className="badge-red">Истёк</span>
    }
    if (promo.max_uses && promo.used_count >= promo.max_uses) {
      return <span className="badge-yellow">Исчерпан</span>
    }
    return <span className="badge-green">Активен</span>
  }

  const columns = [
    { key: 'id', label: 'ID', sortable: true },
    { 
      key: 'code', 
      label: 'Код',
      render: (value) => (
        <div className="flex items-center gap-2">
          <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded font-mono">
            {value}
          </code>
          <button onClick={() => copyCode(value)} className="text-gray-400 hover:text-gray-600">
            <Copy className="w-4 h-4" />
          </button>
        </div>
      )
    },
    { 
      key: 'discount', 
      label: 'Скидка',
      render: (_, row) => {
        if (row.discount_percent) return `${row.discount_percent}%`
        if (row.discount_amount) return `$${row.discount_amount}`
        return '—'
      }
    },
    { 
      key: 'usage', 
      label: 'Использований',
      render: (_, row) => `${row.used_count || 0}${row.max_uses ? ` / ${row.max_uses}` : ''}`
    },
    { 
      key: 'valid_until', 
      label: 'Действует до',
      render: (value) => value ? new Date(value).toLocaleDateString('ru-RU') : 'Бессрочно'
    },
    { 
      key: 'status', 
      label: 'Статус',
      render: (_, row) => getStatusBadge(row)
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
      onClick: (row) => {
        setSelectedPromo(row)
        setIsDeleteOpen(true)
      },
      className: 'text-red-600 hover:text-red-700'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Промокоды</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Всего: {promocodes.length}
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
          Добавить промокод
        </button>
      </div>

      <DataTable
        data={promocodes}
        columns={columns}
        actions={actions}
        loading={loading}
        searchKeys={['code']}
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          resetForm()
        }}
        title={selectedPromo ? 'Редактировать промокод' : 'Добавить промокод'}
      >
        <div className="space-y-4">
          <div>
            <label className="label">Код *</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                className="input flex-1 font-mono"
                placeholder="PROMO2024"
                required
              />
              <button onClick={generateCode} type="button" className="btn-secondary">
                Генерировать
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Скидка %</label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.discount_percent}
                onChange={(e) => setFormData({ ...formData, discount_percent: e.target.value, discount_amount: '' })}
                className="input"
                placeholder="20"
              />
            </div>
            <div>
              <label className="label">Или фикс. сумма $</label>
              <input
                type="number"
                step="0.01"
                value={formData.discount_amount}
                onChange={(e) => setFormData({ ...formData, discount_amount: e.target.value, discount_percent: '' })}
                className="input"
                placeholder="5.00"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Лимит использований</label>
              <input
                type="number"
                value={formData.max_uses}
                onChange={(e) => setFormData({ ...formData, max_uses: e.target.value })}
                className="input"
                placeholder="Без лимита"
              />
            </div>
            <div>
              <label className="label">Действует до</label>
              <input
                type="datetime-local"
                value={formData.valid_until}
                onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })}
                className="input"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="promo_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-4 h-4 rounded"
            />
            <label htmlFor="promo_active" className="text-sm">Активен</label>
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => { setIsModalOpen(false); resetForm() }} className="btn-secondary">
            Отмена
          </button>
          <button onClick={handleSubmit} className="btn-primary" disabled={!formData.code}>
            {selectedPromo ? 'Сохранить' : 'Добавить'}
          </button>
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={handleDelete}
        title="Удалить промокод"
        message={`Удалить промокод "${selectedPromo?.code}"?`}
        confirmText="Удалить"
        danger
      />
    </div>
  )
}
