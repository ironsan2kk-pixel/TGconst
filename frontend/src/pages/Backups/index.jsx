import { useState, useEffect } from 'react'
import { Download, Trash2, Plus, RefreshCw, Database } from 'lucide-react'
import { DataTable, ConfirmDialog } from '../../components'
import { backupAPI } from '../../api/client'

export default function Backups() {
  const [backups, setBackups] = useState([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [selectedBackup, setSelectedBackup] = useState(null)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    loadBackups()
  }, [])

  const loadBackups = async () => {
    setLoading(true)
    try {
      const response = await backupAPI.list()
      setBackups(response.data)
    } catch (error) {
      console.error('Error loading backups:', error)
      setMessage({ type: 'error', text: 'Ошибка загрузки списка бэкапов' })
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    setCreating(true)
    setMessage(null)
    try {
      await backupAPI.create()
      setMessage({ type: 'success', text: 'Бэкап создан успешно' })
      loadBackups()
    } catch (error) {
      console.error('Error creating backup:', error)
      setMessage({ type: 'error', text: 'Ошибка создания бэкапа' })
    } finally {
      setCreating(false)
    }
  }

  const handleDownload = async (backup) => {
    try {
      const response = await backupAPI.download(backup.filename)
      const blob = new Blob([response.data], { type: 'application/octet-stream' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = backup.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading backup:', error)
      setMessage({ type: 'error', text: 'Ошибка скачивания' })
    }
  }

  const handleDelete = async () => {
    try {
      await backupAPI.delete(selectedBackup.filename)
      setIsDeleteOpen(false)
      setMessage({ type: 'success', text: 'Бэкап удалён' })
      loadBackups()
    } catch (error) {
      console.error('Error deleting backup:', error)
      setMessage({ type: 'error', text: 'Ошибка удаления' })
    }
  }

  const formatSize = (bytes) => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleString('ru-RU')
  }

  const columns = [
    { 
      key: 'filename', 
      label: 'Файл',
      render: (value) => (
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-gray-400" />
          <span className="font-mono text-sm">{value}</span>
        </div>
      )
    },
    { 
      key: 'size', 
      label: 'Размер',
      render: formatSize
    },
    { 
      key: 'created_at', 
      label: 'Создан',
      render: formatDate
    }
  ]

  const actions = [
    {
      icon: Download,
      label: 'Скачать',
      onClick: handleDownload
    },
    {
      icon: Trash2,
      label: 'Удалить',
      onClick: (row) => {
        setSelectedBackup(row)
        setIsDeleteOpen(true)
      },
      className: 'text-red-600 hover:text-red-700'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Бэкапы</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Резервные копии базы данных
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={loadBackups} className="btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Обновить
          </button>
          <button 
            onClick={handleCreate} 
            className="btn-primary flex items-center gap-2"
            disabled={creating}
          >
            <Plus className="w-4 h-4" />
            {creating ? 'Создание...' : 'Создать бэкап'}
          </button>
        </div>
      </div>

      {message && (
        <div className={`p-4 rounded-lg ${message.type === 'success' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
          {message.text}
        </div>
      )}

      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <Database className="w-5 h-5 text-blue-500" />
          <span className="text-sm text-blue-700 dark:text-blue-300">
            Бэкапы хранятся в папке <code className="bg-blue-100 dark:bg-blue-900 px-1 rounded">data/backups/</code>
          </span>
        </div>

        <DataTable
          data={backups}
          columns={columns}
          actions={actions}
          loading={loading}
          searchable={false}
        />
      </div>

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={handleDelete}
        title="Удалить бэкап"
        message={`Удалить бэкап "${selectedBackup?.filename}"? Это действие нельзя отменить.`}
        confirmText="Удалить"
        danger
      />
    </div>
  )
}
