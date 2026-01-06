import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Plus, Tag, Trash2, Edit, ArrowLeft } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card, CardContent } from '../../components/ui/Card'
import { Badge, Spinner, Modal, EmptyState } from '../../components/ui/Badge'
import tariffsApi from '../../api/tariffs'

export default function TariffList() {
  const { uuid, channelId } = useParams()
  const [tariffs, setTariffs] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleteModal, setDeleteModal] = useState(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    loadTariffs()
  }, [uuid, channelId])

  const loadTariffs = async () => {
    try {
      const data = await tariffsApi.list(uuid, channelId)
      setTariffs(data)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteModal) return
    setDeleting(true)
    try {
      await tariffsApi.delete(uuid, deleteModal)
      await loadTariffs()
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
      <div className="flex items-center gap-4">
        <Link to={`/bots/${uuid}/channels`}>
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Каналы
          </Button>
        </Link>
      </div>

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Тарифы</h1>
        <Link to={`/bots/${uuid}/channels/${channelId}/tariffs/create`}>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Добавить тариф
          </Button>
        </Link>
      </div>

      {tariffs.length === 0 ? (
        <Card>
          <CardContent>
            <EmptyState
              icon={Tag}
              title="Нет тарифов"
              description="Добавьте тарифы для этого канала"
              action={
                <Link to={`/bots/${uuid}/channels/${channelId}/tariffs/create`}>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Добавить тариф
                  </Button>
                </Link>
              }
            />
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {tariffs.map((tariff) => (
            <Card key={tariff.id}>
              <CardContent className="py-4">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-gray-900">{tariff.name}</h3>
                  <Badge variant={tariff.is_active ? 'success' : 'default'}>
                    {tariff.is_active ? 'Активен' : 'Неактивен'}
                  </Badge>
                </div>
                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  <p>Цена: <span className="font-medium text-gray-900">${tariff.price}</span></p>
                  <p>Срок: <span className="font-medium text-gray-900">{tariff.duration_days} дней</span></p>
                </div>
                <div className="flex gap-2">
                  <Link to={`/bots/${uuid}/tariffs/${tariff.id}/edit`} className="flex-1">
                    <Button variant="secondary" size="sm" className="w-full">
                      <Edit className="w-4 h-4 mr-1" />
                      Изменить
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setDeleteModal(tariff.id)}
                  >
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Modal
        isOpen={!!deleteModal}
        onClose={() => setDeleteModal(null)}
        title="Удаление тарифа"
      >
        <p className="text-gray-600 mb-6">Удалить этот тариф?</p>
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
