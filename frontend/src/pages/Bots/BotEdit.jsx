import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input, Textarea } from '../../components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { Alert, Spinner } from '../../components/ui/Badge'
import botsApi from '../../api/bots'

export default function BotEdit() {
  const { uuid } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    bot_token: '',
    cryptobot_token: '',
    welcome_message: '',
    support_url: '',
  })

  useEffect(() => {
    loadBot()
  }, [uuid])

  const loadBot = async () => {
    try {
      const bot = await botsApi.get(uuid)
      setFormData({
        name: bot.name || '',
        bot_token: bot.bot_token || '',
        cryptobot_token: bot.cryptobot_token || '',
        welcome_message: bot.welcome_message || '',
        support_url: bot.support_url || '',
      })
    } catch (err) {
      setError('Бот не найден')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      await botsApi.update(uuid, formData)
      setSuccess('Настройки сохранены')
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
        <Link to="/bots">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад
          </Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Редактирование бота</h1>
      </div>

      {error && <Alert type="error">{error}</Alert>}
      {success && <Alert type="success">{success}</Alert>}

      <Card>
        <CardHeader>
          <CardTitle>Настройки бота</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Название бота"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />

            <Input
              label="Токен бота"
              value={formData.bot_token}
              onChange={(e) => setFormData({ ...formData, bot_token: e.target.value })}
              required
            />

            <Input
              label="Токен CryptoBot"
              value={formData.cryptobot_token}
              onChange={(e) => setFormData({ ...formData, cryptobot_token: e.target.value })}
              required
            />

            <Textarea
              label="Приветственное сообщение"
              rows={3}
              value={formData.welcome_message}
              onChange={(e) => setFormData({ ...formData, welcome_message: e.target.value })}
            />

            <Input
              label="Ссылка на поддержку"
              value={formData.support_url}
              onChange={(e) => setFormData({ ...formData, support_url: e.target.value })}
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
