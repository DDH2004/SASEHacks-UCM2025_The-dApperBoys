import React, { useState } from 'react';
import BarcodeScanner from './BarcodeScanner';
import AboutProduct from './AboutProduct';

interface DashboardProps {
  wallet: string;
  onDisconnect: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ wallet, onDisconnect }) => {
  const [scannedCode, setScannedCode] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-black to-gray-900 text-white font-sans">
      {/* Navbar */}
      <nav className="bg-black/30 backdrop-blur-md shadow-md sticky top-0 z-10 border-b border-purple-900">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-3xl font-extrabold text-purple-400 tracking-wider">🌱 GreenProof</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-400 font-mono text-sm">
              {wallet.slice(0, 6)}...{wallet.slice(-4)}
            </span>
            <button
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md shadow transition-all"
              onClick={onDisconnect}
            >
              Disconnect
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 sm:px-10 py-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Scanner */}
          <div
            className="bg-zinc-900/70 border border-purple-700 rounded-2xl p-6 shadow-lg hover:shadow-purple-500/50 hover:border-purple-400 transition-all duration-300"
          >
            <h2 className="text-xl font-semibold mb-4 text-purple-300">📷 Scan a Product</h2>
            <BarcodeScanner
              onScan={(barcode) => setScannedCode(barcode)}
              walletId={wallet}
            />
          </div>

          {/* Product Info */}
          {scannedCode ? (
            <div
              className="bg-zinc-900/70 border border-teal-600 rounded-2xl p-6 shadow-lg hover:shadow-teal-400/40 hover:border-teal-300 transition-all duration-300"
            >
              <h2 className="text-xl font-semibold mb-4 text-teal-300">Product Info</h2>
              <AboutProduct barcode={scannedCode} />
            </div>
          ) : (
            <div className="flex items-center justify-center text-center text-zinc-500 italic border border-zinc-700 rounded-xl p-6">
              <p>Scan a barcode to view product details.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
