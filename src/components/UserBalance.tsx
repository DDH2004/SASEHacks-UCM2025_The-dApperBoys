import React, { useState, useEffect } from 'react';
import { FaCoins, FaMedal } from 'react-icons/fa';

interface UserBalanceProps {
  walletAddress: string;
}

interface BalanceData {
  points: number;
  tokens: number;
  rank?: number;
  nextReward?: number;
}

const UserBalance: React.FC<UserBalanceProps> = ({ walletAddress }) => {
  const [loading, setLoading] = useState(true);
  const [balanceData, setBalanceData] = useState<BalanceData>({
    points: 0,
    tokens: 0,
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBalances = async () => {
      try {
        setLoading(true);
        
        // Use full URL to backend server
        const response = await fetch(`http://localhost:8888/wallet/${walletAddress}`);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Error response:', errorText);
          throw new Error(`Failed to fetch balance data: ${response.status}`);
        }
        
        const data = await response.json();
        
        setBalanceData({
          points: data.points || 0,
          tokens: data.reward_balance || 0,
          nextReward: 100 - (data.points % 100)
        });
        
      } catch (err) {
        console.error('Error fetching balance data:', err);
        setError(`Failed to load your balance: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    if (walletAddress) {
      fetchBalances();
    }
  }, [walletAddress]);

  const calculatePointsProgress = () => {
    if (!balanceData.nextReward) return 0;
    return 100 - balanceData.nextReward;
  };

  if (error) {
    return (
      <div className="bg-zinc-900/70 border border-red-600 rounded-2xl p-6 shadow-lg">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900/70 border border-green-700 rounded-2xl p-6 shadow-lg hover:shadow-green-500/50 hover:border-green-400 transition-all duration-300">
      <h2 className="text-xl font-semibold mb-4 text-green-400">💰 Your Balance</h2>
      
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-green-500"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Points Section */}
          <div className="flex items-center justify-between">
            <div>
              <div className="text-zinc-400 text-sm">Recycling Points</div>
              <div className="text-2xl font-bold text-white flex items-center gap-2">
                <FaMedal className="text-yellow-500" /> 
                {balanceData.points}
              </div>
            </div>
            {balanceData.rank && (
              <div className="bg-green-900/50 px-3 py-1 rounded-full">
                <span className="text-sm text-green-300">
                  Rank #{balanceData.rank}
                </span>
              </div>
            )}
          </div>

          {/* Progress to next token reward */}
          <div>
            <div className="flex justify-between mb-2 text-sm">
              <span className="text-zinc-400">Progress to next token reward</span>
              <span className="text-green-400">{calculatePointsProgress()}%</span>
            </div>
            <div className="w-full bg-zinc-700 rounded-full h-2.5">
              <div 
                className="bg-gradient-to-r from-green-500 to-green-300 h-2.5 rounded-full"
                style={{ width: `${calculatePointsProgress()}%` }}
              ></div>
            </div>
            <div className="text-right text-xs mt-1 text-zinc-500">
              {balanceData.nextReward} more points needed
            </div>
          </div>

          {/* Tokens Section */}
          <div>
            <div className="text-zinc-400 text-sm">GreenTokens</div>
            <div className="text-2xl font-bold text-white flex items-center gap-2">
              <FaCoins className="text-green-500" />
              {balanceData.tokens}
            </div>
            <div className="text-xs text-zinc-500 mt-1">
              Current value: ~${(balanceData.tokens * 0.05).toFixed(2)} USD
            </div>
          </div>

          {/* Recent Activity (optional) */}
          <div className="border-t border-zinc-800 pt-4 mt-4">
            <h3 className="text-sm font-medium text-zinc-400 mb-2">Recent Activity</h3>
            <div className="text-sm text-zinc-500">
              <div className="flex justify-between py-1">
                <span>Recycled water bottle</span>
                <span className="text-green-400">+25 points</span>
              </div>
              <div className="flex justify-between py-1">
                <span>Weekly distribution</span>
                <span className="text-green-400">+100 tokens</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserBalance;