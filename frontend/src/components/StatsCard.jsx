import { TrendingUp, TrendingDown } from 'lucide-react'

export default function StatsCard({ title, value, change, changeType = 'neutral', icon: Icon, color = 'primary' }) {
  const colorClasses = {
    primary: 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400',
    green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
    yellow: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
    red: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
    blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
  }

  return (
    <div className="card p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
          
          {change !== undefined && (
            <div className="flex items-center mt-2">
              {changeType === 'increase' && (
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              )}
              {changeType === 'decrease' && (
                <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
              )}
              <span className={`text-sm font-medium ${
                changeType === 'increase' ? 'text-green-500' :
                changeType === 'decrease' ? 'text-red-500' :
                'text-gray-500'
              }`}>
                {change}
              </span>
            </div>
          )}
        </div>
        
        {Icon && (
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
    </div>
  )
}
