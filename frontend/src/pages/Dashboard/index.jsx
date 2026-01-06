import { useState, useEffect } from 'react'
import { Users, CreditCard, DollarSign, TrendingUp } from 'lucide-react'
import { StatsCard, Chart } from '../../components'
import { dashboardAPI } from '../../api/client'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeSubscriptions: 0,
    todayRevenue: 0,
    monthRevenue: 0,
    usersChange: '0%',
    subscriptionsChange: '0%',
    todayChange: '0%',
    monthChange: '0%'
  })
  const [chartData, setChartData] = useState([])
  const [recentEvents, setRecentEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setError(null)
      const [statsRes, chartRes, eventsRes] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getChartData(30),
        dashboardAPI.getRecentEvents(10)
      ])
      setStats(statsRes.data)
      setChartData(chartRes.data)
      setRecentEvents(eventsRes.data)
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      setError('Не удалось загрузить данные. Проверьте что backend запущен.')
    } finally {
      setLoading(false)
    }
  }

  const getEventIcon = (type) => {
    switch (type) {
      case 'payment': return '💰'
      case 'registration': return '👤'
      case 'subscription_expired': return '⏰'
      default: return '📌'
    }
  }

  const getEventText = (event) => {
    switch (event.type) {
      case 'payment': return `${event.user} оплатил $${event.amount}`
      case 'registration': return `${event.user} зарегистрировался`
      case 'subscription_expired': return `Подписка ${event.user} истекла`
      default: return event.type
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <p className="text-red-500 mb-4">{error}</p>
        <button onClick={loadData} className="btn-primary">
          Попробовать снова
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400">Обзор статистики бота</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Всего пользователей"
          value={stats.totalUsers?.toLocaleString() || '0'}
          change={stats.usersChange}
          changeType="increase"
          icon={Users}
          color="blue"
        />
        <StatsCard
          title="Активных подписок"
          value={stats.activeSubscriptions?.toLocaleString() || '0'}
          change={stats.subscriptionsChange}
          changeType="increase"
          icon={CreditCard}
          color="green"
        />
        <StatsCard
          title="Доход сегодня"
          value={`$${(stats.todayRevenue || 0).toFixed(2)}`}
          change={stats.todayChange}
          changeType="increase"
          icon={DollarSign}
          color="yellow"
        />
        <StatsCard
          title="Доход за месяц"
          value={`$${(stats.monthRevenue || 0).toFixed(2)}`}
          change={stats.monthChange}
          changeType="increase"
          icon={TrendingUp}
          color="primary"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Chart
          title="Доход по дням (USDT)"
          data={chartData}
          type="area"
          dataKey="revenue"
          xAxisKey="date"
          color="#3b82f6"
          height={280}
        />
        <Chart
          title="Новые пользователи"
          data={chartData}
          type="bar"
          dataKey="users"
          xAxisKey="date"
          color="#10b981"
          height={280}
        />
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Последние события
        </h3>
        {recentEvents.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400 text-center py-4">
            Пока нет событий
          </p>
        ) : (
          <div className="space-y-3">
            {recentEvents.map(event => (
              <div 
                key={event.id}
                className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50"
              >
                <span className="text-xl">{getEventIcon(event.type)}</span>
                <div className="flex-1">
                  <p className="text-sm text-gray-900 dark:text-white">
                    {getEventText(event)}
                  </p>
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {event.time}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
