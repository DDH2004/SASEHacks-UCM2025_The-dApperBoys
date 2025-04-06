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
    <div className="min-h-screen bg-gradient-to-br from-purple-950 to-black text-white">
      {/* Navbar */}
      <nav className="bg-zinc-900 shadow-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <h1 className="text-2xl font-bold tracking-tight">🌿 GreenProof</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-300">
              Wallet: {wallet.slice(0, 6)}...{wallet.slice(-4)}
            </span>
            <button
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition"
              onClick={onDisconnect}
            >
              Disconnect
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8">
        {/* Scanner Section */}
        <section className="bg-zinc-800 rounded-xl p-6 shadow-lg">
          <h2 className="text-xl font-semibold mb-4 text-white">📷 Scan a Product Barcode</h2>
          <BarcodeScanner onScan={(barcode) => setScannedCode(barcode)} />
        </section>

        {/* Product Info Section */}
        {scannedCode && (
          <section className="bg-zinc-800 rounded-xl p-6 shadow-lg border border-zinc-700">
            <h2 className="text-xl font-semibold mb-4 text-white">ℹ️ About This Product</h2>
            <AboutProduct barcode={scannedCode} />
          </section>
        )}
      </main>
    </div>
  );
};

export default Dashboard;