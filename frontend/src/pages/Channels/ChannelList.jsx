import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Plus, Hash, Tag, Trash2, Edit } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card, CardContent } from '../../components/ui/Card'
import { Badge, Spinner, Modal, EmptyState } from '../../components/ui/Badge'
import channelsApi from '../../api/channels'

export default function ChannelList() {
  const { uuid } = useParams()
  const [channels, setChannels] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleteModal, setDeleteModal] = useState(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    loadChannels()
  }, [uuid])

  const loadChannels = async () => {
    try {
      const data = await channelsApi.list(uuid)
      setChannels(data)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteModal) return
    setDeleting(true)
    try {
      await channelsApi.delete(uuid, deleteModal)
      await loadChannels()
    } finally {
      setDeleting(false)
      setDeleteModal(null)
    }
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
        <h1 className="text-2xl font-bold text-gray-900">Каналы</h1>
        <Link to={`/bots/${uuid}/channels/create`}>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Добавить канал
          </Button>
        </Link>
      </div>

      {channels.length === 0 ? (
        <Card>
          <CardContent>
            <EmptyState
              icon={Hash}
              title="Нет каналов"
              description="Добавьте канал для продажи подписок"
              action={
                <Link to={`/bots/${uuid}/channels/create`}>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Добавить канал
                  </Button>
                </Link>
              }
            />
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {channels.map((channel) => (
            <Card key={channel.id}>
              <CardContent className="py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Hash className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{channel.title}</h3>
                      <p className="text-sm text-gray-500">
                        {channel.channel_username || `ID: ${channel.channel_id}`}
                      </p>
                    </div>
                    <Badge variant={channel.is_active ? 'success' : 'default'}>
                      {channel.is_active ? 'Активен' : 'Неактивен'}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link to={`/bots/${uuid}/channels/${channel.id}/tariffs`}>
                      <Button variant="secondary" size="sm">
                        <Tag className="w-4 h-4 mr-2" />
                        Тарифы
                      </Button>
                    </Link>
                    <Link to={`/bots/${uuid}/channels/${channel.id}/edit`}>
                      <Button variant="ghost" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDeleteModal(channel.id)}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Modal
        isOpen={!!deleteModal}
        onClose={() => setDeleteModal(null)}
        title="Удаление канала"
      >
        <p className="text-gray-600 mb-6">
          Удалить канал и все связанные тарифы?
        </p>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => setDeleteModal(null)}>
            Отмена
          </Button>
          <Button variant="danger" onClick={handleDelete} loading={deleting}>
            Удалить
          </Button>
        </div>
      </Modal>
    </div>
  )
}
