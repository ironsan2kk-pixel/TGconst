import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input, Checkbox } from '../../components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { Alert } from '../../components/ui/Badge'
import channelsApi from '../../api/channels'

export default function ChannelCreate() {
  const { uuid } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    channel_id: '',
    channel_username: '',
    title: '',
    is_active: true,
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await channelsApi.create(uuid, {
        ...formData,
        channel_id: parseInt(formData.channel_id),
      })
      navigate(`/bots/${uuid}/channels`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка создания канала')
    } finally {
      setLoading(false)
    }
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
        <h1 className="text-2xl font-bold text-gray-900">Новый канал</h1>
      </div>

      {error && <Alert type="error">{error}</Alert>}

      <Card>
        <CardHeader>
          <CardTitle>Настройки канала</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="ID канала"
              placeholder="-1001234567890"
              value={formData.channel_id}
              onChange={(e) => setFormData({ ...formData, channel_id: e.target.value })}
              required
            />

            <Input
              label="Username канала"
              placeholder="@mychannel"
              value={formData.channel_username}
              onChange={(e) => setFormData({ ...formData, channel_username: e.target.value })}
            />

            <Input
              label="Название"
              placeholder="VIP Канал"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />

            <Checkbox
              label="Активен"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
            />

            <div className="flex gap-3">
              <Button type="submit" loading={loading}>
                Добавить канал
              </Button>
              <Link to={`/bots/${uuid}/channels`}>
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
