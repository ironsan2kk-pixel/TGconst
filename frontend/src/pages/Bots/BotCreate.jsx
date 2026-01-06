import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input, Textarea } from '../../components/ui/Input'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { Alert } from '../../components/ui/Badge'
import botsApi from '../../api/bots'

export default function BotCreate() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    bot_token: '',
    cryptobot_token: '',
    welcome_message: 'Добро пожаловать! Выберите канал для подписки.',
    support_url: '',
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const bot = await botsApi.create(formData)
      navigate(`/bots/${bot.uuid}/channels`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка создания бота')
    } finally {
      setLoading(false)
    }
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
        <h1 className="text-2xl font-bold text-gray-900">Новый бот</h1>
      </div>

      {error && <Alert type="error">{error}</Alert>}

      <Card>
        <CardHeader>
          <CardTitle>Настройки бота</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Название бота"
              placeholder="Мой магазин подписок"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />

            <Input
              label="Токен бота (от @BotFather)"
              placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
              value={formData.bot_token}
              onChange={(e) => setFormData({ ...formData, bot_token: e.target.value })}
              required
            />

            <Input
              label="Токен CryptoBot (от @CryptoBot)"
              placeholder="12345:ABCdefGHIjklMNO"
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
              placeholder="https://t.me/support"
              value={formData.support_url}
              onChange={(e) => setFormData({ ...formData, support_url: e.target.value })}
            />

            <div className="flex gap-3">
              <Button type="submit" loading={loading}>
                Создать бота
              </Button>
              <Link to="/bots">
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
