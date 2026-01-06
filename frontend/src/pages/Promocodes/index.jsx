import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, Copy } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog } from '../../components'

// Mock data
const mockPromocodes = [
  { id: 1, code: 'WELCOME10', discount_percent: 10, discount_amount: null, max_uses: 100, used_count: 45, valid_until: '2024-12-31', is_active: true },
  { id: 2, code: 'VIP50', discount_percent: 50, discount_amount: null, max_uses: 10, used_count: 10, valid_until: '2024-06-30', is_active: false },
  { id: 3, code: 'FLAT5', discount_percent: null, discount_amount: 5, max_uses: null, used_count: 123, valid_until: null, is_active: true },
]

export default function Promocodes() {
  const [promocodes, setPromocodes] = useState(mockPromocodes)
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [deleteDialog, setDeleteDialog] = useState({ open: false, promo: null })
  const [editingPromo, setEditingPromo] = useState(null)
  const [form, setForm] = useState({
    code: '',
    discount_type: 'percent',
    discount_percent: '',
    discount_amount: '',
    max_uses: '',
    valid_until: '',
    is_active: true
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = {
        ...form,
        code: form.code.toUpperCase(),
        discount_percent: form.discount_type === 'percent' ? parseInt(form.discount_percent) : null,
        discount_amount: form.discount_type === 'amount' ? parseFloat(form.discount_amount) : null,
        max_uses: form.max_uses ? parseInt(form.max_uses) : null,
        valid_until: form.valid_until || null
      }
      
      if (editingPromo) {
        setPromocodes(promocodes.map(p => p.id === editingPromo.id ? { ...p, ...data } : p))
      } else {
        const newPromo = { id: Date.now(), ...data, used_count: 0 }
        setPromocodes([...promocodes, newPromo])
      }
      closeModal()
    } catch (error) {
      console.error('Failed to save:', error)
    }
  }

  const handleDelete = async () => {
    try {
      setPromocodes(promocodes.filter(p => p.id !== deleteDialog.promo.id))
      setDeleteDialog({ open: false, promo: null })
    } catch (error) {
      console.error('Failed to delete:', error)
    }
  }

  const copyCode = (code) => {
    navigator.clipboard.writeText(code)
  }

  const generateCode = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    let code = ''
    for (let i = 0; i < 8; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    setForm({ ...form, code })
  }

  const openModal = (promo = null) => {
    if (promo) {
      setEditingPromo(promo)
      setForm({
        code: promo.code,
        discount_type: promo.discount_percent ? 'percent' : 'amount',
        discount_percent: promo.discount_percent?.toString() || '',
        discount_amount: promo.discount_amount?.toString() || '',
        max_uses: promo.max_uses?.toString() || '',
        valid_until: promo.valid_until || '',
        is_active: promo.is_active
      })
    } else {
      setEditingPromo(null)
      setForm({
        code: '',
        discount_type: 'percent',
        discount_percent: '',
        discount_amount: '',
        max_uses: '',
        valid_until: '',
        is_active: true
      })
    }
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setEditingPromo(null)
  }

  const columns = [
    { key: 'id', label: 'ID' },
    { 
      key: 'code', 
      label: 'Код',
      render: (val) => (
        <code className="font-bold text-primary-600 dark:text-primary-400">{val}</code>
      )
    },
    { 
      key: 'discount_percent', 
      label: 'Скидка',
      render: (val, row) => row.discount_percent 
        ? `${row.discount_percent}%` 
        : `$${row.discount_amount}`
    },
    { 
      key: 'used_count', 
      label: 'Использований',
      render: (val, row) => row.max_uses 
        ? `${val} / ${row.max_uses}` 
        : `${val} / ∞`
    },
    { 
      key: 'valid_until', 
      label: 'Действует до',
      render: (val) => val || '♾️ Бессрочно'
    },
    { 
      key: 'is_active', 
      label: 'Статус',
      render: (val, row) => {
        const isExpired = row.valid_until && new Date(row.valid_until) < new Date()
        const isUsedUp = row.max_uses && row.used_count >= row.max_uses
        if (!val) return <span className="badge badge-danger">Неактивен</span>
        if (isExpired) return <span className="badge badge-warning">Истёк</span>
        if (isUsedUp) return <span className="badge badge-warning">Исчерпан</span>
        return <span className="badge badge-success">Активен</span>
      }
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Промокоды</h1>
          <p className="text-gray-500 dark:text-gray-400">
            Активных: {promocodes.filter(p => p.is_active).length}
          </p>
        </div>
        <button onClick={() => openModal()} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Добавить промокод
        </button>
      </div>

      <DataTable
        columns={columns}
        data={promocodes}
        searchable={true}
        searchKeys={['code']}
        actions={(row) => (
          <>
            <button
              onClick={() => copyCode(row.code)}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500"
              title="Копировать"
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
              onClick={() => setDeleteDialog({ open: true, promo: row })}
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
        title={editingPromo ? 'Редактировать промокод' : 'Добавить промокод'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Код</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={form.code}
                onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })}
                placeholder="SAVE10"
                className="input flex-1"
                required
              />
              <button type="button" onClick={generateCode} className="btn btn-secondary">
                Сгенерировать
              </button>
            </div>
          </div>

          <div>
            <label className="label">Тип скидки</label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="discount_type"
                  value="percent"
                  checked={form.discount_type === 'percent'}
                  onChange={(e) => setForm({ ...form, discount_type: e.target.value })}
                />
                <span>Процент</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="discount_type"
                  value="amount"
                  checked={form.discount_type === 'amount'}
                  onChange={(e) => setForm({ ...form, discount_type: e.target.value })}
                />
                <span>Фиксированная сумма</span>
              </label>
            </div>
          </div>

          {form.discount_type === 'percent' ? (
            <div>
              <label className="label">Скидка (%)</label>
              <input
                type="number"
                min="1"
                max="100"
                value={form.discount_percent}
                onChange={(e) => setForm({ ...form, discount_percent: e.target.value })}
                placeholder="10"
                className="input"
                required
              />
            </div>
          ) : (
            <div>
              <label className="label">Скидка (USDT)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={form.discount_amount}
                onChange={(e) => setForm({ ...form, discount_amount: e.target.value })}
                placeholder="5.00"
                className="input"
                required
              />
            </div>
          )}

          <div>
            <label className="label">Лимит использований</label>
            <input
              type="number"
              min="1"
              value={form.max_uses}
              onChange={(e) => setForm({ ...form, max_uses: e.target.value })}
              placeholder="Без лимита"
              className="input"
            />
          </div>

          <div>
            <label className="label">Действует до</label>
            <input
              type="date"
              value={form.valid_until}
              onChange={(e) => setForm({ ...form, valid_until: e.target.value })}
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
              {editingPromo ? 'Сохранить' : 'Добавить'}
            </button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        isOpen={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, promo: null })}
        onConfirm={handleDelete}
        title="Удалить промокод"
        message={`Удалить промокод "${deleteDialog.promo?.code}"?`}
      />
    </div>
  )
}
