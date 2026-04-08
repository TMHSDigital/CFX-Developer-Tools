import { useEffect, useState } from 'react';
import { useNuiEvent, closeNui, fetchNui } from './nui-bridge';

export default function App() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const removeOpen = useNuiEvent('open', () => setVisible(true));
    const removeClose = useNuiEvent('close', () => setVisible(false));

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setVisible(false);
        closeNui();
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      removeOpen();
      removeClose();
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  if (!visible) return null;

  return (
    <div style={styles.overlay}>
      <div style={styles.container}>
        <header style={styles.header}>
          <h2>My Resource</h2>
          <button onClick={() => { setVisible(false); closeNui(); }} style={styles.closeBtn}>
            X
          </button>
        </header>
        <main style={styles.main}>
          <p>Your UI content goes here.</p>
          <button
            style={styles.actionBtn}
            onClick={async () => {
              const result = await fetchNui('getData');
              console.log('Got data:', result);
            }}
          >
            Fetch Data
          </button>
        </main>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: 'fixed',
    inset: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'rgba(0, 0, 0, 0.5)',
  },
  container: {
    width: 480,
    maxHeight: '80vh',
    background: '#1a1a2e',
    borderRadius: 12,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 20px',
    borderBottom: '1px solid rgba(255,255,255,0.1)',
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    color: '#aaa',
    fontSize: 18,
    cursor: 'pointer',
  },
  main: {
    padding: 20,
    overflowY: 'auto' as const,
    flex: 1,
  },
  actionBtn: {
    marginTop: 16,
    padding: '10px 20px',
    background: '#e94560',
    color: '#fff',
    border: 'none',
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: 14,
  },
};
