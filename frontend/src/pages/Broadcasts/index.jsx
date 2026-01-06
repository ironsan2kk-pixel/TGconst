import { useState, useEffect } from 'react';
import { 
  Send, 
  Plus, 
  Play, 
  Pause, 
  X, 
  Eye,
  Users,
  CheckCircle,
  XCircle,
  Clock,
  Filter
} from 'lucide-react';
import { DataTable, Modal, ConfirmDialog } from '../../components';
// import { broadcastsAPI } from '../../api/client';

export default function Broadcasts() {
  const [broadcasts, setBroadcasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [selectedBroadcast, setSelectedBroadcast] = useState(null);
  const [confirmAction, setConfirmAction] = useState(null);
  
  const [formData, setFormData] = useState({
    message_text: '',
    message_photo: '',
    buttons_json: '[]',
    filter_type: 'all',
    filter_language: 'all',
    scheduled_at: ''
  });

  useEffect(() => {
    fetchBroadcasts();
  }, []);

  const fetchBroadcasts = async () => {
    setLoading(true);
    try {
      // const response = await broadcastsAPI.getAll();
      // setBroadcasts(response.data);
      
      // Mock data
      setBroadcasts([
        {
          id: 1,
          message_text: '🎉 Новогодняя распродажа! Скидка 30% на все тарифы до 31 декабря!',
          message_photo: null,
          buttons_json: '[{"text": "Купить", "url": "t.me/bot?start=tariff_1"}]',
          filter_type: 'all',
          filter_language: 'all',
          total_users: 1250,
          sent_count: 1248,
          failed_count: 2,
          status: 'completed',
          scheduled_at: null,
          started_at: '2025-01-01T10:00:00Z',
          completed_at: '2025-01-01T10:15:00Z',
          created_at: '2025-01-01T09:00:00Z'
        },
        {
          id: 2,
          message_text: '📢 Напоминание о продлении подписки. Не пропустите контент!',
          message_photo: null,
          buttons_json: '[]',
          filter_type: 'active',
          filter_language: 'ru',
          total_users: 450,
          sent_count: 230,
          failed_count: 5,
          status: 'running',
          scheduled_at: null,
          started_at: '2025-01-06T14:00:00Z',
          completed_at: null,
          created_at: '2025-01-06T13:30:00Z'
        },
        {
          id: 3,
          message_text: '🚀 Coming soon: New premium features!',
          message_photo: null,
          buttons_json: '[]',
          filter_type: 'all',
          filter_language: 'en',
          total_users: 0,
          sent_count: 0,
          failed_count: 0,
          status: 'draft',
          scheduled_at: '2025-01-10T12:00:00Z',
          started_at: null,
          completed_at: null,
          created_at: '2025-01-05T16:00:00Z'
        },
        {
          id: 4,
          message_text: '⏸️ Приостановленная рассылка для неактивных юзеров',
          message_photo: null,
          buttons_json: '[]',
          filter_type: 'inactive',
          filter_language: 'all',
          total_users: 800,
          sent_count: 400,
          failed_count: 10,
          status: 'paused',
          scheduled_at: null,
          started_at: '2025-01-05T10:00:00Z',
          completed_at: null,
          created_at: '2025-01-05T09:00:00Z'
        }
      ]);
    } catch (error) {
      console.error('Error fetching broadcasts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      // await broadcastsAPI.create(formData);
      console.log('Creating broadcast:', formData);
      setShowCreateModal(false);
      resetForm();
      fetchBroadcasts();
    } catch (error) {
      console.error('Error creating broadcast:', error);
    }
  };

  const handleStart = async (broadcast) => {
    try {
      // await broadcastsAPI.start(broadcast.id);
      console.log('Starting broadcast:', broadcast.id);
      fetchBroadcasts();
    } catch (error) {
      console.error('Error starting broadcast:', error);
    }
  };

  const handlePause = async (broadcast) => {
    try {
      // await broadcastsAPI.pause(broadcast.id);
      console.log('Pausing broadcast:', broadcast.id);
      fetchBroadcasts();
    } catch (error) {
      console.error('Error pausing broadcast:', error);
    }
  };

  const handleCancel = async () => {
    if (!selectedBroadcast) return;
    try {
      // await broadcastsAPI.cancel(selectedBroadcast.id);
      console.log('Cancelling broadcast:', selectedBroadcast.id);
      setShowConfirm(false);
      setSelectedBroadcast(null);
      fetchBroadcasts();
    } catch (error) {
      console.error('Error cancelling broadcast:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      message_text: '',
      message_photo: '',
      buttons_json: '[]',
      filter_type: 'all',
      filter_language: 'all',
      scheduled_at: ''
    });
  };

  const getStatusBadge = (status) => {
    const styles = {
      draft: 'badge-yellow',
      running: 'badge-blue',
      paused: 'badge-yellow',
      completed: 'badge-green',
      cancelled: 'badge-red'
    };
    const labels = {
      draft: 'Черновик',
      running: 'Отправка...',
      paused: 'Пауза',
      completed: 'Завершена',
      cancelled: 'Отменена'
    };
    return <span className={styles[status]}>{labels[status]}</span>;
  };

  const getFilterLabel = (type) => {
    const labels = {
      all: 'Все',
      active: 'С подпиской',
      inactive: 'Без подписки'
    };
    return labels[type] || type;
  };

  const getLanguageLabel = (lang) => {
    const labels = {
      all: 'Все',
      ru: '🇷🇺 RU',
      en: '🇬🇧 EN'
    };
    return labels[lang] || lang;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString('ru-RU');
  };

  const columns = [
    {
      key: 'message_text',
      label: 'Сообщение',
      render: (value) => (
        <div className="max-w-xs truncate" title={value}>
          {value}
        </div>
      )
    },
    {
      key: 'filter_type',
      label: 'Фильтр',
      render: (value, row) => (
        <div className="text-sm">
          <div>{getFilterLabel(value)}</div>
          <div className="text-gray-500">{getLanguageLabel(row.filter_language)}</div>
        </div>
      )
    },
    {
      key: 'progress',
      label: 'Прогресс',
      render: (_, row) => (
        <div className="text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>{row.sent_count}</span>
            {row.failed_count > 0 && (
              <>
                <XCircle className="w-4 h-4 text-red-500 ml-2" />
                <span>{row.failed_count}</span>
              </>
            )}
          </div>
          <div className="text-gray-500">из {row.total_users}</div>
          {row.total_users > 0 && (
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mt-1">
              <div 
                className="bg-primary-500 h-1.5 rounded-full" 
                style={{ width: `${(row.sent_count / row.total_users) * 100}%` }}
              />
            </div>
          )}
        </div>
      )
    },
    {
      key: 'status',
      label: 'Статус',
      render: (value) => getStatusBadge(value)
    },
    {
      key: 'created_at',
      label: 'Создана',
      render: (value) => formatDate(value)
    }
  ];

  const actions = [
    {
      icon: Eye,
      label: 'Просмотр',
      onClick: (row) => {
        setSelectedBroadcast(row);
        setShowViewModal(true);
      }
    },
    {
      icon: Play,
      label: 'Запустить',
      onClick: handleStart,
      show: (row) => row.status === 'draft' || row.status === 'paused'
    },
    {
      icon: Pause,
      label: 'Пауза',
      onClick: handlePause,
      show: (row) => row.status === 'running'
    },
    {
      icon: X,
      label: 'Отменить',
      onClick: (row) => {
        setSelectedBroadcast(row);
        setConfirmAction('cancel');
        setShowConfirm(true);
      },
      className: 'text-red-600 hover:text-red-700',
      show: (row) => row.status === 'running' || row.status === 'paused' || row.status === 'draft'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Рассылки
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Управление массовыми рассылками
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Создать рассылку
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Send className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Всего</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {broadcasts.length}
              </p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Завершено</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {broadcasts.filter(b => b.status === 'completed').length}
              </p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <Clock className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">В процессе</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {broadcasts.filter(b => b.status === 'running').length}
              </p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <Users className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Отправлено</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {broadcasts.reduce((sum, b) => sum + b.sent_count, 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        data={broadcasts}
        actions={actions}
        loading={loading}
      />

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          resetForm();
        }}
        title="Создать рассылку"
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="label">Текст сообщения *</label>
            <textarea
              value={formData.message_text}
              onChange={(e) => setFormData({ ...formData, message_text: e.target.value })}
              className="input min-h-[120px]"
              placeholder="Введите текст рассылки..."
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              Поддерживается HTML-разметка: &lt;b&gt;, &lt;i&gt;, &lt;a&gt;
            </p>
          </div>

          <div>
            <label className="label">Фото (file_id или URL)</label>
            <input
              type="text"
              value={formData.message_photo}
              onChange={(e) => setFormData({ ...formData, message_photo: e.target.value })}
              className="input"
              placeholder="Опционально"
            />
          </div>

          <div>
            <label className="label">Кнопки (JSON)</label>
            <textarea
              value={formData.buttons_json}
              onChange={(e) => setFormData({ ...formData, buttons_json: e.target.value })}
              className="input font-mono text-sm"
              placeholder='[{"text": "Кнопка", "url": "https://..."}]'
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Фильтр получателей</label>
              <select
                value={formData.filter_type}
                onChange={(e) => setFormData({ ...formData, filter_type: e.target.value })}
                className="input"
              >
                <option value="all">Все пользователи</option>
                <option value="active">С активной подпиской</option>
                <option value="inactive">Без подписки</option>
              </select>
            </div>

            <div>
              <label className="label">Язык</label>
              <select
                value={formData.filter_language}
                onChange={(e) => setFormData({ ...formData, filter_language: e.target.value })}
                className="input"
              >
                <option value="all">Все языки</option>
                <option value="ru">🇷🇺 Только русский</option>
                <option value="en">🇬🇧 Только английский</option>
              </select>
            </div>
          </div>

          <div>
            <label className="label">Запланировать на</label>
            <input
              type="datetime-local"
              value={formData.scheduled_at}
              onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
              className="input"
            />
            <p className="text-sm text-gray-500 mt-1">
              Оставьте пустым для ручного запуска
            </p>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              onClick={() => {
                setShowCreateModal(false);
                resetForm();
              }}
              className="btn-secondary"
            >
              Отмена
            </button>
            <button
              onClick={handleCreate}
              className="btn-primary"
              disabled={!formData.message_text.trim()}
            >
              Создать
            </button>
          </div>
        </div>
      </Modal>

      {/* View Modal */}
      <Modal
        isOpen={showViewModal}
        onClose={() => {
          setShowViewModal(false);
          setSelectedBroadcast(null);
        }}
        title="Детали рассылки"
        size="lg"
      >
        {selectedBroadcast && (
          <div className="space-y-4">
            <div>
              <label className="label">Статус</label>
              <div>{getStatusBadge(selectedBroadcast.status)}</div>
            </div>

            <div>
              <label className="label">Сообщение</label>
              <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg whitespace-pre-wrap">
                {selectedBroadcast.message_text}
              </div>
            </div>

            {selectedBroadcast.message_photo && (
              <div>
                <label className="label">Фото</label>
                <p className="text-gray-900 dark:text-white">{selectedBroadcast.message_photo}</p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Фильтр</label>
                <p className="text-gray-900 dark:text-white">
                  {getFilterLabel(selectedBroadcast.filter_type)}
                </p>
              </div>
              <div>
                <label className="label">Язык</label>
                <p className="text-gray-900 dark:text-white">
                  {getLanguageLabel(selectedBroadcast.filter_language)}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="label">Всего получателей</label>
                <p className="text-gray-900 dark:text-white">{selectedBroadcast.total_users}</p>
              </div>
              <div>
                <label className="label">Отправлено</label>
                <p className="text-green-600 dark:text-green-400 font-medium">
                  {selectedBroadcast.sent_count}
                </p>
              </div>
              <div>
                <label className="label">Ошибок</label>
                <p className="text-red-600 dark:text-red-400 font-medium">
                  {selectedBroadcast.failed_count}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Создана</label>
                <p className="text-gray-900 dark:text-white">
                  {formatDate(selectedBroadcast.created_at)}
                </p>
              </div>
              <div>
                <label className="label">Запущена</label>
                <p className="text-gray-900 dark:text-white">
                  {formatDate(selectedBroadcast.started_at)}
                </p>
              </div>
            </div>

            {selectedBroadcast.completed_at && (
              <div>
                <label className="label">Завершена</label>
                <p className="text-gray-900 dark:text-white">
                  {formatDate(selectedBroadcast.completed_at)}
                </p>
              </div>
            )}

            <div className="flex justify-end pt-4">
              <button
                onClick={() => {
                  setShowViewModal(false);
                  setSelectedBroadcast(null);
                }}
                className="btn-secondary"
              >
                Закрыть
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={showConfirm}
        onClose={() => {
          setShowConfirm(false);
          setSelectedBroadcast(null);
        }}
        onConfirm={handleCancel}
        title="Отменить рассылку?"
        message="Рассылка будет остановлена. Уже отправленные сообщения останутся."
        confirmText="Отменить рассылку"
        type="danger"
      />
    </div>
  );
}
