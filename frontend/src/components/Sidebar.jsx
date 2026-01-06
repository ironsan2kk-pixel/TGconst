import { Link, useLocation, useParams } from 'react-router-dom'
import { Home, Bot, Settings, ChevronLeft, Hash, Tag, Percent, Send } from 'lucide-react'

export default function Sidebar() {
  const location = useLocation()
  const { uuid } = useParams()

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/')

  const mainNav = [
    { name: 'Дашборд', href: '/', icon: Home },
    { name: 'Боты', href: '/bots', icon: Bot },
  ]

  const botNav = uuid ? [
    { name: 'Назад к ботам', href: '/bots', icon: ChevronLeft },
    { name: 'Настройки', href: `/bots/${uuid}/edit`, icon: Settings },
    { name: 'Каналы', href: `/bots/${uuid}/channels`, icon: Hash },
    { name: 'Промокоды', href: `/bots/${uuid}/promocodes`, icon: Percent },
    { name: 'Рассылки', href: `/bots/${uuid}/broadcasts`, icon: Send },
  ] : []

  const navigation = uuid ? botNav : mainNav

  return (
    <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
      <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
        <div className="flex items-center h-16 px-4 border-b border-gray-200">
          <Bot className="w-8 h-8 text-primary-600" />
          <span className="ml-2 text-lg font-bold text-gray-900">Bot Constructor</span>
        </div>
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            const active = item.href === '/' 
              ? location.pathname === '/'
              : isActive(item.href)
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center px-3 py-2 text-sm font-medium rounded-lg
                  transition-colors duration-200
                  ${active
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                <Icon className={`w-5 h-5 mr-3 ${active ? 'text-primary-600' : 'text-gray-400'}`} />
                {item.name}
              </Link>
            )
          })}
        </nav>
      </div>
    </div>
  )
}
