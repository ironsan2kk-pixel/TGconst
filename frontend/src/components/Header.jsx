import { Menu, Bell } from 'lucide-react'
import ThemeToggle from './ThemeToggle'

export default function Header({ onMenuClick }) {
  return (
    <header className="sticky top-0 z-30 h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between h-full px-4">
        {/* Left side */}
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
          
          <h1 className="text-lg font-semibold text-gray-800 dark:text-gray-200 hidden sm:block">
            Telegram Channel Bot
          </h1>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          
          {/* Theme toggle */}
          <ThemeToggle />
          
          {/* Avatar */}
          <div className="w-8 h-8 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-primary-600 dark:text-primary-400">A</span>
          </div>
        </div>
      </div>
    </header>
  )
}
