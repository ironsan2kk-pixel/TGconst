import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components';

// Pages
import Dashboard from './pages/Dashboard';
import Channels from './pages/Channels';
import Tariffs from './pages/Tariffs';
import Users from './pages/Users';
import Subscriptions from './pages/Subscriptions';
import Payments from './pages/Payments';
import Promocodes from './pages/Promocodes';
import Broadcasts from './pages/Broadcasts';
import MenuBuilder from './pages/MenuBuilder';
import FAQ from './pages/FAQ';
import Settings from './pages/Settings';
import Backups from './pages/Backups';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/channels" element={<Channels />} />
        <Route path="/tariffs" element={<Tariffs />} />
        <Route path="/users" element={<Users />} />
        <Route path="/subscriptions" element={<Subscriptions />} />
        <Route path="/payments" element={<Payments />} />
        <Route path="/promocodes" element={<Promocodes />} />
        <Route path="/broadcasts" element={<Broadcasts />} />
        <Route path="/menu-builder" element={<MenuBuilder />} />
        <Route path="/faq" element={<FAQ />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/backups" element={<Backups />} />
        
        {/* Redirect unknown routes to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
