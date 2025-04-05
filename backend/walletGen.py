#!/usr/bin/env python3
"""
This script generates a new wallet for a user and assigns them a random password.
It saves the wallet's secret key to a JSON file (named using the wallet's public key)
and prints the public key and the generated password.

Note:
  • In production, you should store passwords securely (e.g. hashed) and keep the secret
    keys safe.
  • This is a simplified example for a hackathon.
"""

import json
import secrets
from solders.keypair import Keypair

def generate_random_password(length: int = 16) -> str:
    # Generates a secure random password using URL-safe characters.
    return secrets.token_urlsafe(length)

def generate_wallet() -> Keypair:
    # Generate a new wallet keypair.
    return Keypair()

def save_wallet_to_file(wallet: Keypair, filepath: str) -> None:
    # Convert the wallet's secret key (bytes) to a list of integers and save it as JSON.
    secret_key = list(wallet.to_bytes())
    with open(filepath, "w") as f:
        json.dump(secret_key, f)
    print(f"Wallet saved to {filepath}")

def main():
    # Generate a new wallet for the user.
    wallet = generate_wallet()
    # Generate a random password for the user.
    password = generate_random_password(16)
    # Create a filename based on the wallet's public key.
    wallet_filename = f"wallet_{wallet.pubkey()}.json"
    # Save the wallet's secret key to the file.
    save_wallet_to_file(wallet, wallet_filename)
    
    # Print out the details for the user.
    print("\nNew wallet generated!")
    print("Public Key:", wallet.pubkey())
    print("Wallet file:", wallet_filename)
    print("Assigned Password:", password)

if __name__ == "__main__":
    main()
