import { useEffect } from 'react'
import { X } from 'lucide-react'

export default function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'md',
  showClose = true 
}) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen) return null

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4'
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className={`
          relative w-full ${sizeClasses[size]}
          bg-white dark:bg-gray-800 
          rounded-xl shadow-xl
        `}>
          {/* Header */}
          {(title || showClose) && (
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              {title && (
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {title}
                </h3>
              )}
              {showClose && (
                <button
                  onClick={onClose}
                  className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              )}
            </div>
          )}
          
          {/* Content */}
          <div className="px-6 py-4">
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}

// Confirm Dialog
export function ConfirmDialog({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title = 'Подтверждение',
  message = 'Вы уверены?',
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  variant = 'primary',
  danger = false  // Support boolean danger prop
}) {
  // If danger prop is true, use danger variant
  const actualVariant = danger ? 'danger' : variant

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <p className="text-gray-600 dark:text-gray-400 mb-6">{message}</p>
      <div className="flex justify-end gap-3">
        <button onClick={onClose} className="btn-secondary">
          {cancelText}
        </button>
        <button 
          onClick={onConfirm} 
          className={actualVariant === 'danger' ? 'btn-primary bg-red-600 hover:bg-red-700' : 'btn-primary'}
        >
          {confirmText}
        </button>
      </div>
    </Modal>
  )
}
