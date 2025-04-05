import { 
  Connection, 
  PublicKey, 
  Transaction,
  SystemProgram,
  LAMPORTS_PER_SOL
} from '@solana/web3.js';

// Solana network configuration
const SOLANA_NETWORK = import.meta.env.VITE_SOLANA_NETWORK || 'devnet';
const PROGRAM_ID = new PublicKey(import.meta.env.VITE_PROGRAM_ID);

// Network endpoints
const ENDPOINTS = {
  'mainnet-beta': 'https://api.mainnet-beta.solana.com',
  'devnet': 'https://api.devnet.solana.com',
  'testnet': 'https://api.testnet.solana.com',
};

// Initialize Solana connection
export const connection = new Connection(ENDPOINTS[SOLANA_NETWORK], 'confirmed');

/**
 * Submit an environmental action proof to the Solana blockchain
 * @param wallet Connected wallet instance
 * @param proofData Proof data to be submitted
 * @returns Transaction signature
 */
export async function submitProof(wallet: any, proofData: any) {
  try {
    if (!wallet.publicKey) throw new Error('Wallet not connected');

    // Create instruction data
    const data = Buffer.from(JSON.stringify(proofData));
    
    // Create transaction
    const transaction = new Transaction().add(
      SystemProgram.transfer({
        fromPubkey: wallet.publicKey,
        toPubkey: PROGRAM_ID,
        lamports: LAMPORTS_PER_SOL * 0.001 // Small fee for proof submission
      })
    );

    // Sign and send transaction
    const signature = await wallet.sendTransaction(transaction, connection);
    await connection.confirmTransaction(signature);

    return signature;
  } catch (error) {
    console.error('Error submitting proof:', error);
    throw error;
  }
}

/**
 * Get account balance
 * @param publicKey Wallet public key
 * @returns Balance in SOL
 */
export async function getBalance(publicKey: PublicKey): Promise<number> {
  const balance = await connection.getBalance(publicKey);
  return balance / LAMPORTS_PER_SOL;
}

/**
 * Request airdrop (only works on devnet/testnet)
 * @param publicKey Wallet public key
 * @returns Transaction signature
 */
export async function requestAirdrop(publicKey: PublicKey): Promise<string> {
  if (SOLANA_NETWORK === 'mainnet-beta') {
    throw new Error('Airdrop not available on mainnet');
  }
  const signature = await connection.requestAirdrop(
    publicKey,
    LAMPORTS_PER_SOL
  );
  await connection.confirmTransaction(signature);
  return signature;
}