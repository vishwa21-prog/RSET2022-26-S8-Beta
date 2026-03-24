import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, Clipboard, Send, Volume2 } from 'lucide-react';

export default function TranslationOutput({ type }) {
  const [text, setText] = useState('');
  const [copied, setCopied] = useState(false);
  const [simulating, setSimulating] = useState(false);

  // Mock interpretation for the 'interpreter' type
  useEffect(() => {
    if (type === 'interpreter') {
      const demoSentences = [
        "Waiting for sign...",
        "I",
        "I am",
        "I am using",
        "I am using SignSync",
        "I am using SignSync today."
      ];
      
      let index = 0;
      setSimulating(true);
      
      const interval = setInterval(() => {
        setText(demoSentences[index]);
        index++;
        if (index >= demoSentences.length) {
          clearInterval(interval);
          setSimulating(false);
        }
      }, 1500);
      
      return () => clearInterval(interval);
    }
  }, [type]);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (type === 'interpreter') {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
        <div style={{ flex: 1, position: 'relative', marginTop: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <AnimatePresence mode="wait">
            <motion.p
              key={text}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: -1, y: -10 }}
              style={{
                fontSize: text.length > 20 ? '1.8rem' : '2.5rem',
                fontFamily: 'Outfit',
                fontWeight: 600,
                color: simulating ? 'var(--text-secondary)' : 'white',
                lineHeight: 1.4
              }}
            >
              {text || "Awaiting input..."}
              {simulating && (
                <motion.span
                  animate={{ opacity: [0, 1, 0] }}
                  transition={{ duration: 1, repeat: Infinity }}
                  style={{ display: 'inline-block', ml: 2, color: 'var(--accent-primary)' }}
                >
                  |
                </motion.span>
              )}
            </motion.p>
          </AnimatePresence>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '24px', paddingTop: '16px', borderTop: '1px solid var(--glass-border)' }}>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="icon-btn" onClick={handleCopy} title="Copy to clipboard">
              {copied ? <Check size={18} color="var(--success)" /> : <Clipboard size={18} />}
            </button>
            <button className="icon-btn" title="Speak text aloud">
              <Volume2 size={18} />
            </button>
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>
            Gemini Language Model Active
          </div>
        </div>
      </div>
    );
  }

  // Generator mode (Text to Sign)
  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type a sentence to translate into sign language..."
        style={{
          flex: 1,
          background: 'rgba(0,0,0,0.2)',
          border: '1px solid var(--glass-border)',
          borderRadius: 'var(--radius-md)',
          padding: '20px',
          color: 'white',
          fontSize: '1.2rem',
          fontFamily: 'Inter',
          resize: 'none',
          outline: 'none',
          boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.5)',
          transition: 'all 0.3s ease'
        }}
        onFocus={(e) => e.target.style.borderColor = 'var(--accent-primary)'}
        onBlur={(e) => e.target.style.borderColor = 'var(--glass-border)'}
      />
      
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
        <button 
          className="btn btn-primary"
          style={{ padding: '14px 32px', fontSize: '1.1rem' }}
          onClick={() => {
            // Trigger 3D animation context logic
          }}
        >
          <Send size={20} /> Generate Sign Sequence
        </button>
      </div>
    </div>
  );
}
