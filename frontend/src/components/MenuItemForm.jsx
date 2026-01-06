import { useState, useEffect } from 'react'

const EMOJI_LIST = ['📺', '💳', '🎁', '❓', '📚', '📢', '🌐', '💬', '⚙️', '📖', '🎥', '📝', '🔗', '📁', '⭐', '🏆', '🎯', '💡', '🔥', '💎']

export default function MenuItemForm({ 
  initialData,  // Support both naming conventions
  item,
  parentId, 
  onSubmit,     // Support both naming conventions
  onSave,
  onCancel 
}) {
  // Use whichever prop is provided
  const data = initialData || item || {}
  const handleSave = onSubmit || onSave

  const [form, setForm] = useState({
    type: 'link',
    system_action: '',
    text_ru: '',
    text_en: '',
    icon: '',
    value: '',
    visibility: 'all',
    visibility_language: 'all',
    is_active: true,
    sort_order: 0,
    ...data
  })

  useEffect(() => {
    const newData = initialData || item || {}
    setForm({
      type: 'link',
      system_action: '',
      text_ru: '',
      text_en: '',
      icon: '',
      value: '',
      visibility: 'all',
      visibility_language: 'all',
      is_active: true,
      sort_order: 0,
      ...newData
    })
  }, [initialData, item])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (handleSave) {
      handleSave({
        ...form,
        parent_id: form.parent_id ?? data?.parent_id ?? parentId ?? null
      })
    }
  }

  const handleChange = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Type */}
      <div>
        <label className="label">Тип элемента</label>
        <select
          value={form.type}
          onChange={(e) => handleChange('type', e.target.value)}
          className="input"
        >
          <option value="section">📁 Раздел (подменю)</option>
          <option value="link">🔗 Ссылка</option>
          <option value="text">💬 Текст</option>
          <option value="faq">❓ FAQ</option>
          <option value="system">⚙️ Системное действие</option>
        </select>
      </div>

      {/* System action */}
      {form.type === 'system' && (
        <div>
          <label className="label">Системное действие</label>
          <select
            value={form.system_action || ''}
            onChange={(e) => handleChange('system_action', e.target.value)}
            className="input"
          >
            <option value="">Выберите...</option>
            <option value="tariffs">Тарифы</option>
            <option value="subscriptions">Мои подписки</option>
            <option value="language">Сменить язык</option>
            <option value="support">Поддержка</option>
            <option value="promocode">Ввести промокод</option>
          </select>
        </div>
      )}

      {/* Icon */}
      <div>
        <label className="label">Иконка</label>
        <div className="flex flex-wrap gap-2 mb-2">
          {EMOJI_LIST.map(emoji => (
            <button
              key={emoji}
              type="button"
              onClick={() => handleChange('icon', emoji)}
              className={`
                w-10 h-10 text-xl rounded-lg border-2 transition-colors
                ${form.icon === emoji 
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/30' 
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                }
              `}
            >
              {emoji}
            </button>
          ))}
        </div>
        <input
          type="text"
          value={form.icon || ''}
          onChange={(e) => handleChange('icon', e.target.value)}
          placeholder="Или введите свой emoji"
          className="input"
        />
      </div>

      {/* Text RU */}
      <div>
        <label className="label">Текст кнопки (RU) *</label>
        <input
          type="text"
          value={form.text_ru || ''}
          onChange={(e) => handleChange('text_ru', e.target.value)}
          placeholder="Например: Тарифы"
          className="input"
          required
        />
      </div>

      {/* Text EN */}
      <div>
        <label className="label">Текст кнопки (EN)</label>
        <input
          type="text"
          value={form.text_en || ''}
          onChange={(e) => handleChange('text_en', e.target.value)}
          placeholder="Example: Tariffs"
          className="input"
        />
      </div>

      {/* Value (URL / text / faq_id) */}
      {form.type === 'link' && (
        <div>
          <label className="label">URL ссылки</label>
          <input
            type="url"
            value={form.value || ''}
            onChange={(e) => handleChange('value', e.target.value)}
            placeholder="https://..."
            className="input"
          />
        </div>
      )}

      {form.type === 'text' && (
        <div>
          <label className="label">Текст сообщения</label>
          <textarea
            value={form.value || ''}
            onChange={(e) => handleChange('value', e.target.value)}
            placeholder="Текст, который отправится при нажатии"
            className="input"
            rows={4}
          />
        </div>
      )}

      {/* Visibility */}
      <div>
        <label className="label">Видимость</label>
        <select
          value={form.visibility || 'all'}
          onChange={(e) => handleChange('visibility', e.target.value)}
          className="input"
        >
          <option value="all">Всем пользователям</option>
          <option value="subscribed">Только с активной подпиской</option>
          <option value="not_subscribed">Только без подписки</option>
        </select>
      </div>

      {/* Language visibility */}
      <div>
        <label className="label">Язык</label>
        <select
          value={form.visibility_language || 'all'}
          onChange={(e) => handleChange('visibility_language', e.target.value)}
          className="input"
        >
          <option value="all">Все языки</option>
          <option value="ru">Только RU</option>
          <option value="en">Только EN</option>
        </select>
      </div>

      {/* Active */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_active"
          checked={form.is_active !== false}
          onChange={(e) => handleChange('is_active', e.target.checked)}
          className="w-4 h-4 rounded border-gray-300"
        />
        <label htmlFor="is_active" className="text-sm text-gray-700 dark:text-gray-300">
          Активен
        </label>
      </div>

      {/* Buttons */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <button type="button" onClick={onCancel} className="btn-secondary">
          Отмена
        </button>
        <button type="submit" className="btn-primary">
          {data?.id ? 'Сохранить' : 'Добавить'}
        </button>
      </div>
    </form>
  )
}
