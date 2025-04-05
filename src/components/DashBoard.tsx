import React from 'react';

interface DashboardProps {
  wallet: string;
  onDisconnect: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ wallet, onDisconnect }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-950 to-black text-white">
      <nav className="bg-zinc-900 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <span className="text-xl font-bold text-white">GreenProof</span>
            <div className="flex items-center">
              <span className="text-gray-300 mr-4">
                Wallet: {wallet.slice(0, 6)}...{wallet.slice(-4)}
              </span>
              <button
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
                onClick={onDisconnect}
              >
                Disconnect
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-zinc-800 rounded-lg shadow-xl p-6">
          <h2 className="text-2xl font-bold text-white mb-4">
            Submit Environmental Proof
          </h2>
          {/* Your form or content goes here */}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
