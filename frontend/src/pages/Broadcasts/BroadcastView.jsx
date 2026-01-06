import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Play, X, Trash2, RefreshCw, Users, CheckCircle, XCircle, Clock } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge, Alert, Spinner, Modal } from '../../components/ui/Badge';
import { getBroadcast, startBroadcast, cancelBroadcast, deleteBroadcast, getBroadcastStats } from '../../api/broadcasts';

export default function BroadcastView() {
  const { uuid, id } = useParams();
  const navigate = useNavigate();
  const [broadcast, setBroadcast] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const fetchData = async () => {
    try {
      const [broadcastData, statsData] = await Promise.all([
        getBroadcast(uuid, id),
        getBroadcastStats(uuid, id).catch(() => null)
      ]);
      setBroadcast(broadcastData);
      setStats(statsData);
    } catch (err) {
      setError('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Автообновление для активных рассылок
    const interval = setInterval(() => {
      if (broadcast?.status === 'running') {
        fetchData();
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [uuid, id, broadcast?.status]);

  const handleStart = async () => {
    setActionLoading(true);
    try {
      await startBroadcast(uuid, id);
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка запуска');
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    setActionLoading(true);
    try {
      await cancelBroadcast(uuid, id);
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка отмены');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    setActionLoading(true);
    try {
      await deleteBroadcast(uuid, id);
      navigate(`/bots/${uuid}/broadcasts`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка удаления');
    } finally {
      setActionLoading(false);
      setShowDeleteModal(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: { variant: 'warning', icon: Clock, text: 'Ожидает' },
      running: { variant: 'info', icon: RefreshCw, text: 'Выполняется' },
      completed: { variant: 'success', icon: CheckCircle, text: 'Завершена' },
      cancelled: { variant: 'error', icon: XCircle, text: 'Отменена' },
    };
    const style = styles[status] || styles.pending;
    const Icon = style.icon;
    return (
      <Badge variant={style.variant} className="flex items-center gap-1">
        <Icon className={`w-4 h-4 ${status === 'running' ? 'animate-spin' : ''}`} />
        {style.text}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!broadcast) {
    return <Alert type="error">Рассылка не найдена</Alert>;
  }

  const progress = broadcast.total_users > 0 
    ? Math.round(((broadcast.sent_count + broadcast.failed_count) / broadcast.total_users) * 100)
    : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to={`/bots/${uuid}/broadcasts`}>
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Назад
            </Button>
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Рассылка #{broadcast.id}</h1>
          {getStatusBadge(broadcast.status)}
        </div>
        
        <div className="flex gap-2">
          {broadcast.status === 'pending' && (
            <Button onClick={handleStart} loading={actionLoading}>
              <Play className="w-4 h-4 mr-2" />
              Запустить
            </Button>
          )}
          {broadcast.status === 'running' && (
            <Button variant="secondary" onClick={handleCancel} loading={actionLoading}>
              <X className="w-4 h-4 mr-2" />
              Остановить
            </Button>
          )}
          {(broadcast.status === 'completed' || broadcast.status === 'cancelled') && (
            <Button variant="danger" onClick={() => setShowDeleteModal(true)}>
              <Trash2 className="w-4 h-4 mr-2" />
              Удалить
            </Button>
          )}
        </div>
      </div>

      {error && <Alert type="error">{error}</Alert>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Статистика */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Статистика
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-600">Всего получателей:</span>
              <span className="font-medium">{broadcast.total_users}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Отправлено:</span>
              <span className="font-medium text-green-600">{broadcast.sent_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Ошибок:</span>
              <span className="font-medium text-red-600">{broadcast.failed_count}</span>
            </div>
            
            {broadcast.status === 'running' && (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Прогресс</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {broadcast.started_at && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Начало:</span>
                <span>{new Date(broadcast.started_at).toLocaleString('ru')}</span>
              </div>
            )}
            {broadcast.completed_at && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Завершение:</span>
                <span>{new Date(broadcast.completed_at).toLocaleString('ru')}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Сообщение */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Сообщение</CardTitle>
          </CardHeader>
          <CardContent>
            {broadcast.message_photo && (
              <img 
                src={broadcast.message_photo} 
                alt="Broadcast" 
                className="max-w-md rounded-lg mb-4"
              />
            )}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-800 whitespace-pre-wrap">{broadcast.message_text}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Дополнительная статистика */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Детальная статистика</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-600">{stats.delivered || 0}</div>
                <div className="text-sm text-green-700">Доставлено</div>
              </div>
              <div className="bg-red-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-600">{stats.blocked || 0}</div>
                <div className="text-sm text-red-700">Заблокировали</div>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-yellow-600">{stats.errors || 0}</div>
                <div className="text-sm text-yellow-700">Ошибки</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {broadcast.total_users > 0 
                    ? Math.round((stats.delivered / broadcast.total_users) * 100) 
                    : 0}%
                </div>
                <div className="text-sm text-blue-700">Успешность</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Модалка удаления */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Удаление рассылки"
      >
        <p className="text-gray-600 mb-6">
          Вы уверены, что хотите удалить эту рассылку? Это действие нельзя отменить.
        </p>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Отмена
          </Button>
          <Button variant="danger" onClick={handleDelete} loading={actionLoading}>
            Удалить
          </Button>
        </div>
      </Modal>
    </div>
  );
}
