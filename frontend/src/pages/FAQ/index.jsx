import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, ChevronDown, ChevronRight } from 'lucide-react'
import { DataTable, Modal, ConfirmDialog } from '../../components'
import { faqAPI } from '../../api/client'

export default function FAQ() {
  const [faqItems, setFaqItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [expandedIds, setExpandedIds] = useState(new Set())
  const [formData, setFormData] = useState({
    question_ru: '',
    question_en: '',
    answer_ru: '',
    answer_en: '',
    category_id: '',
    sort_order: 0,
    is_active: true
  })

  useEffect(() => {
    loadFAQ()
  }, [])

  const loadFAQ = async () => {
    setLoading(true)
    try {
      const response = await faqAPI.getAll()
      setFaqItems(response.data)
    } catch (error) {
      console.error('Error loading FAQ:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    try {
      const data = {
        ...formData,
        category_id: formData.category_id ? parseInt(formData.category_id) : null,
        sort_order: parseInt(formData.sort_order) || 0
      }
      if (selectedItem) {
        await faqAPI.update(selectedItem.id, data)
      } else {
        await faqAPI.create(data)
      }
      setIsModalOpen(false)
      resetForm()
      loadFAQ()
    } catch (error) {
      console.error('Error saving FAQ:', error)
    }
  }

  const handleDelete = async () => {
    try {
      await faqAPI.delete(selectedItem.id)
      setIsDeleteOpen(false)
      loadFAQ()
    } catch (error) {
      console.error('Error deleting FAQ:', error)
    }
  }

  const openEditModal = (item) => {
    setSelectedItem(item)
    setFormData({
      question_ru: item.question_ru,
      question_en: item.question_en || '',
      answer_ru: item.answer_ru,
      answer_en: item.answer_en || '',
      category_id: item.category_id?.toString() || '',
      sort_order: item.sort_order || 0,
      is_active: item.is_active
    })
    setIsModalOpen(true)
  }

  const resetForm = () => {
    setSelectedItem(null)
    setFormData({
      question_ru: '',
      question_en: '',
      answer_ru: '',
      answer_en: '',
      category_id: '',
      sort_order: 0,
      is_active: true
    })
  }

  const toggleExpand = (id) => {
    setExpandedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const columns = [
    { key: 'id', label: 'ID', sortable: true },
    { 
      key: 'question_ru', 
      label: 'Вопрос',
      render: (value, row) => (
        <div>
          <button 
            onClick={() => toggleExpand(row.id)}
            className="flex items-center gap-2 text-left hover:text-primary-600"
          >
            {expandedIds.has(row.id) ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
            <span className="font-medium">{value}</span>
          </button>
          {expandedIds.has(row.id) && (
            <div className="mt-2 ml-6 p-3 bg-gray-50 dark:bg-gray-700 rounded text-sm">
              {row.answer_ru}
            </div>
          )}
        </div>
      )
    },
    { 
      key: 'is_active', 
      label: 'Статус',
      render: (value) => (
        <span className={value ? 'badge-green' : 'badge-red'}>
          {value ? 'Активен' : 'Скрыт'}
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
      onClick: (row) => {
        setSelectedItem(row)
        setIsDeleteOpen(true)
      },
      className: 'text-red-600 hover:text-red-700'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">FAQ</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Вопросы и ответы: {faqItems.length}
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
          Добавить вопрос
        </button>
      </div>

      <DataTable
        data={faqItems}
        columns={columns}
        actions={actions}
        loading={loading}
        searchKeys={['question_ru', 'question_en', 'answer_ru']}
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          resetForm()
        }}
        title={selectedItem ? 'Редактировать вопрос' : 'Добавить вопрос'}
        size="lg"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Вопрос (RU) *</label>
              <input
                type="text"
                value={formData.question_ru}
                onChange={(e) => setFormData({ ...formData, question_ru: e.target.value })}
                className="input"
                required
              />
            </div>
            <div>
              <label className="label">Вопрос (EN)</label>
              <input
                type="text"
                value={formData.question_en}
                onChange={(e) => setFormData({ ...formData, question_en: e.target.value })}
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="label">Ответ (RU) *</label>
            <textarea
              value={formData.answer_ru}
              onChange={(e) => setFormData({ ...formData, answer_ru: e.target.value })}
              className="input min-h-[100px]"
              required
            />
          </div>

          <div>
            <label className="label">Ответ (EN)</label>
            <textarea
              value={formData.answer_en}
              onChange={(e) => setFormData({ ...formData, answer_en: e.target.value })}
              className="input min-h-[100px]"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="faq_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-4 h-4 rounded"
            />
            <label htmlFor="faq_active" className="text-sm">Активен</label>
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button onClick={() => { setIsModalOpen(false); resetForm() }} className="btn-secondary">
            Отмена
          </button>
          <button 
            onClick={handleSubmit} 
            className="btn-primary"
            disabled={!formData.question_ru || !formData.answer_ru}
          >
            {selectedItem ? 'Сохранить' : 'Добавить'}
          </button>
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={handleDelete}
        title="Удалить вопрос"
        message={`Удалить "${selectedItem?.question_ru}"?`}
        confirmText="Удалить"
        danger
      />
    </div>
  )
}
