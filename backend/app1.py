#!/usr/bin/env python3
"""
app.py

1) Sign Up:
   - Generate a new wallet and random password.
   - Save wallet_file and password hash into wallets_db.json via wallet_manager.add_wallet().

2) Sign In:
   - Prompt for public key and password.
   - Retrieve the stored wallet info via wallet_manager.get_wallet_info().
   - If authentication is successful, display the wallet info and mint a token.
"""

import json
import getpass
import secrets
from walletGen import generate_wallet
from wallet_manager import add_wallet, wallet_exists, get_wallet_info, verify_password
from solana.rpc.api import Client
from solders.keypair import Keypair
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey

# Configuration constants
MINT_AUTHORITY_FILE = "/Users/lalkattil/my-solana-wallet.json"  # Your mint authority keypair file
MINT_ADDRESS = "CzMUHT5wpcF331PyEvquERyrMeEnTXLQxQyKirPvnNo2"     # Your token mint address
LOCAL_RPC = "http://127.0.0.1:8899"

def generate_random_password(length: int = 16) -> str:
    return secrets.token_urlsafe(length)

def load_keypair_from_file(filepath: str) -> Keypair:
    with open(filepath, "r") as f:
        secret = json.load(f)
    return Keypair.from_bytes(bytes(secret))

def mint_token_to_wallet(pubkey_str: str) -> str:
    """
    Mint 1 token to the given wallet (identified by its public key string) and return the transaction signature.
    """
    # Retrieve wallet info from DB
    info = get_wallet_info(pubkey_str)
    wallet_file = info["wallet_file"]

    # Load the user's keypair from their wallet file
    user_kp = load_keypair_from_file(wallet_file)

    # Load the mint authority keypair (used for minting tokens)
    mint_authority = load_keypair_from_file(MINT_AUTHORITY_FILE)

    # Connect to the local validator
    client = Client(LOCAL_RPC)

    # Initialize the Token client for the given mint.
    token = Token(
        conn=client,
        pubkey=Pubkey.from_string(MINT_ADDRESS),
        program_id=TOKEN_PROGRAM_ID,
        payer=mint_authority,
    )

    # Get or create the associated token account for the user.
    ata = token.create_account(Pubkey.from_string(pubkey_str))

    # Mint 1 token to the user's token account.
    resp = token.mint_to(
        dest=ata,
        mint_authority=mint_authority,
        amount=1,
        opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed"),
    )
    return str(resp.value)

def main():
    print("=== User Sign Up ===")
    # Generate a new wallet using walletGen.py's generate_wallet()
    wallet = generate_wallet()
    password = generate_random_password()
    wallet_file = f"wallet_{wallet.pubkey()}.json"

    print("New wallet generated!")
    print("Public Key:", wallet.pubkey())
    print("Wallet file:", wallet_file)
    print("Assigned Password:", password)

    # Save the wallet's secret key to a file
    with open(wallet_file, "w") as f:
        json.dump(list(wallet.to_bytes()), f)

    # Save the wallet info in the database using wallet_manager.add_wallet()
    add_wallet(str(wallet.pubkey()), wallet_file, password)

    print("\n=== User Sign In ===")
    input_pubkey = input("Enter your wallet public key: ").strip()
    input_password = getpass.getpass("Enter your password: ").strip()

    if not wallet_exists(input_pubkey):
        print("Wallet not found.")
        return
    if not verify_password(input_pubkey, input_password):
        print("Incorrect password.")
        return

    print("Sign in successful!")

    # Retrieve and print the wallet info from the database.
    info = get_wallet_info(input_pubkey)
    print("Wallet info from DB:", info)

    print("Minting token...")
    tx_sig = mint_token_to_wallet(input_pubkey)
    print("Mint tx signature:", tx_sig)

if __name__ == "__main__":
    main()
