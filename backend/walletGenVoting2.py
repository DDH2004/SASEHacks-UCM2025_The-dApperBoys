import secrets
from solders.keypair import Keypair

def generate_random_password(length: int = 16) -> str:
    return secrets.token_urlsafe(length)

def generate_wallet():
    """
    Generate a new Solana keypair and a random password.
    Returns (pubkey_str, secret_key_list, password).
    """
    wallet = Keypair()
    password = generate_random_password()
    secret_key = list(wallet.to_bytes())
    pubkey_str = str(wallet.pubkey())
    return pubkey_str, secret_key, password
