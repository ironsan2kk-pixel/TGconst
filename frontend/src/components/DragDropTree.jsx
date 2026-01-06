import { useState } from 'react'
import { ChevronRight, ChevronDown, GripVertical, Plus, Edit2, Trash2 } from 'lucide-react'

export default function DragDropTree({ 
  items = [], 
  onEdit, 
  onDelete, 
  onAdd,
  onReorder 
}) {
  const [expandedIds, setExpandedIds] = useState(new Set())

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

  const getTypeIcon = (type) => {
    switch (type) {
      case 'section': return '📁'
      case 'link': return '🔗'
      case 'text': return '💬'
      case 'faq': return '❓'
      case 'system': return '⚙️'
      default: return '📄'
    }
  }

  const getTypeLabel = (type, systemAction) => {
    switch (type) {
      case 'section': return 'Раздел'
      case 'link': return 'Ссылка'
      case 'text': return 'Текст'
      case 'faq': return 'FAQ'
      case 'system': 
        const actions = {
          tariffs: 'Тарифы',
          subscriptions: 'Подписки',
          language: 'Язык',
          support: 'Поддержка',
          promocode: 'Промокод'
        }
        return actions[systemAction] || 'Система'
      default: return type
    }
  }

  const renderItem = (item, level = 0) => {
    // items is already a tree structure with children property
    const children = item.children || []
    const hasChildren = children.length > 0
    const isExpanded = expandedIds.has(item.id)

    return (
      <div key={item.id}>
        <div 
          className={`
            flex items-center gap-2 px-3 py-2 rounded-lg
            hover:bg-gray-100 dark:hover:bg-gray-700
            ${!item.is_active ? 'opacity-50' : ''}
          `}
          style={{ paddingLeft: `${level * 24 + 12}px` }}
        >
          {/* Drag handle */}
          <GripVertical className="w-4 h-4 text-gray-400 cursor-grab" />
          
          {/* Expand/Collapse */}
          {item.type === 'section' ? (
            <button 
              onClick={() => toggleExpand(item.id)}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
            >
              {isExpanded 
                ? <ChevronDown className="w-4 h-4" /> 
                : <ChevronRight className="w-4 h-4" />
              }
            </button>
          ) : (
            <div className="w-6" />
          )}
          
          {/* Icon */}
          <span className="text-lg">{item.icon || getTypeIcon(item.type)}</span>
          
          {/* Name */}
          <div className="flex-1 min-w-0">
            <p className="font-medium text-gray-900 dark:text-white truncate">
              {item.text_ru || 'Без названия'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {getTypeLabel(item.type, item.system_action)}
              {item.visibility && item.visibility !== 'all' && (
                <span className="ml-2">
                  • {item.visibility === 'subscribed' ? '👑 Подписчики' : '🆓 Без подписки'}
                </span>
              )}
            </p>
          </div>
          
          {/* Actions */}
          <div className="flex items-center gap-1">
            {item.type === 'section' && (
              <button
                onClick={() => onAdd && onAdd(item.id)}
                className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-500"
                title="Добавить вложенный"
              >
                <Plus className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={() => onEdit && onEdit(item)}
              className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-500"
              title="Редактировать"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => onDelete && onDelete(item)}
              className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-red-500"
              title="Удалить"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {/* Children */}
        {item.type === 'section' && isExpanded && hasChildren && (
          <div className="border-l-2 border-gray-200 dark:border-gray-700 ml-6">
            {children.map(child => renderItem(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  if (!items || items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <p>Меню пустое</p>
        <button 
          onClick={() => onAdd && onAdd(null)}
          className="mt-2 btn-primary"
        >
          <Plus className="w-4 h-4 inline mr-2" />
          Добавить элемент
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {items.map(item => renderItem(item))}
      <button 
        onClick={() => onAdd && onAdd(null)}
        className="w-full mt-4 py-2 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-500 hover:border-primary-500 hover:text-primary-500 transition-colors"
      >
        <Plus className="w-4 h-4 inline mr-2" />
        Добавить в корень
      </button>
    </div>
  )
}
