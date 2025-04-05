import React, { useState } from 'react';
import Login from './components/Login';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [wallet, setWallet] = useState<string | null>(null);

  if (!isConnected || !wallet) {
    return <Login setIsConnected={setIsConnected} setWallet={setWallet} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="ml-2 text-xl font-bold text-gray-900">GreenProof</span>
            </div>
            <div className="flex items-center">
              <span className="text-gray-700 mr-4">
                Wallet: {wallet.slice(0, 6)}...{wallet.slice(-4)}
              </span>
              <button
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
                onClick={() => {
                  setIsConnected(false);
                  setWallet(null);
                }}
              >
                Disconnect
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-xl p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Submit Environmental Proof
          </h2>
          {/* Add your form components here */}
        </div>
      </main>
    </div>
  );
}

export default App;
