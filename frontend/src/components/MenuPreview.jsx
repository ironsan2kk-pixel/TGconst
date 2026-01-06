import { useState } from 'react'

export default function MenuPreview({ items, language = 'ru' }) {
  const [currentPath, setCurrentPath] = useState([])
  
  const getChildren = (parentId) => {
    return items
      .filter(item => {
        if (item.parent_id !== parentId) return false
        if (!item.is_active) return false
        if (item.visibility_language !== 'all' && item.visibility_language !== language) return false
        return true
      })
      .sort((a, b) => a.sort_order - b.sort_order)
  }

  const currentParentId = currentPath.length > 0 ? currentPath[currentPath.length - 1].id : null
  const currentItems = getChildren(currentParentId)
  const currentTitle = currentPath.length > 0 
    ? currentPath[currentPath.length - 1][language === 'ru' ? 'text_ru' : 'text_en'] 
    : 'Главное меню'

  const handleItemClick = (item) => {
    if (item.type === 'section') {
      setCurrentPath([...currentPath, item])
    }
  }

  const handleBack = () => {
    setCurrentPath(currentPath.slice(0, -1))
  }

  const getText = (item) => {
    return language === 'ru' ? item.text_ru : (item.text_en || item.text_ru)
  }

  return (
    <div className="w-full max-w-sm mx-auto">
      {/* Phone frame */}
      <div className="bg-gray-900 rounded-3xl p-2 shadow-2xl">
        {/* Screen */}
        <div className="bg-[#1a1a2e] rounded-2xl overflow-hidden">
          {/* Telegram header */}
          <div className="bg-[#2b2b4a] px-4 py-3 flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold">B</span>
            </div>
            <div>
              <p className="text-white font-medium">Channel Bot</p>
              <p className="text-gray-400 text-xs">бот</p>
            </div>
          </div>

          {/* Chat area */}
          <div className="h-80 p-4 flex flex-col justify-end">
            {/* Message bubble */}
            <div className="bg-[#2b2b4a] rounded-2xl rounded-bl-sm p-3 max-w-[85%]">
              <p className="text-white text-sm">
                {language === 'ru' 
                  ? '👋 Добро пожаловать! Выберите действие:'
                  : '👋 Welcome! Choose an action:'
                }
              </p>
              <p className="text-gray-500 text-xs mt-1 text-right">12:00</p>
            </div>
          </div>

          {/* Buttons area */}
          <div className="bg-[#1e1e32] border-t border-gray-800 p-3">
            {/* Section title */}
            {currentPath.length > 0 && (
              <p className="text-center text-gray-400 text-xs mb-2">
                {currentTitle}
              </p>
            )}

            {/* Menu buttons */}
            <div className="space-y-2">
              {currentPath.length > 0 && (
                <button
                  onClick={handleBack}
                  className="w-full py-2.5 px-4 bg-[#2b2b4a] hover:bg-[#3b3b5a] rounded-xl text-white text-sm transition-colors"
                >
                  ← {language === 'ru' ? 'Назад' : 'Back'}
                </button>
              )}
              
              {currentItems.length === 0 ? (
                <p className="text-center text-gray-500 text-sm py-4">
                  {language === 'ru' ? 'Нет элементов' : 'No items'}
                </p>
              ) : (
                currentItems.map(item => (
                  <button
                    key={item.id}
                    onClick={() => handleItemClick(item)}
                    className="w-full py-2.5 px-4 bg-[#2b2b4a] hover:bg-[#3b3b5a] rounded-xl text-white text-sm transition-colors text-left flex items-center gap-2"
                  >
                    {item.icon && <span>{item.icon}</span>}
                    <span>{getText(item)}</span>
                    {item.type === 'section' && (
                      <span className="ml-auto text-gray-500">›</span>
                    )}
                    {item.type === 'link' && (
                      <span className="ml-auto text-gray-500">↗</span>
                    )}
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Input area */}
          <div className="bg-[#1e1e32] px-3 py-2 flex items-center gap-2">
            <div className="flex-1 bg-[#2b2b4a] rounded-full px-4 py-2">
              <span className="text-gray-500 text-sm">
                {language === 'ru' ? 'Сообщение' : 'Message'}
              </span>
            </div>
            <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
              <span className="text-white">🎤</span>
            </div>
          </div>
        </div>
      </div>

      {/* Language toggle */}
      <div className="flex justify-center gap-2 mt-4">
        <span className={`px-3 py-1 rounded-full text-xs ${language === 'ru' ? 'bg-primary-500 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>
          RU
        </span>
        <span className={`px-3 py-1 rounded-full text-xs ${language === 'en' ? 'bg-primary-500 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>
          EN
        </span>
      </div>
    </div>
  )
}
