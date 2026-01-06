import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Bot, Users, CreditCard, TrendingUp } from 'lucide-react'
import { Card, CardContent } from '../components/ui/Card'
import { Spinner } from '../components/ui/Badge'
import botsApi from '../api/bots'

export default function Dashboard() {
  const [bots, setBots] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBots()
  }, [])

  const loadBots = async () => {
    try {
      const data = await botsApi.list()
      setBots(data)
    } finally {
      setLoading(false)
    }
  }

  const activeBots = bots.filter(b => b.is_active).length
  const totalBots = bots.length

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="py-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 p-3 bg-primary-100 rounded-lg">
                <Bot className="w-6 h-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Всего ботов</p>
                <p className="text-2xl font-semibold text-gray-900">{totalBots}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="py-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 p-3 bg-green-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Активных</p>
                <p className="text-2xl font-semibold text-gray-900">{activeBots}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="py-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 p-3 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Пользователей</p>
                <p className="text-2xl font-semibold text-gray-900">—</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="py-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 p-3 bg-yellow-100 rounded-lg">
                <CreditCard className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Платежей</p>
                <p className="text-2xl font-semibold text-gray-900">—</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Последние боты</h2>
            <Link to="/bots" className="text-sm text-primary-600 hover:text-primary-700">
              Все боты →
            </Link>
          </div>

          {bots.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              Нет созданных ботов. <Link to="/bots/create" className="text-primary-600">Создать первого</Link>
            </p>
          ) : (
            <div className="space-y-3">
              {bots.slice(0, 5).map((bot) => (
                <Link
                  key={bot.uuid}
                  to={`/bots/${bot.uuid}/edit`}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
                >
                  <div className="flex items-center gap-3">
                    <Bot className="w-5 h-5 text-gray-400" />
                    <span className="font-medium text-gray-900">{bot.name}</span>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    bot.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {bot.is_active ? 'Активен' : 'Остановлен'}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
