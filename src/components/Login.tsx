import React, { useEffect, useState } from 'react';
import WebGLBackground from './WebGLBackground';

interface LoginProps {
  setIsConnected: (value: boolean) => void;
  setWallet: (wallet: string | null) => void;
}

const Login: React.FC<LoginProps> = ({ setIsConnected, setWallet }) => {
  const [hasWallet, setHasWallet] = useState(false);

  useEffect(() => {
    if ('solana' in window) {
      const provider = (window as any).solana;
      if (provider?.isPhantom) {
        setHasWallet(true);
      }
    }
  }, []);

  const connectWallet = async () => {
    const provider = (window as any).solana;

    if (!provider?.isPhantom) {
      alert('Please install Phantom Wallet!');
      return;
    }

    try {
      const res = await provider.connect(); // ← this triggers the popup
      const walletAddress = res.publicKey.toString();

      setWallet(walletAddress);
      setIsConnected(true);
    } catch (err) {
      console.error('Wallet connection failed:', err);
    }
  };

  return (
    <>
      <WebGLBackground />
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-zinc-900/80 backdrop-blur-md p-8 rounded-xl shadow-lg text-center z-10">
          <h1 className="text-3xl font-bold mb-4 text-white">GreenRewards</h1>
          <p className="text-gray-300 mb-6">Connect your wallet to start earning rewards for recycling</p>
    
          {hasWallet ? (
            <button
              onClick={connectWallet}
              className="bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600 transition-colors"
            >
              Sign in with Phantom Wallet
            </button>
          ) : (
            <div className="text-red-400 font-medium">
              <p className="mb-3">Phantom Wallet not detected</p>
              <a 
                href="https://phantom.app/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition-colors"
              >
                Install Phantom Wallet
              </a>
            </div>
          )}
          
          <p className="mt-4 text-sm text-gray-400">
            Earning tokens for sustainable choices
          </p>
        </div>
      </div>
    </>
  );
};

export default Login;
