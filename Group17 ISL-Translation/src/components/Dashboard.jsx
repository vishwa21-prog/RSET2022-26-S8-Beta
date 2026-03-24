import CameraFeed from './CameraFeed';
import AvatarView from './AvatarView';
import TranslationOutput from './TranslationOutput';

export default function Dashboard({ mode }) {
  // A sleek layout that adapts instantly depending on the mode.
  if (mode === 'sign-to-text') {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '24px', flex: 1 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-card" style={{ flex: 1, padding: '24px', position: 'relative', overflow: 'hidden' }}>
            <h2 style={{ fontSize: '1.2rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: 'var(--accent-primary)' }}>live</span>
              Analysis Feed
            </h2>
            <CameraFeed />
          </div>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-card" style={{ flex: 1, padding: '24px', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ fontSize: '1.2rem', marginBottom: '16px' }}>Translation Engine</h2>
            <TranslationOutput type="interpreter" />
          </div>
          <div className="glass-card" style={{ height: '200px', padding: '24px' }}>
            <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>AI Confidence</h3>
            {/* Mocked confidence metrics for visual flair */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                <span>Hand Tracking</span>
                <span style={{ color: 'var(--success)' }}>98%</span>
              </div>
              <div style={{ width: '100%', height: '6px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '3px' }}>
                <div style={{ width: '98%', height: '100%', backgroundColor: 'var(--success)', borderRadius: '3px' }}></div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginTop: '8px' }}>
                <span>Gloss Prediction</span>
                <span style={{ color: 'var(--accent-primary)' }}>92%</span>
              </div>
              <div style={{ width: '100%', height: '6px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '3px' }}>
                <div style={{ width: '92%', height: '100%', backgroundColor: 'var(--accent-primary)', borderRadius: '3px' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'text-to-sign') {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '24px', flex: 1 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-card" style={{ flex: 1, padding: '24px', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ fontSize: '1.2rem', marginBottom: '16px' }}>Text Input</h2>
            <TranslationOutput type="generator" />
          </div>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-card" style={{ flex: 1, padding: '24px', position: 'relative' }}>
            <h2 style={{ fontSize: '1.2rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: 'var(--accent-secondary)' }}>3d</span>
              Avatar Translator
            </h2>
            <AvatarView />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <h2 style={{ color: 'var(--text-tertiary)' }}>Select a mode from the sidebar</h2>
    </div>
  );
}
