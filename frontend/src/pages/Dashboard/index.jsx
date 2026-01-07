import { useState, useEffect } from 'react'
import { Users, CreditCard, DollarSign, TrendingUp } from 'lucide-react'
import { StatsCard, Chart } from '../../components'
import api from '../../api/client'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalUsers: 0, activeSubscriptions: 0, todayRevenue: 0, monthRevenue: 0
  })
  const [revenueChart, setRevenueChart] = useState([])
  const [usersChart, setUsersChart] = useState([])
  const [recentUsers, setRecentUsers] = useState([])
  const [recentPayments, setRecentPayments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    try {
      setError(null)
      const [statsRes, revenueRes, usersRes, recentRes] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/dashboard/chart/revenue?days=30'),
        api.get('/dashboard/chart/users?days=30'),
        api.get('/dashboard/recent?limit=10')
      ])

      // Parse stats
      const s = statsRes.data
      setStats({
        totalUsers: s.users?.total || 0,
        activeSubscriptions: s.subscriptions?.active || 0,
        todayRevenue: s.revenue?.today || 0,
        monthRevenue: s.revenue?.month || 0,
        newUsersToday: s.users?.today || 0,
        pendingPayments: s.payments?.pending || 0
      })

      // Parse charts
      const revenueData = revenueRes.data.data || []
      setRevenueChart(revenueData.map(d => ({
        date: new Date(d.date).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' }),
        revenue: d.amount || 0
      })))

      const usersData = usersRes.data.data || []
      setUsersChart(usersData.map(d => ({
        date: new Date(d.date).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' }),
        users: d.count || 0
      })))

      // Parse recent activity
      const recent = recentRes.data
      setRecentUsers(recent.users || [])
      setRecentPayments(recent.payments || [])

    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      setError('Не удалось загрузить данные. Проверьте что backend запущен.')
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date
    const mins = Math.floor(diff / 60000)
    if (mins < 60) return `${mins} мин назад`
    const hours = Math.floor(mins / 60)
    if (hours < 24) return `${hours} ч назад`
    return date.toLocaleDateString('ru-RU')
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <p className="text-red-500 mb-4">{error}</p>
        <button onClick={loadData} className="btn-primary">Попробовать снова</button>
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
        <StatsCard title="Всего пользователей" value={stats.totalUsers.toLocaleString()} icon={Users} color="blue" />
        <StatsCard title="Активных подписок" value={stats.activeSubscriptions.toLocaleString()} icon={CreditCard} color="green" />
        <StatsCard title="Доход сегодня" value={`$${stats.todayRevenue.toFixed(2)}`} icon={DollarSign} color="yellow" />
        <StatsCard title="Доход за месяц" value={`$${stats.monthRevenue.toFixed(2)}`} icon={TrendingUp} color="primary" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Chart title="Доход по дням (USDT)" data={revenueChart} type="area" dataKey="revenue" xAxisKey="date" color="#3b82f6" height={280} />
        <Chart title="Новые пользователи" data={usersChart} type="bar" dataKey="users" xAxisKey="date" color="#10b981" height={280} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Новые пользователи</h3>
          {recentUsers.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-center py-4">Пока нет пользователей</p>
          ) : (
            <div className="space-y-3">
              {recentUsers.slice(0, 5).map(user => (
                <div key={user.id} className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                  <span className="text-xl">👤</span>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900 dark:text-white">{user.username ? `@${user.username}` : user.first_name || `ID: ${user.telegram_id}`}</p>
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{formatTime(user.created_at)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Последние платежи</h3>
          {recentPayments.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-center py-4">Пока нет платежей</p>
          ) : (
            <div className="space-y-3">
              {recentPayments.slice(0, 5).map(payment => (
                <div key={payment.id} className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                  <span className="text-xl">💰</span>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900 dark:text-white">Платёж ${payment.amount}</p>
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{formatTime(payment.paid_at)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
