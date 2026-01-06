import { useState, useEffect } from 'react'
import { Save, RefreshCw } from 'lucide-react'
import { settingsAPI } from '../../api/client'

export default function Settings() {
  const [settings, setSettings] = useState({
    bot_token: '',
    cryptobot_token: '',
    admin_ids: '',
    welcome_message_ru: '',
    welcome_message_en: '',
    support_url: '',
    default_language: 'ru',
    notify_new_users: true,
    notify_payments: true
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setLoading(true)
    try {
      const response = await settingsAPI.getAll()
      const data = response.data
      setSettings({
        bot_token: data.bot_token || '',
        cryptobot_token: data.cryptobot_token || '',
        admin_ids: Array.isArray(data.admin_ids) ? data.admin_ids.join(', ') : (data.admin_ids || ''),
        welcome_message_ru: data.welcome_message_ru || '',
        welcome_message_en: data.welcome_message_en || '',
        support_url: data.support_url || '',
        default_language: data.default_language || 'ru',
        notify_new_users: data.notify_new_users !== false,
        notify_payments: data.notify_payments !== false
      })
    } catch (error) {
      console.error('Error loading settings:', error)
      setMessage({ type: 'error', text: 'Ошибка загрузки настроек' })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)
    try {
      const data = {
        ...settings,
        admin_ids: settings.admin_ids.split(',').map(id => id.trim()).filter(Boolean)
      }
      await settingsAPI.update(data)
      setMessage({ type: 'success', text: 'Настройки сохранены' })
    } catch (error) {
      console.error('Error saving settings:', error)
      setMessage({ type: 'error', text: 'Ошибка сохранения' })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Настройки</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Конфигурация бота
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={loadSettings} className="btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Обновить
          </button>
          <button onClick={handleSave} className="btn-primary flex items-center gap-2" disabled={saving}>
            <Save className="w-4 h-4" />
            {saving ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </div>

      {message && (
        <div className={`p-4 rounded-lg ${message.type === 'success' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bot Settings */}
        <div className="card p-6 space-y-4">
          <h3 className="text-lg font-semibold border-b pb-2 dark:border-gray-700">Telegram Bot</h3>
          
          <div>
            <label className="label">Bot Token</label>
            <input
              type="password"
              value={settings.bot_token}
              onChange={(e) => setSettings({ ...settings, bot_token: e.target.value })}
              className="input font-mono"
              placeholder="123456789:AABBCCDDEEFFgghhiijjkkllmmnn"
            />
          </div>

          <div>
            <label className="label">Admin IDs (через запятую)</label>
            <input
              type="text"
              value={settings.admin_ids}
              onChange={(e) => setSettings({ ...settings, admin_ids: e.target.value })}
              className="input"
              placeholder="123456789, 987654321"
            />
          </div>

          <div>
            <label className="label">Язык по умолчанию</label>
            <select
              value={settings.default_language}
              onChange={(e) => setSettings({ ...settings, default_language: e.target.value })}
              className="input"
            >
              <option value="ru">🇷🇺 Русский</option>
              <option value="en">🇬🇧 English</option>
            </select>
          </div>

          <div>
            <label className="label">Ссылка на поддержку</label>
            <input
              type="text"
              value={settings.support_url}
              onChange={(e) => setSettings({ ...settings, support_url: e.target.value })}
              className="input"
              placeholder="https://t.me/support"
            />
          </div>
        </div>

        {/* Payment Settings */}
        <div className="card p-6 space-y-4">
          <h3 className="text-lg font-semibold border-b pb-2 dark:border-gray-700">CryptoBot</h3>
          
          <div>
            <label className="label">CryptoBot Token</label>
            <input
              type="password"
              value={settings.cryptobot_token}
              onChange={(e) => setSettings({ ...settings, cryptobot_token: e.target.value })}
              className="input font-mono"
              placeholder="Токен от @CryptoBot"
            />
            <p className="text-xs text-gray-500 mt-1">
              Получите токен у @CryptoBot → My Apps
            </p>
          </div>
        </div>

        {/* Welcome Messages */}
        <div className="card p-6 space-y-4">
          <h3 className="text-lg font-semibold border-b pb-2 dark:border-gray-700">Приветственные сообщения</h3>
          
          <div>
            <label className="label">Приветствие (RU)</label>
            <textarea
              value={settings.welcome_message_ru}
              onChange={(e) => setSettings({ ...settings, welcome_message_ru: e.target.value })}
              className="input min-h-[100px]"
              placeholder="Привет! Добро пожаловать..."
            />
          </div>

          <div>
            <label className="label">Приветствие (EN)</label>
            <textarea
              value={settings.welcome_message_en}
              onChange={(e) => setSettings({ ...settings, welcome_message_en: e.target.value })}
              className="input min-h-[100px]"
              placeholder="Hello! Welcome..."
            />
          </div>
        </div>

        {/* Notifications */}
        <div className="card p-6 space-y-4">
          <h3 className="text-lg font-semibold border-b pb-2 dark:border-gray-700">Уведомления</h3>
          
          <div className="space-y-3">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notify_new_users}
                onChange={(e) => setSettings({ ...settings, notify_new_users: e.target.checked })}
                className="w-4 h-4 rounded"
              />
              <span>Уведомлять о новых пользователях</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notify_payments}
                onChange={(e) => setSettings({ ...settings, notify_payments: e.target.checked })}
                className="w-4 h-4 rounded"
              />
              <span>Уведомлять о платежах</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}
