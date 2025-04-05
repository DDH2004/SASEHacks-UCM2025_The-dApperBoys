import React, { useEffect, useState } from 'react';

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

      // Optional: sign a message here for verification
      // const message = `Sign in at ${new Date().toISOString()}`;
      // const signed = await provider.signMessage(new TextEncoder().encode(message), 'utf8');

      setWallet(walletAddress);
      setIsConnected(true);
    } catch (err) {
      console.error('Wallet connection failed:', err);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-950 to-black">
      <div className="bg-zinc-900 p-8 rounded-xl shadow-lg text-center">
        <h1 className="text-2xl font-bold mb-4 text-white">Welcome to dApp</h1>
        <p className="text-gray-300 mb-6">Connect your wallet to get started</p>
  
        {hasWallet ? (
          <button
            onClick={connectWallet}
            className="bg-green-500 text-white px-6 py-2 rounded-md hover:bg-green-600 transition-colors"
          >
            Sign in with Phantom Wallet
          </button>
        ) : (
          <p className="text-red-400 font-medium">
            Phantom Wallet not detected. Please install it.
          </p>
        )}
      </div>
    </div>
  );
  
};
export default Login;
