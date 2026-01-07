import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Tv, 
  Package, 
  Users, 
  CreditCard, 
  Ticket,
  Gift,
  Megaphone,
  Menu as MenuIcon,
  HelpCircle,
  Settings,
  Database,
  X
} from 'lucide-react'

const menuItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/channels', icon: Tv, label: 'Каналы' },
  { path: '/tariffs', icon: Package, label: 'Тарифы' },
  { path: '/users', icon: Users, label: 'Пользователи' },
  { path: '/subscriptions', icon: CreditCard, label: 'Подписки' },
  { path: '/payments', icon: Ticket, label: 'Платежи' },
  { path: '/promocodes', icon: Gift, label: 'Промокоды' },
  { path: '/broadcasts', icon: Megaphone, label: 'Рассылки' },
  { path: '/menu-builder', icon: MenuIcon, label: 'Конструктор меню' },
  { path: '/faq', icon: HelpCircle, label: 'FAQ' },
  { path: '/settings', icon: Settings, label: 'Настройки' },
  { path: '/backups', icon: Database, label: 'Бэкапы' },
]

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Backdrop for mobile */}
      {open && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 
        bg-white dark:bg-gray-800 
        border-r border-gray-200 dark:border-gray-700
        transform transition-transform duration-300 ease-in-out
        ${open ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Tv className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg text-gray-900 dark:text-white">
              TG Admin
            </span>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1 overflow-y-auto h-[calc(100%-4rem)]">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `
                flex items-center gap-3 px-3 py-2.5 rounded-lg
                transition-colors duration-200
                ${isActive 
                  ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 font-medium' 
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                }
              `}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  )
}
