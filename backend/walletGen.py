import json
import secrets
from solders.keypair import Keypair

def generate_random_password(length: int = 16) -> str:
    return secrets.token_urlsafe(length)

def generate_wallet():
    """
    Generate a new Solana Keypair, save its secret key to disk,
    and return (Keypair, password, wallet_filename).
    """
    wallet = Keypair()
    password = generate_random_password()
    wallet_filename = f"wallet_{wallet.pubkey()}.json"
    with open(wallet_filename, "w") as f:
        json.dump(list(wallet.to_bytes()), f)
    return wallet, password, wallet_filename
