import { motion } from 'framer-motion';

export default function AvatarView() {
  return (
    <div style={{ position: 'relative', width: '100%', height: 'calc(100% - 40px)', borderRadius: 'var(--radius-md)', overflow: 'hidden', background: 'radial-gradient(circle at center, #1e293b 0%, #0f172a 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      
      {/* Dynamic 3D Avatar Placeholder */}
      <motion.div
        animate={{ y: [0, -10, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        style={{ width: '200px', height: '300px', position: 'relative' }}
      >
        {/* We use a CSS-based generic avatar/robot placeholder for visual appeal */}
        <div style={{ position: 'absolute', top: '10%', left: '50%', transform: 'translateX(-50%)', width: '100px', height: '120px', background: 'var(--accent-primary)', borderRadius: '50px 50px 20px 20px', boxShadow: '0 0 30px var(--accent-glow)', opacity: 0.9 }}></div>
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translateX(-50%)', width: '140px', height: '150px', background: 'linear-gradient(180deg, var(--accent-secondary), rgba(0,0,0,0))', borderRadius: '40px 40px 0 0', opacity: 0.7 }}></div>
        
        {/* Glowing Data Streams behind Avatar */}
        <div style={{ position: 'absolute', inset: 0, opacity: 0.3, background: 'repeating-linear-gradient(0deg, transparent, transparent 10px, var(--accent-primary) 10px, var(--accent-primary) 11px)', zIndex: -1 }}></div>
      </motion.div>

      {/* Grid Floor */}
      <div style={{ position: 'absolute', bottom: '-50%', width: '200%', height: '100%', borderTop: '1px solid rgba(255,255,255,0.1)', background: 'linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)', backgroundSize: '40px 40px', transform: 'perspective(500px) rotateX(60deg)', transformOrigin: 'top', opacity: 0.5 }}></div>

      <div style={{ position: 'absolute', top: 20, left: 20, zIndex: 10 }}>
        <span style={{ background: 'var(--glass-bg)', padding: '6px 12px', borderRadius: '20px', fontSize: '0.8rem', border: '1px solid var(--glass-border)' }}>Engine: Unity WebGL</span>
      </div>

    </div>
  );
}
