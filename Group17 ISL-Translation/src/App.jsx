import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Login from './components/Login';

function App() {
  const [activeMode, setActiveMode] = useState('sign-to-text'); // 'sign-to-text' or 'text-to-sign'
  const [user, setUser] = useState(null); // Auth State

  if (!user) {
    return (
      <AnimatePresence mode="wait">
        <motion.div
           key="login"
           initial={{ opacity: 0 }}
           animate={{ opacity: 1 }}
           exit={{ opacity: 0 }}
           transition={{ duration: 0.5 }}
           style={{ display: 'flex', width: '100%', minHeight: '100vh' }}
        >
          <Login onLogin={(userData) => setUser(userData)} />
        </motion.div>
      </AnimatePresence>
    );
  }

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <div className="app-container">
      {/* Background blurred blobs for the premium feel */}
      <div className="blob blob-1"></div>
      <div className="blob blob-2"></div>
      
      <Sidebar activeMode={activeMode} setActiveMode={setActiveMode} onLogout={handleLogout} />
      
      <main className="main-content">
        <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <motion.h1 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="title-gradient"
              style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}
            >
              SignSync Studio
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}
            >
              Welcome back, {user.username || 'User'}! Ready to translate?
            </motion.p>
          </div>
          
          <div className="glass-panel text-gradient-primary" style={{ padding: '8px 16px', borderRadius: 'var(--radius-full)', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div className="status-dot"></div>
            System Online
          </div>
        </header>

        <AnimatePresence mode="wait">
          <motion.div
            key={activeMode}
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.3 }}
            style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
          >
            <Dashboard mode={activeMode} />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
