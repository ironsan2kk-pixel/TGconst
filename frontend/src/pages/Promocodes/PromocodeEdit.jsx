import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input, Checkbox } from '../../components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { Alert, Spinner } from '../../components/ui/Badge'
import promocodesApi from '../../api/promocodes'

export default function PromocodeEdit() {
  const { uuid, id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    code: '',
    discount_percent: '',
    discount_amount: '',
    max_uses: '',
    valid_until: '',
    is_active: true,
  })

  useEffect(() => {
    loadPromocode()
  }, [uuid, id])

  const loadPromocode = async () => {
    try {
      const promo = await promocodesApi.get(uuid, id)
      setFormData({
        code: promo.code || '',
        discount_percent: promo.discount_percent?.toString() || '',
        discount_amount: promo.discount_amount?.toString() || '',
        max_uses: promo.max_uses?.toString() || '',
        valid_until: promo.valid_until ? promo.valid_until.slice(0, 16) : '',
        is_active: promo.is_active ?? true,
      })
    } catch (err) {
      setError('Промокод не найден')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')

    try {
      await promocodesApi.update(uuid, id, {
        code: formData.code.toUpperCase(),
        discount_percent: formData.discount_percent ? parseInt(formData.discount_percent) : null,
        discount_amount: formData.discount_amount ? parseFloat(formData.discount_amount) : null,
        max_uses: formData.max_uses ? parseInt(formData.max_uses) : null,
        valid_until: formData.valid_until || null,
        is_active: formData.is_active,
      })
      navigate(`/bots/${uuid}/promocodes`)
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
        <Link to={`/bots/${uuid}/promocodes`}>
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад
          </Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Редактирование промокода</h1>
      </div>

      {error && <Alert type="error">{error}</Alert>}

      <Card>
        <CardHeader>
          <CardTitle>Настройки промокода</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Код"
              value={formData.code}
              onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
              required
            />

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Скидка (%)"
                type="number"
                min="1"
                max="100"
                value={formData.discount_percent}
                onChange={(e) => setFormData({ ...formData, discount_percent: e.target.value, discount_amount: '' })}
              />

              <Input
                label="Фикс. скидка (USD)"
                type="number"
                step="0.01"
                min="0"
                value={formData.discount_amount}
                onChange={(e) => setFormData({ ...formData, discount_amount: e.target.value, discount_percent: '' })}
              />
            </div>

            <Input
              label="Лимит использований"
              type="number"
              min="1"
              value={formData.max_uses}
              onChange={(e) => setFormData({ ...formData, max_uses: e.target.value })}
            />

            <Input
              label="Действует до"
              type="datetime-local"
              value={formData.valid_until}
              onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })}
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
