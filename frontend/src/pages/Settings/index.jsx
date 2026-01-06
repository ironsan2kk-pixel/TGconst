import { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Save,
  Bot,
  CreditCard,
  Bell,
  Globe,
  Shield,
  RefreshCw,
  Eye,
  EyeOff,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
// import { settingsAPI } from '../../api/client';

export default function Settings() {
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showTokens, setShowTokens] = useState({});
  const [saveStatus, setSaveStatus] = useState(null);
  const [activeTab, setActiveTab] = useState('bot');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      // const response = await settingsAPI.getAll();
      // setSettings(response.data);
      
      // Mock data
      setSettings({
        bot_token: '7123456789:AABBCCDDEEFFgghhiijjkkllmmnnoopp',
        cryptobot_token: 'crypto_token_here',
        cryptobot_webhook_secret: 'webhook_secret',
        admin_ids: '[123456789, 987654321]',
        welcome_message_ru: '👋 Добро пожаловать!\n\nЭто бот для доступа к приватным каналам.\nВыберите тариф и получите доступ к эксклюзивному контенту.',
        welcome_message_en: '👋 Welcome!\n\nThis is a bot for accessing private channels.\nChoose a tariff and get access to exclusive content.',
        support_url: 'https://t.me/support_username',
        default_language: 'ru',
        notify_new_users: true,
        notify_payments: true
      });
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveStatus(null);
    try {
      // await settingsAPI.updateAll(settings);
      console.log('Saving settings:', settings);
      setSaveStatus('success');
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveStatus('error');
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const toggleShowToken = (key) => {
    setShowTokens(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const tabs = [
    { id: 'bot', label: 'Telegram бот', icon: Bot },
    { id: 'payments', label: 'Платежи', icon: CreditCard },
    { id: 'notifications', label: 'Уведомления', icon: Bell },
    { id: 'localization', label: 'Локализация', icon: Globe },
    { id: 'admins', label: 'Админы', icon: Shield }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Настройки
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Конфигурация бота и системы
          </p>
        </div>
        <button
          onClick={handleSave}
          className="btn-primary flex items-center gap-2"
          disabled={saving}
        >
          {saving ? (
            <RefreshCw className="w-5 h-5 animate-spin" />
          ) : (
            <Save className="w-5 h-5" />
          )}
          Сохранить
        </button>
      </div>

      {/* Save Status */}
      {saveStatus && (
        <div className={`p-4 rounded-lg flex items-center gap-3 ${
          saveStatus === 'success' 
            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' 
            : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
        }`}>
          {saveStatus === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          {saveStatus === 'success' ? 'Настройки сохранены!' : 'Ошибка сохранения'}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex gap-4 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm whitespace-nowrap
                ${activeTab === tab.id
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                }
              `}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="card p-6">
        {activeTab === 'bot' && (
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">
              Telegram бот
            </h2>
            
            <div>
              <label className="label">Bot Token *</label>
              <div className="relative">
                <input
                  type={showTokens.bot_token ? 'text' : 'password'}
                  value={settings.bot_token || ''}
                  onChange={(e) => updateSetting('bot_token', e.target.value)}
                  className="input pr-10 font-mono"
                  placeholder="123456789:AABBCCDDEEFFgghhiijjkkllmmnn"
                />
                <button
                  onClick={() => toggleShowToken('bot_token')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showTokens.bot_token ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Получите токен у @BotFather
              </p>
            </div>

            <div>
              <label className="label">Ссылка на поддержку</label>
              <input
                type="text"
                value={settings.support_url || ''}
                onChange={(e) => updateSetting('support_url', e.target.value)}
                className="input"
                placeholder="https://t.me/support_username"
              />
              <p className="text-sm text-gray-500 mt-1">
                URL или @username для кнопки "Поддержка"
              </p>
            </div>
          </div>
        )}

        {activeTab === 'payments' && (
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">
              Настройки платежей (CryptoBot)
            </h2>
            
            <div>
              <label className="label">CryptoBot Token</label>
              <div className="relative">
                <input
                  type={showTokens.cryptobot_token ? 'text' : 'password'}
                  value={settings.cryptobot_token || ''}
                  onChange={(e) => updateSetting('cryptobot_token', e.target.value)}
                  className="input pr-10 font-mono"
                  placeholder="Оставьте пустым для отключения платежей"
                />
                <button
                  onClick={() => toggleShowToken('cryptobot_token')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showTokens.cryptobot_token ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Получите токен в @CryptoBot → Crypto Pay → Create App
              </p>
            </div>

            <div>
              <label className="label">Webhook Secret</label>
              <div className="relative">
                <input
                  type={showTokens.cryptobot_webhook_secret ? 'text' : 'password'}
                  value={settings.cryptobot_webhook_secret || ''}
                  onChange={(e) => updateSetting('cryptobot_webhook_secret', e.target.value)}
                  className="input pr-10 font-mono"
                  placeholder="Секрет для проверки webhook"
                />
                <button
                  onClick={() => toggleShowToken('cryptobot_webhook_secret')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showTokens.cryptobot_webhook_secret ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                <strong>Важно:</strong> После настройки CryptoBot токена, 
                укажите Webhook URL в настройках вашего приложения CryptoBot:
                <br />
                <code className="bg-yellow-100 dark:bg-yellow-900/50 px-2 py-0.5 rounded mt-1 inline-block">
                  https://your-domain.com/webhooks/cryptobot
                </code>
              </p>
            </div>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">
              Уведомления админам
            </h2>

            <div className="space-y-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notify_new_users || false}
                  onChange={(e) => updateSetting('notify_new_users', e.target.checked)}
                  className="w-5 h-5 rounded border-gray-300 text-primary-500 focus:ring-primary-500"
                />
                <div>
                  <span className="text-gray-900 dark:text-white font-medium">
                    Новые пользователи
                  </span>
                  <p className="text-sm text-gray-500">
                    Уведомлять о каждом новом пользователе бота
                  </p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notify_payments || false}
                  onChange={(e) => updateSetting('notify_payments', e.target.checked)}
                  className="w-5 h-5 rounded border-gray-300 text-primary-500 focus:ring-primary-500"
                />
                <div>
                  <span className="text-gray-900 dark:text-white font-medium">
                    Платежи
                  </span>
                  <p className="text-sm text-gray-500">
                    Уведомлять о каждой успешной оплате
                  </p>
                </div>
              </label>
            </div>
          </div>
        )}

        {activeTab === 'localization' && (
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">
              Локализация
            </h2>

            <div>
              <label className="label">Язык по умолчанию</label>
              <select
                value={settings.default_language || 'ru'}
                onChange={(e) => updateSetting('default_language', e.target.value)}
                className="input"
              >
                <option value="ru">🇷🇺 Русский</option>
                <option value="en">🇬🇧 English</option>
              </select>
              <p className="text-sm text-gray-500 mt-1">
                Язык для новых пользователей до выбора
              </p>
            </div>

            <div>
              <label className="label">Приветственное сообщение (RU)</label>
              <textarea
                value={settings.welcome_message_ru || ''}
                onChange={(e) => updateSetting('welcome_message_ru', e.target.value)}
                className="input min-h-[120px]"
                placeholder="Приветствие на русском..."
              />
            </div>

            <div>
              <label className="label">Приветственное сообщение (EN)</label>
              <textarea
                value={settings.welcome_message_en || ''}
                onChange={(e) => updateSetting('welcome_message_en', e.target.value)}
                className="input min-h-[120px]"
                placeholder="Welcome message in English..."
              />
            </div>
          </div>
        )}

        {activeTab === 'admins' && (
          <div className="space-y-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">
              Администраторы
            </h2>

            <div>
              <label className="label">Telegram ID админов (JSON массив)</label>
              <textarea
                value={settings.admin_ids || '[]'}
                onChange={(e) => updateSetting('admin_ids', e.target.value)}
                className="input font-mono min-h-[80px]"
                placeholder="[123456789, 987654321]"
              />
              <p className="text-sm text-gray-500 mt-1">
                Список Telegram ID в формате JSON. Узнать свой ID можно у @userinfobot
              </p>
            </div>

            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Права админов:</strong>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>Доступ к команде /admin в боте</li>
                  <li>Просмотр статистики</li>
                  <li>Выдача и отзыв доступа</li>
                  <li>Бан/разбан пользователей</li>
                  <li>Ручное подтверждение оплаты</li>
                  <li>Рассылки</li>
                  <li>Получение уведомлений</li>
                </ul>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
