#!/usr/bin/env python3
"""
This script demonstrates how to:
  1. Connect to a local Solana test validator.
  2. Load a wallet from a keypair JSON file (your new wallet).
  3. Create a new SPL token mint.
  4. Create an associated token account for a user.
  5. Mint tokens to that user’s account.

Before running:
  • Start your local validator with: solana-test-validator
  • Ensure your wallet’s secret key is saved in a JSON file (e.g., ~/.config/solana/my-solana-wallet.json)
"""

import json
import time
from solana.rpc.api import Client
from solders.keypair import Keypair
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.commitment import Confirmed
from solana.exceptions import SolanaRpcException

def load_keypair(filepath: str) -> Keypair:
    with open(filepath, "r") as f:
        secret = json.load(f)
    return Keypair.from_bytes(bytes(secret))

def main():
    try:
        # 1. Connect to the local validator.
        local_url = "http://127.0.0.1:8899"
        client = Client(local_url)
        print("Connected to local Solana test validator.")

        # 2. Load your wallet from the JSON file.
        wallet_path = "/Users/lalkattil/my-solana-wallet.json"
        wallet = load_keypair(wallet_path)
        print("Loaded wallet. Public key:", wallet.pubkey())
        # This should match: GeCGjHsrXeuGMpqCgbL5Mi3BxtNBeKxfaEAkTg29v3fA

        # Use this wallet as the mint authority and fee payer.
        mint_authority = wallet
        payer = wallet

        # 3. Request an airdrop for your wallet on the local node.
        print("Requesting airdrop for wallet...")
        airdrop_resp = client.request_airdrop(mint_authority.pubkey(), 10_000_000_000)  # 10 SOL in lamports
        if airdrop_resp.value is not None:
            time.sleep(5)  # Wait for confirmation (in production, poll for confirmation)
            balance_resp = client.get_balance(mint_authority.pubkey(), commitment=Confirmed)
            print("Airdrop complete. Balance:", balance_resp.value, "lamports")
        else:
            print("Airdrop failed. Response:", airdrop_resp)
            return

        # 4. Create a new token mint with 0 decimals (indivisible token).
        decimals = 0
        token = Token.create_mint(
            conn=client,
            payer=payer,
            mint_authority=mint_authority.pubkey(),
            decimals=decimals,
            program_id=TOKEN_PROGRAM_ID,
        )
        print("Created token mint:", token.pubkey)

        # 5. Create an associated token account for a user.
        # Replace this with the actual user's wallet public key in your application.
        user = Keypair()
        user_token_account = token.create_account(user.pubkey())
        print("Created token account for user:", user_token_account)

        # 6. Mint 1 token to the user's token account.
        amount_to_mint = 1
        tx_signature = token.mint_to(
            dest=user_token_account,
            mint_authority=mint_authority,
            amount=amount_to_mint,
            opts=Confirmed,
        )
        print(f"Minted {amount_to_mint} token(s) to user account {user_token_account}.")
        print("Transaction signature:", tx_signature)
    except SolanaRpcException as e:
        print("An RPC error occurred:", e)
        print("Error details:", e.args)
    except Exception as e:
        print("An unexpected error occurred:", e)

if __name__ == "__main__":
    main()
