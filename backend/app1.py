#!/usr/bin/env python3
"""
app.py

1) Sign Up:
   - Generate a new wallet and random password.
   - Save wallet_file + password_hash into wallets_db.json via wallet_manager.add_wallet()

2) Sign In:
   - Prompt for public key + password.
   - Lookup wallet_file & password_hash via wallet_manager.get_wallet_info().
   - If password matches, load the secret key from wallet_file and mint a token.
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

# Path to your mint authority's keypair file (the one that can mint)
MINT_AUTHORITY_FILE = "/Users/lalkattil/my-solana-wallet.json"
# The SPL token mint address you created earlier
MINT_ADDRESS = "CzMUHT5wpcF331PyEvquERyrMeEnTXLQxQyKirPvnNo2"
# Local validator RPC URL
LOCAL_RPC = "http://127.0.0.1:8899"

def generate_random_password(length: int = 16) -> str:
    return secrets.token_urlsafe(length)

def load_keypair_from_file(filepath: str) -> Keypair:
    with open(filepath, "r") as f:
        secret = json.load(f)
    return Keypair.from_bytes(bytes(secret))

def mint_token_to_wallet(pubkey_str: str) -> str:
    """
    Mint 1 token to the given wallet (identified by its public key string).
    """
    # 1) Read DB entry to get user's wallet file
    info = get_wallet_info(pubkey_str)
    wallet_file = info["wallet_file"]

    # 2) Load the user's secret key
    user_kp = load_keypair_from_file(wallet_file)

    # 3) Load mint authority keypair
    mint_authority = load_keypair_from_file(MINT_AUTHORITY_FILE)

    # 4) Connect to local validator
    client = Client(LOCAL_RPC)

    # 5) Initialize the Token client
    token = Token(
        conn=client,
        pubkey=Pubkey.from_string(MINT_ADDRESS),
        program_id=TOKEN_PROGRAM_ID,
        payer=mint_authority,
    )

    # 6) Get or create the user's associated token account
    ata = token.create_account(Pubkey.from_string(pubkey_str))

    # 7) Mint 1 token
    resp = token.mint_to(
        dest=ata,
        mint_authority=mint_authority,
        amount=1,
        opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed"),
    )
    return str(resp.value)

def main():
    print("=== User Sign Up ===")
    # Generate wallet + password
    wallet = generate_wallet()
    password = generate_random_password()
    wallet_file = f"wallet_{wallet.pubkey()}.json"

    print("Public Key:", wallet.pubkey())
    print("Wallet file:", wallet_file)
    print("Assigned Password:", password)

    # Persist secret key to file
    with open(wallet_file, "w") as f:
        json.dump(list(wallet.to_bytes()), f)

    # Store in DB
    add_wallet(str(wallet.pubkey()), wallet_file, password)

    print("\n=== User Sign In ===")
    pubkey = input("Enter public key: ").strip()
    pwd     = getpass.getpass("Enter password: ").strip()

    if not wallet_exists(pubkey):
        print("Wallet not found.")
        return
    if not verify_password(pubkey, pwd):
        print("Incorrect password.")
        return

    print("Sign in successful! Minting token...")
    tx_sig = mint_token_to_wallet(pubkey)
    print("Mint tx signature:", tx_sig)

if __name__ == "__main__":
    main()
