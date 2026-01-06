import { useState, useEffect } from 'react'
import { Users, CreditCard, DollarSign, TrendingUp } from 'lucide-react'
import { StatsCard, Chart } from '../../components'
import { dashboardAPI } from '../../api/client'

// Mock data for demo
const mockStats = {
  totalUsers: 1247,
  activeSubscriptions: 384,
  todayRevenue: 125.50,
  monthRevenue: 4820.00,
  usersChange: '+12%',
  subscriptionsChange: '+5%',
  todayChange: '+18%',
  monthChange: '+23%'
}

const mockChartData = Array.from({ length: 30 }, (_, i) => {
  const date = new Date()
  date.setDate(date.getDate() - (29 - i))
  return {
    date: date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' }),
    revenue: Math.floor(Math.random() * 200) + 50,
    users: Math.floor(Math.random() * 20) + 5
  }
})

const mockRecentEvents = [
  { id: 1, type: 'payment', user: 'Иван П.', amount: 15, time: '5 мин назад' },
  { id: 2, type: 'registration', user: 'Anna K.', time: '12 мин назад' },
  { id: 3, type: 'payment', user: 'Сергей М.', amount: 30, time: '25 мин назад' },
  { id: 4, type: 'subscription_expired', user: 'Maria L.', time: '1 час назад' },
  { id: 5, type: 'registration', user: 'Alex B.', time: '2 часа назад' },
]

export default function Dashboard() {
  const [stats, setStats] = useState(mockStats)
  const [chartData, setChartData] = useState(mockChartData)
  const [recentEvents, setRecentEvents] = useState(mockRecentEvents)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      // Uncomment when API is ready
      // const [statsRes, chartRes, eventsRes] = await Promise.all([
      //   dashboardAPI.getStats(),
      //   dashboardAPI.getChartData(30),
      //   dashboardAPI.getRecentEvents(10)
      // ])
      // setStats(statsRes.data)
      // setChartData(chartRes.data)
      // setRecentEvents(eventsRes.data)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
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

  return (
    <div className="space-y-6">
      {/* Page title */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400">Обзор статистики бота</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Всего пользователей"
          value={stats.totalUsers.toLocaleString()}
          change={stats.usersChange}
          changeType="increase"
          icon={Users}
          color="blue"
        />
        <StatsCard
          title="Активных подписок"
          value={stats.activeSubscriptions.toLocaleString()}
          change={stats.subscriptionsChange}
          changeType="increase"
          icon={CreditCard}
          color="green"
        />
        <StatsCard
          title="Доход сегодня"
          value={`$${stats.todayRevenue.toFixed(2)}`}
          change={stats.todayChange}
          changeType="increase"
          icon={DollarSign}
          color="yellow"
        />
        <StatsCard
          title="Доход за месяц"
          value={`$${stats.monthRevenue.toFixed(2)}`}
          change={stats.monthChange}
          changeType="increase"
          icon={TrendingUp}
          color="primary"
        />
      </div>

      {/* Charts */}
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

      {/* Recent events */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Последние события
        </h3>
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
      </div>
    </div>
  )
}
