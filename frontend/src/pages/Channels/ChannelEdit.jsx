import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input, Checkbox } from '../../components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { Alert, Spinner } from '../../components/ui/Badge'
import channelsApi from '../../api/channels'

export default function ChannelEdit() {
  const { uuid, id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    channel_id: '',
    channel_username: '',
    title: '',
    is_active: true,
  })

  useEffect(() => {
    loadChannel()
  }, [uuid, id])

  const loadChannel = async () => {
    try {
      const channel = await channelsApi.get(uuid, id)
      setFormData({
        channel_id: channel.channel_id?.toString() || '',
        channel_username: channel.channel_username || '',
        title: channel.title || '',
        is_active: channel.is_active ?? true,
      })
    } catch (err) {
      setError('Канал не найден')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')

    try {
      await channelsApi.update(uuid, id, {
        ...formData,
        channel_id: parseInt(formData.channel_id),
      })
      navigate(`/bots/${uuid}/channels`)
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
        <h1 className="text-2xl font-bold text-gray-900">Редактирование канала</h1>
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
              value={formData.channel_id}
              onChange={(e) => setFormData({ ...formData, channel_id: e.target.value })}
              required
            />

            <Input
              label="Username канала"
              value={formData.channel_username}
              onChange={(e) => setFormData({ ...formData, channel_username: e.target.value })}
            />

            <Input
              label="Название"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
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
