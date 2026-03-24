import { motion } from 'framer-motion';
import { Layers, Settings, MessageSquare, Hand, LogOut } from 'lucide-react';

export default function Sidebar({ activeMode, setActiveMode, onLogout }) {
  const menuItems = [
    { id: 'sign-to-text', icon: Hand, label: 'Sign &rarr; Text' },
    { id: 'text-to-sign', icon: MessageSquare, label: 'Text &rarr; Sign' },
    { id: 'history', icon: Layers, label: 'History' },
    { id: 'settings', icon: Settings, label: 'Settings' }
  ];

  return (
    <nav className="glass-panel" style={{ 
      width: '80px', 
      height: 'calc(100vh - 40px)', 
      margin: '20px 0 20px 20px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '30px 0',
      gap: '30px',
      position: 'relative'
    }}>
      <div 
        style={{
          width: '45px',
          height: '45px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 8px 32px var(--accent-glow)',
          marginBottom: '20px'
        }}
      >
        <span style={{ color: 'white', fontWeight: 'bold', fontSize: '1.2rem', fontFamily: 'Outfit' }}>S</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', width: '100%', alignItems: 'center', flex: 1 }}>
        {menuItems.map(item => {
          const isActive = item.id === activeMode;
          return (
            <motion.button
              key={item.id}
              onClick={() => setActiveMode(item.id)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              style={{
                background: isActive ? 'rgba(255,255,255,0.1)' : 'transparent',
                border: isActive ? '1px solid rgba(255,255,255,0.2)' : '1px solid transparent',
                width: '50px',
                height: '50px',
                borderRadius: '15px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)',
                transition: 'color 0.3s ease',
                position: 'relative'
              }}
              title={item.label}
            >
              <item.icon size={22} strokeWidth={activeMode === item.id ? 2.5 : 2} />
              
              {isActive && (
                <motion.div
                  layoutId="activeIndicator"
                  style={{
                    position: 'absolute',
                    left: '-16px',
                    width: '4px',
                    height: '24px',
                    background: 'var(--accent-primary)',
                    borderRadius: '0 4px 4px 0',
                    boxShadow: '0 0 10px var(--accent-glow)'
                  }}
                />
              )}
            </motion.button>
          );
        })}
      </div>

      {onLogout && (
          <div style={{ marginTop: 'auto' }}>
            <motion.button
                onClick={onLogout}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                style={{
                  background: 'transparent',
                  border: '1px solid transparent',
                  width: '50px',
                  height: '50px',
                  borderRadius: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  color: 'var(--error)',
                  transition: 'background 0.3s ease',
                  position: 'relative'
                }}
                title="Logout"
              >
                <LogOut size={22} strokeWidth={2} />
            </motion.button>
          </div>
      )}
    </nav>
  );
}
