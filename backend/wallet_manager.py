#!/usr/bin/env python3
"""
wallet_manager.py

This module implements basic wallet management functions:
  - add_wallet: Add a new wallet entry (public key, wallet file, password hash)
  - wallet_exists: Check if a wallet exists in the database.
  - get_wallet_info: Return stored information for a wallet.
  - verify_password: Validate a user-provided password against the stored hash.

Wallet data is stored in a JSON file ("wallets_db.json") in the same directory.
Note: For demonstration only. In production, use a secure password hashing algorithm.
"""

import json
import os
import hashlib

DB_FILENAME = "wallets_db.json"

def load_db():
    """Load the wallet database from the JSON file."""
    if os.path.exists(DB_FILENAME):
        with open(DB_FILENAME, "r") as f:
            return json.load(f)
    return {}

def save_db(db):
    """Save the wallet database to the JSON file."""
    with open(DB_FILENAME, "w") as f:
        json.dump(db, f, indent=4)

def hash_password(password: str) -> str:
    """
    Returns a SHA-256 hash of the provided password.
    (In production, use a more secure hashing mechanism such as bcrypt.)
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def add_wallet(public_key: str, wallet_file: str, password: str):
    """
    Adds a wallet entry to the database with the given public key, wallet file path,
    and password (stored as a hash).
    """
    db = load_db()
    if public_key in db:
        print(f"Wallet {public_key} already exists in the database.")
        return
    db[public_key] = {
        "wallet_file": wallet_file,
        "password_hash": hash_password(password)
    }
    save_db(db)
    print(f"Wallet {public_key} added successfully.")

def wallet_exists(public_key: str) -> bool:
    """Returns True if a wallet entry exists for the provided public key."""
    db = load_db()
    return public_key in db

def get_wallet_info(public_key: str):
    """
    Returns a dictionary with the wallet info (wallet_file and password_hash) 
    for the given public key, or None if it doesn't exist.
    """
    db = load_db()
    return db.get(public_key)

def verify_password(public_key: str, password: str) -> bool:
    """
    Checks if the provided password matches the stored hash for the wallet.
    Returns True if it matches; False otherwise.
    """
    info = get_wallet_info(public_key)
    if info is None:
        return False
    return hash_password(password) == info.get("password_hash")

if __name__ == "__main__":
    # Simple CLI demo to test the functions.
    print("Wallet Manager Demo")
    print("-------------------")
    print("Select an action:")
    print("1. Add new wallet")
    print("2. Check if wallet exists")
    print("3. Get wallet info")
    print("4. Verify wallet password")
    
    action = input("Enter action number (1-4): ").strip()
    
    if action == "1":
        pubkey = input("Enter wallet public key: ").strip()
        wallet_file = input("Enter wallet file path: ").strip()
        password = input("Enter wallet password: ").strip()
        add_wallet(pubkey, wallet_file, password)
    elif action == "2":
        pubkey = input("Enter wallet public key: ").strip()
        if wallet_exists(pubkey):
            print(f"Wallet {pubkey} exists in the database.")
        else:
            print(f"Wallet {pubkey} does not exist.")
    elif action == "3":
        pubkey = input("Enter wallet public key: ").strip()
        info = get_wallet_info(pubkey)
        if info:
            print("Wallet Info:")
            print(info)
        else:
            print("Wallet not found.")
    elif action == "4":
        pubkey = input("Enter wallet public key: ").strip()
        password = input("Enter wallet password: ").strip()
        if verify_password(pubkey, password):
            print("Password is correct.")
        else:
            print("Incorrect password or wallet not found.")
    else:
        print("Invalid action.")
