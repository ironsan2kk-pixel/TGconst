import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input, Checkbox } from '../../components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { Alert, Spinner } from '../../components/ui/Badge'
import tariffsApi from '../../api/tariffs'

export default function TariffEdit() {
  const { uuid, id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [channelId, setChannelId] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    price: '',
    duration_days: '',
    sort_order: '0',
    is_active: true,
  })

  useEffect(() => {
    loadTariff()
  }, [uuid, id])

  const loadTariff = async () => {
    try {
      const tariff = await tariffsApi.get(uuid, id)
      setChannelId(tariff.channel_id)
      setFormData({
        name: tariff.name || '',
        price: tariff.price?.toString() || '',
        duration_days: tariff.duration_days?.toString() || '',
        sort_order: tariff.sort_order?.toString() || '0',
        is_active: tariff.is_active ?? true,
      })
    } catch (err) {
      setError('Тариф не найден')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')

    try {
      await tariffsApi.update(uuid, id, {
        name: formData.name,
        price: parseFloat(formData.price),
        duration_days: parseInt(formData.duration_days),
        sort_order: parseInt(formData.sort_order),
        is_active: formData.is_active,
      })
      navigate(`/bots/${uuid}/channels/${channelId}/tariffs`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка сохранения')
    } finally {
      setSaving(false)
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
            Назад
          </Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Редактирование тарифа</h1>
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
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />

            <Input
              label="Цена (USD)"
              type="number"
              step="0.01"
              min="0"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              required
            />

            <Input
              label="Срок (дней)"
              type="number"
              min="1"
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

            <Button type="submit" loading={saving}>
              <Save className="w-4 h-4 mr-2" />
              Сохранить
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
