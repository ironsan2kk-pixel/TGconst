import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import BotList from './pages/Bots/BotList'
import BotCreate from './pages/Bots/BotCreate'
import BotEdit from './pages/Bots/BotEdit'
import ChannelList from './pages/Channels/ChannelList'
import ChannelCreate from './pages/Channels/ChannelCreate'
import ChannelEdit from './pages/Channels/ChannelEdit'
import TariffList from './pages/Tariffs/TariffList'
import TariffCreate from './pages/Tariffs/TariffCreate'
import TariffEdit from './pages/Tariffs/TariffEdit'
import PromocodeList from './pages/Promocodes/PromocodeList'
import PromocodeCreate from './pages/Promocodes/PromocodeCreate'
import PromocodeEdit from './pages/Promocodes/PromocodeEdit'
import BroadcastList from './pages/Broadcasts/BroadcastList'
import BroadcastCreate from './pages/Broadcasts/BroadcastCreate'
import BroadcastView from './pages/Broadcasts/BroadcastView'

function PrivateRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route path="/" element={
        <PrivateRoute>
          <Layout />
        </PrivateRoute>
      }>
        <Route index element={<Dashboard />} />
        
        {/* Боты */}
        <Route path="bots" element={<BotList />} />
        <Route path="bots/create" element={<BotCreate />} />
        <Route path="bots/:uuid/edit" element={<BotEdit />} />
        
        {/* Каналы */}
        <Route path="bots/:uuid/channels" element={<ChannelList />} />
        <Route path="bots/:uuid/channels/create" element={<ChannelCreate />} />
        <Route path="bots/:uuid/channels/:id/edit" element={<ChannelEdit />} />
        
        {/* Тарифы */}
        <Route path="bots/:uuid/channels/:channelId/tariffs" element={<TariffList />} />
        <Route path="bots/:uuid/channels/:channelId/tariffs/create" element={<TariffCreate />} />
        <Route path="bots/:uuid/tariffs/:id/edit" element={<TariffEdit />} />
        
        {/* Промокоды */}
        <Route path="bots/:uuid/promocodes" element={<PromocodeList />} />
        <Route path="bots/:uuid/promocodes/create" element={<PromocodeCreate />} />
        <Route path="bots/:uuid/promocodes/:id/edit" element={<PromocodeEdit />} />
        
        {/* Рассылки */}
        <Route path="bots/:uuid/broadcasts" element={<BroadcastList />} />
        <Route path="bots/:uuid/broadcasts/create" element={<BroadcastCreate />} />
        <Route path="bots/:uuid/broadcasts/:id" element={<BroadcastView />} />
      </Route>
      
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App
