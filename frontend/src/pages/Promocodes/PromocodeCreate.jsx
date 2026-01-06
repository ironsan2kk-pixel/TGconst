import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input, Checkbox } from '../../components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { Alert } from '../../components/ui/Badge'
import promocodesApi from '../../api/promocodes'

export default function PromocodeCreate() {
  const { uuid } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    code: '',
    discount_percent: '',
    discount_amount: '',
    max_uses: '',
    valid_until: '',
    is_active: true,
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    if (!formData.discount_percent && !formData.discount_amount) {
      setError('Укажите скидку в процентах или фиксированную сумму')
      setLoading(false)
      return
    }

    try {
      await promocodesApi.create(uuid, {
        code: formData.code.toUpperCase(),
        discount_percent: formData.discount_percent ? parseInt(formData.discount_percent) : null,
        discount_amount: formData.discount_amount ? parseFloat(formData.discount_amount) : null,
        max_uses: formData.max_uses ? parseInt(formData.max_uses) : null,
        valid_until: formData.valid_until || null,
        is_active: formData.is_active,
      })
      navigate(`/bots/${uuid}/promocodes`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка создания промокода')
    } finally {
      setLoading(false)
    }
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
        <h1 className="text-2xl font-bold text-gray-900">Новый промокод</h1>
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
              placeholder="SAVE20"
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
                placeholder="20"
                value={formData.discount_percent}
                onChange={(e) => setFormData({ ...formData, discount_percent: e.target.value, discount_amount: '' })}
              />

              <Input
                label="Фикс. скидка (USD)"
                type="number"
                step="0.01"
                min="0"
                placeholder="5.00"
                value={formData.discount_amount}
                onChange={(e) => setFormData({ ...formData, discount_amount: e.target.value, discount_percent: '' })}
              />
            </div>

            <Input
              label="Лимит использований"
              type="number"
              min="1"
              placeholder="Без лимита"
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

            <div className="flex gap-3">
              <Button type="submit" loading={loading}>
                Создать промокод
              </Button>
              <Link to={`/bots/${uuid}/promocodes`}>
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
