import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Plus, Percent, Trash2, Edit } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card, CardContent } from '../../components/ui/Card'
import { Badge, Spinner, Modal, EmptyState } from '../../components/ui/Badge'
import promocodesApi from '../../api/promocodes'

export default function PromocodeList() {
  const { uuid } = useParams()
  const [promocodes, setPromocodes] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleteModal, setDeleteModal] = useState(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    loadPromocodes()
  }, [uuid])

  const loadPromocodes = async () => {
    try {
      const data = await promocodesApi.list(uuid)
      setPromocodes(data)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteModal) return
    setDeleting(true)
    try {
      await promocodesApi.delete(uuid, deleteModal)
      await loadPromocodes()
    } finally {
      setDeleting(false)
      setDeleteModal(null)
    }
  }

  const formatDiscount = (promo) => {
    if (promo.discount_percent) return `${promo.discount_percent}%`
    if (promo.discount_amount) return `$${promo.discount_amount}`
    return '—'
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
        <h1 className="text-2xl font-bold text-gray-900">Промокоды</h1>
        <Link to={`/bots/${uuid}/promocodes/create`}>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Создать промокод
          </Button>
        </Link>
      </div>

      {promocodes.length === 0 ? (
        <Card>
          <CardContent>
            <EmptyState
              icon={Percent}
              title="Нет промокодов"
              description="Создайте промокод для скидок"
              action={
                <Link to={`/bots/${uuid}/promocodes/create`}>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Создать промокод
                  </Button>
                </Link>
              }
            />
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {promocodes.map((promo) => (
            <Card key={promo.id}>
              <CardContent className="py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <Percent className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="font-mono font-bold text-gray-900">{promo.code}</h3>
                      <p className="text-sm text-gray-500">
                        Скидка: {formatDiscount(promo)} • Использований: {promo.used_count}/{promo.max_uses || '∞'}
                      </p>
                    </div>
                    <Badge variant={promo.is_active ? 'success' : 'default'}>
                      {promo.is_active ? 'Активен' : 'Неактивен'}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-2">
                    <Link to={`/bots/${uuid}/promocodes/${promo.id}/edit`}>
                      <Button variant="ghost" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDeleteModal(promo.id)}
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
        title="Удаление промокода"
      >
        <p className="text-gray-600 mb-6">Удалить этот промокод?</p>
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
