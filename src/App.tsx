import React, { useState } from 'react';
import Login from './components/Login';
import Dashboard from './components/DashBoard';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [wallet, setWallet] = useState<string | null>(null);

  if (!isConnected || !wallet) {
    return <Login setIsConnected={setIsConnected} setWallet={setWallet} />;
  }

  return (
    <Dashboard
      wallet={wallet}
      onDisconnect={() => {
        setWallet(null);
        setIsConnected(false);
      }}
    />
  );
}

export default App;
