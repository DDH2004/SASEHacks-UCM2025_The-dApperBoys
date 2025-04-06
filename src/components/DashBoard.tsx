import React, { useState, useEffect } from 'react';
import BarcodeScanner from './BarcodeScanner';
import AboutProduct from './AboutProduct';
import DynamicGraph from './DynamicGraph';
import PopUp from './PopUp';

interface DashboardProps {
  wallet: string;
  onDisconnect: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ wallet, onDisconnect }) => {
  const [scannedCode, setScannedCode] = useState<string | null>(null);
  const [points, setPoints] = useState<number | null>(null);
  const [tokens, setTokens] = useState<number | null>(null);
  const [isModalVisible, setModalVisible] = useState(false);

  // Fetch points for the wallet
  const fetchPoints = async () => {
    try {
      const response = await fetch(`http://localhost:8888/wallet/${wallet}`);
      const data = await response.json();

      if (response.ok) {
        const formData = new FormData();
        formData.append("barcode_id", scannedCode?.toString() || "0");
        formData.append("pubkey", wallet);

        const vResponse = await fetch(`http://localhost:8888/api/validate`, {
          method: "POST",
          body: formData,
        });
        const vData = await response.json();

        if (vResponse.ok){
          setPoints(vData.points_awarded || 0); // Set points from API response
          setTokens(data.reward_balance || 0);
          setModalVisible(true); // Show modal
        }
      } else {
        console.error('Error fetching wallet info:', data.error);
      }
    } catch (error) {
      console.error('Error fetching wallet info:', error);
    }
  };

  // Trigger point fetching when a barcode is scanned
  useEffect(() => {
    if (scannedCode) {
      fetchPoints();
    }
  }, [scannedCode]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-900 via-green-1000 to-gray-900 text-white font-sans">
      {/* Navbar */}
      <nav className="bg-black/30 backdrop-blur-md shadow-md sticky top-0 z-10 border-b border-green-900">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-3xl font-extrabold text-green-400 tracking-wider">🌱 GreenProof</h1>
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
            className="bg-zinc-900/70 border border-green-700 rounded-2xl p-6 shadow-lg hover:shadow-green-500/50 hover:border-green-400 transition-all duration-300"
          >
            <h2 className="text-xl font-semibold mb-4 text-green-400">📷 Scan a Product</h2>
            <BarcodeScanner
              onScan={(barcode) => setScannedCode(barcode)}
              walletId={wallet}
            />
          </div>

          {/* Product Info */}
          {scannedCode ? (
            <div
              className="bg-zinc-900/70 border border-green-600 rounded-2xl p-6 shadow-lg hover:shadow-green-400/40 hover:border-green-300 transition-all duration-300"
            >
              <h2 className="text-xl font-semibold mb-4 text-green-400">Product Info</h2>
              <AboutProduct barcode={scannedCode} />
            </div>
          ) : (
            <div className="flex items-center justify-center text-center text-zinc-500 italic border border-zinc-700 rounded-xl p-6">
              <p>Scan a barcode to view product details.</p>
            </div>
          )}

          <DynamicGraph />
        </div>

        {/* Modal Pop-Up */}
        <PopUp
          isVisible={isModalVisible}
          onClose={() => setModalVisible(false)}
          points={points}
          tokens={tokens}
        />
      </main>
    </div>
  );
};

export default Dashboard;