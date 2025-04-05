import React, { useEffect, useState } from 'react';
import { connection, submitProof } from './lib/solana';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [wallet, setWallet] = useState<any>(null);

  useEffect(() => {
    // Auto-connect if wallet already connected
    if ('solana' in window) {
      const provider = (window as any).solana;
      if (provider.isPhantom) {
        provider.connect({ onlyIfTrusted: true }).then(({ publicKey }: any) => {
          setWallet(publicKey.toString());
          setIsConnected(true);
        });
      }
    }
  }, []);


  const connectWallet = async () => {
    if ('solana' in window) {
      const provider = (window as any).solana;
      if (provider.isPhantom) {
        try {
          const res = await provider.connect();
          setWallet(res.publicKey.toString());
          setIsConnected(true);
        } catch (err) {
          console.error('Wallet connection failed:', err);
        }
      } else {
        alert('Please install Phantom Wallet');
      }
    }
  };

  // Login Screen
  if (!isConnected) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-green-50">
        <div className="bg-white p-8 rounded-xl shadow-md text-center">
          <h1 className="text-2xl font-bold mb-4">Welcome to GreenProof</h1>
          <p className="text-gray-600 mb-6">Connect your wallet to get started</p>
          <button
            className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
            onClick={connectWallet}
          >
            Connect Wallet
          </button>
        </div>
      </div>
    );
  }

  // 👇Shown only if connected
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="ml-2 text-xl font-bold text-gray-900">GreenProof</span>
            </div>
            <div className="flex items-center">
              <span className="text-gray-700 mr-4">Wallet: {wallet.slice(0, 6)}...{wallet.slice(-4)}</span>
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
