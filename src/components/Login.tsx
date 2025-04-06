import React, { useEffect, useState } from 'react';
import WebGLBackground from './WebGLBackground';

interface LoginProps {
  setIsConnected: (value: boolean) => void;
  setWallet: (wallet: string | null) => void;
}

const Login: React.FC<LoginProps> = ({ setIsConnected, setWallet }) => {
  const [hasWallet, setHasWallet] = useState(false);
  const [pubkey, setPubkey] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

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
      const res = await provider.connect();
      const walletAddress = res.publicKey.toString();
      setWallet(walletAddress);
      setIsConnected(true);
    } catch (err) {
      console.error('Wallet connection failed:', err);
    }
  };

  const handleSignup = async () => {
    try {
      const res = await fetch('http://localhost:8888/signup', { method: 'POST' });
      const data = await res.json();
      setPubkey(data.pubkey);
      setPassword(data.password);
      setMessage('✅ Account created. Use these credentials to sign in.');
    } catch (err) {
      console.error(err);
      setMessage('❌ Failed to create account');
    }
  };

  const handleSignin = async () => {
    try {
      const res = await fetch('http://localhost:8888/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pubkey, password }),
      });

      const data = await res.json();
      if (!res.ok) {
        setMessage(`❌ ${data.error}`);
        return;
      }

      setWallet(pubkey);
      setIsConnected(true);
    } catch (err) {
      console.error(err);
      setMessage('❌ Sign in failed');
    }
  };

  return (
    <>
      <WebGLBackground />
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-zinc-900/80 backdrop-blur-md p-8 rounded-xl shadow-lg text-center z-10 w-full max-w-md space-y-4">
          <h1 className="text-3xl font-bold text-white">GreenRewards</h1>
          <p className="text-gray-300 mb-2">Earn tokens for sustainable actions</p>
          {/* Chang naem? */}

          {/* Phantom Wallet */}
          {hasWallet ? (
            <button
              onClick={connectWallet}
              className="w-full bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600 transition"
            >
              Sign in with Phantom Wallet
            </button>
          ) : (
            <div className="text-red-400 font-medium space-y-2">
              <p>Phantom Wallet not detected</p>
              <a
                href="https://phantom.app/"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition"
              >
                Install Phantom Wallet
              </a>
            </div>
          )}

          {/* Divider */}
          <div className="border-t border-zinc-700 my-4" />

          {/* Traditional login */}
          <input
            type="text"
            value={pubkey}
            onChange={(e) => setPubkey(e.target.value)}
            placeholder="Public Key"
            className="w-full px-4 py-2 rounded bg-zinc-800 border border-zinc-700 text-white placeholder-gray-400"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="w-full px-4 py-2 rounded bg-zinc-800 border border-zinc-700 text-white placeholder-gray-400"
          />

          <div className="flex flex-col space-y-3">
            <button
              onClick={handleSignup}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md transition"
            >
              🌱 Create Account
            </button>
            <button
              onClick={handleSignin}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-md transition"
            >
              🔐 Sign In Without Wallet
            </button>
          </div>

          {/* Feedback message */}
          {message && <p className="text-sm text-purple-300 mt-2">{message}</p>}
        </div>
      </div>
    </>
  );
};

export default Login;
