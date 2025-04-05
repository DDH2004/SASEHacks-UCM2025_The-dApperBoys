import React, { useEffect } from 'react';

interface LoginProps {
  setIsConnected: (value: boolean) => void;
  setWallet: (wallet: string | null) => void;
}

// Worry about later
const Login: React.FC<LoginProps> = ({ setIsConnected, setWallet }) => {
  useEffect(() => {
    if ('solana' in window) {
      const provider = (window as any).solana;
      if (provider?.isPhantom) {
        provider.connect({ onlyIfTrusted: true }).then(({ publicKey }: any) => {
          setWallet(publicKey.toString());
          setIsConnected(true);
        }).catch(() => {});
      }
    }
  }, [setIsConnected, setWallet]);


  // Phantom Wallet?
  const connectWallet = async () => {
    if ('solana' in window) {
      const provider = (window as any).solana;
      if (provider?.isPhantom) {
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
};

export default Login;
