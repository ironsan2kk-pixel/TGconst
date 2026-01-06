import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Plus, Send, Play, X, Trash2, Eye, Clock, CheckCircle, XCircle, RefreshCw } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card, CardContent } from '../../components/ui/Card'
import { Badge, Spinner, Modal, EmptyState } from '../../components/ui/Badge'
import { getBroadcasts, startBroadcast, cancelBroadcast, deleteBroadcast } from '../../api/broadcasts'

export default function BroadcastList() {
  const { uuid } = useParams()
  const [broadcasts, setBroadcasts] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(null)
  const [deleteModal, setDeleteModal] = useState(null)

  useEffect(() => {
    loadBroadcasts()
  }, [uuid])

  const loadBroadcasts = async () => {
    try {
      const data = await getBroadcasts(uuid)
      setBroadcasts(data)
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async (id) => {
    setActionLoading(id)
    try {
      await startBroadcast(uuid, id)
      await loadBroadcasts()
    } finally {
      setActionLoading(null)
    }
  }

  const handleCancel = async (id) => {
    setActionLoading(id)
    try {
      await cancelBroadcast(uuid, id)
      await loadBroadcasts()
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async () => {
    if (!deleteModal) return
    setActionLoading(deleteModal)
    try {
      await deleteBroadcast(uuid, deleteModal)
      await loadBroadcasts()
    } finally {
      setActionLoading(null)
      setDeleteModal(null)
    }
  }

  const getStatusBadge = (status) => {
    const styles = {
      pending: { variant: 'warning', icon: Clock, text: 'Ожидает' },
      running: { variant: 'info', icon: RefreshCw, text: 'Выполняется' },
      completed: { variant: 'success', icon: CheckCircle, text: 'Завершена' },
      cancelled: { variant: 'error', icon: XCircle, text: 'Отменена' },
    }
    const style = styles[status] || styles.pending
    const Icon = style.icon
    return (
      <Badge variant={style.variant} className="flex items-center gap-1">
        <Icon className={`w-3 h-3 ${status === 'running' ? 'animate-spin' : ''}`} />
        {style.text}
      </Badge>
    )
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Рассылки</h1>
        <Link to={`/bots/${uuid}/broadcasts/create`}>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Новая рассылка
          </Button>
        </Link>
      </div>

      {broadcasts.length === 0 ? (
        <Card>
          <CardContent>
            <EmptyState
              icon={Send}
              title="Нет рассылок"
              description="Создайте рассылку для отправки сообщений пользователям"
              action={
                <Link to={`/bots/${uuid}/broadcasts/create`}>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Новая рассылка
                  </Button>
                </Link>
              }
            />
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {broadcasts.map((broadcast) => {
            const progress = broadcast.total_users > 0 
              ? Math.round(((broadcast.sent_count + broadcast.failed_count) / broadcast.total_users) * 100)
              : 0

            return (
              <Card key={broadcast.id}>
                <CardContent className="py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-gray-900">
                          Рассылка #{broadcast.id}
                        </h3>
                        {getStatusBadge(broadcast.status)}
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                        {broadcast.message_text}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>Всего: {broadcast.total_users}</span>
                        <span className="text-green-600">Отправлено: {broadcast.sent_count}</span>
                        <span className="text-red-600">Ошибок: {broadcast.failed_count}</span>
                      </div>
                      {broadcast.status === 'running' && (
                        <div className="mt-2">
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div 
                              className="bg-primary-600 h-1.5 rounded-full transition-all"
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      {broadcast.status === 'pending' && (
                        <Button
                          variant="success"
                          size="sm"
                          onClick={() => handleStart(broadcast.id)}
                          loading={actionLoading === broadcast.id}
                        >
                          <Play className="w-4 h-4" />
                        </Button>
                      )}
                      {broadcast.status === 'running' && (
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleCancel(broadcast.id)}
                          loading={actionLoading === broadcast.id}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      )}
                      <Link to={`/bots/${uuid}/broadcasts/${broadcast.id}`}>
                        <Button variant="ghost" size="sm">
                          <Eye className="w-4 h-4" />
                        </Button>
                      </Link>
                      {(broadcast.status === 'completed' || broadcast.status === 'cancelled') && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeleteModal(broadcast.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      <Modal
        isOpen={!!deleteModal}
        onClose={() => setDeleteModal(null)}
        title="Удаление рассылки"
      >
        <p className="text-gray-600 mb-6">Удалить эту рассылку?</p>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => setDeleteModal(null)}>
            Отмена
          </Button>
          <Button variant="danger" onClick={handleDelete} loading={!!actionLoading}>
            Удалить
          </Button>
        </div>
      </Modal>
    </div>
  )
}
