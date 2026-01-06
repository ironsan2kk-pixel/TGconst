import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input, Checkbox } from '../../components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { Alert } from '../../components/ui/Badge'
import tariffsApi from '../../api/tariffs'

export default function TariffCreate() {
  const { uuid, channelId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    price: '',
    duration_days: '',
    sort_order: '0',
    is_active: true,
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await tariffsApi.create(uuid, channelId, {
        name: formData.name,
        price: parseFloat(formData.price),
        duration_days: parseInt(formData.duration_days),
        sort_order: parseInt(formData.sort_order),
        is_active: formData.is_active,
      })
      navigate(`/bots/${uuid}/channels/${channelId}/tariffs`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка создания тарифа')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to={`/bots/${uuid}/channels/${channelId}/tariffs`}>
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад
          </Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Новый тариф</h1>
      </div>

      {error && <Alert type="error">{error}</Alert>}

      <Card>
        <CardHeader>
          <CardTitle>Настройки тарифа</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Название"
              placeholder="1 месяц"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />

            <Input
              label="Цена (USD)"
              type="number"
              step="0.01"
              min="0"
              placeholder="10.00"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              required
            />

            <Input
              label="Срок (дней)"
              type="number"
              min="1"
              placeholder="30"
              value={formData.duration_days}
              onChange={(e) => setFormData({ ...formData, duration_days: e.target.value })}
              required
            />

            <Input
              label="Сортировка"
              type="number"
              value={formData.sort_order}
              onChange={(e) => setFormData({ ...formData, sort_order: e.target.value })}
            />

            <Checkbox
              label="Активен"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
            />

            <div className="flex gap-3">
              <Button type="submit" loading={loading}>
                Создать тариф
              </Button>
              <Link to={`/bots/${uuid}/channels/${channelId}/tariffs`}>
                <Button type="button" variant="secondary">
                  Отмена
                </Button>
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
