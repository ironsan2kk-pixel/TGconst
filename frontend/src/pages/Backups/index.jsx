import { useState, useEffect } from 'react';
import { 
  Database, 
  Download, 
  Trash2,
  RefreshCw,
  Clock,
  HardDrive,
  AlertCircle,
  CheckCircle,
  Plus
} from 'lucide-react';
import { ConfirmDialog } from '../../components';
// import { backupAPI } from '../../api/client';

export default function Backups() {
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState(null);
  const [actionStatus, setActionStatus] = useState(null);

  useEffect(() => {
    fetchBackups();
  }, []);

  const fetchBackups = async () => {
    setLoading(true);
    try {
      // const response = await backupAPI.getAll();
      // setBackups(response.data);
      
      // Mock data
      setBackups([
        {
          id: 1,
          filename: 'bot_backup_2025-01-06_12-00-00.db',
          size: 2457600, // bytes
          created_at: '2025-01-06T12:00:00Z',
          type: 'auto'
        },
        {
          id: 2,
          filename: 'bot_backup_2025-01-05_12-00-00.db',
          size: 2396160,
          created_at: '2025-01-05T12:00:00Z',
          type: 'auto'
        },
        {
          id: 3,
          filename: 'bot_backup_2025-01-04_18-30-00.db',
          size: 2334720,
          created_at: '2025-01-04T18:30:00Z',
          type: 'manual'
        },
        {
          id: 4,
          filename: 'bot_backup_2025-01-04_12-00-00.db',
          size: 2273280,
          created_at: '2025-01-04T12:00:00Z',
          type: 'auto'
        },
        {
          id: 5,
          filename: 'bot_backup_2025-01-03_12-00-00.db',
          size: 2211840,
          created_at: '2025-01-03T12:00:00Z',
          type: 'auto'
        }
      ]);
    } catch (error) {
      console.error('Error fetching backups:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    setCreating(true);
    setActionStatus(null);
    try {
      // await backupAPI.create();
      console.log('Creating backup...');
      
      // Mock: add new backup
      const newBackup = {
        id: Date.now(),
        filename: `bot_backup_${new Date().toISOString().slice(0, 19).replace(/[T:]/g, '-').replace(/-/g, (m, i) => i < 10 ? '-' : '_')}.db`,
        size: Math.floor(Math.random() * 1000000) + 2000000,
        created_at: new Date().toISOString(),
        type: 'manual'
      };
      setBackups([newBackup, ...backups]);
      setActionStatus({ type: 'success', message: 'Бэкап успешно создан!' });
    } catch (error) {
      console.error('Error creating backup:', error);
      setActionStatus({ type: 'error', message: 'Ошибка создания бэкапа' });
    } finally {
      setCreating(false);
      setTimeout(() => setActionStatus(null), 5000);
    }
  };

  const handleDownload = async (backup) => {
    try {
      // const response = await backupAPI.download(backup.id);
      // Create blob and download
      console.log('Downloading backup:', backup.filename);
      
      // Mock download
      const link = document.createElement('a');
      link.href = '#';
      link.download = backup.filename;
      // link.click();
      
      setActionStatus({ type: 'success', message: `Скачивание ${backup.filename}...` });
      setTimeout(() => setActionStatus(null), 3000);
    } catch (error) {
      console.error('Error downloading backup:', error);
      setActionStatus({ type: 'error', message: 'Ошибка скачивания' });
    }
  };

  const handleDelete = async () => {
    if (!selectedBackup) return;
    try {
      // await backupAPI.delete(selectedBackup.id);
      console.log('Deleting backup:', selectedBackup.filename);
      setBackups(backups.filter(b => b.id !== selectedBackup.id));
      setShowConfirm(false);
      setSelectedBackup(null);
      setActionStatus({ type: 'success', message: 'Бэкап удалён' });
      setTimeout(() => setActionStatus(null), 3000);
    } catch (error) {
      console.error('Error deleting backup:', error);
      setActionStatus({ type: 'error', message: 'Ошибка удаления' });
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const totalSize = backups.reduce((sum, b) => sum + b.size, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Бэкапы базы данных
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Резервные копии для восстановления
          </p>
        </div>
        <button
          onClick={handleCreateBackup}
          className="btn-primary flex items-center gap-2"
          disabled={creating}
        >
          {creating ? (
            <RefreshCw className="w-5 h-5 animate-spin" />
          ) : (
            <Plus className="w-5 h-5" />
          )}
          Создать бэкап
        </button>
      </div>

      {/* Status Message */}
      {actionStatus && (
        <div className={`p-4 rounded-lg flex items-center gap-3 ${
          actionStatus.type === 'success' 
            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' 
            : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
        }`}>
          {actionStatus.type === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          {actionStatus.message}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Database className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Всего бэкапов</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {backups.length}
              </p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <HardDrive className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Общий размер</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {formatSize(totalSize)}
              </p>
            </div>
          </div>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <Clock className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Последний</p>
              <p className="text-xl font-bold text-gray-900 dark:text-white">
                {backups.length > 0 ? formatDate(backups[0].created_at).split(',')[0] : '—'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="card p-4 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
          <div className="text-sm text-blue-800 dark:text-blue-200">
            <strong>Автоматические бэкапы</strong> создаются каждый день в 12:00 UTC.
            <br />
            Хранятся последние 7 автоматических бэкапов. Ручные бэкапы не удаляются автоматически.
          </div>
        </div>
      </div>

      {/* Backup List */}
      <div className="card overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="font-medium text-gray-900 dark:text-white">
            Список бэкапов
          </h2>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <RefreshCw className="w-8 h-8 text-primary-500 animate-spin mx-auto" />
          </div>
        ) : backups.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            Нет бэкапов. Создайте первый!
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {backups.map(backup => (
              <div 
                key={backup.id}
                className="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50"
              >
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                    <Database className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 dark:text-white">
                        {backup.filename}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        backup.type === 'auto' 
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                          : 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                      }`}>
                        {backup.type === 'auto' ? 'Авто' : 'Ручной'}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {formatDate(backup.created_at)}
                      </span>
                      <span className="flex items-center gap-1">
                        <HardDrive className="w-4 h-4" />
                        {formatSize(backup.size)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDownload(backup)}
                    className="p-2 text-gray-500 hover:text-primary-600 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg"
                    title="Скачать"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => {
                      setSelectedBackup(backup);
                      setShowConfirm(true);
                    }}
                    className="p-2 text-gray-500 hover:text-red-600 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg"
                    title="Удалить"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Restore Info */}
      <div className="card p-6">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Восстановление из бэкапа
        </h2>
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <p className="text-gray-600 dark:text-gray-400">
            Для восстановления базы данных из бэкапа:
          </p>
          <ol className="text-gray-600 dark:text-gray-400 space-y-2 mt-3">
            <li>Остановите бота и админ-панель</li>
            <li>Скачайте нужный бэкап</li>
            <li>Переименуйте файл в <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">bot.db</code></li>
            <li>Замените файл в папке <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">data/</code></li>
            <li>Запустите бота и админ-панель</li>
          </ol>
        </div>
      </div>

      {/* Confirm Delete */}
      <ConfirmDialog
        isOpen={showConfirm}
        onClose={() => {
          setShowConfirm(false);
          setSelectedBackup(null);
        }}
        onConfirm={handleDelete}
        title="Удалить бэкап?"
        message={`Файл "${selectedBackup?.filename}" будет удалён безвозвратно.`}
        confirmText="Удалить"
        type="danger"
      />
    </div>
  );
}
