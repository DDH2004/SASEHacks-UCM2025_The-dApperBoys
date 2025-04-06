import json
import os
import hashlib

DB = "wallets_db.json"

def load_db():
    if os.path.exists(DB):
        with open(DB, "r") as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB, "w") as f:
        json.dump(db, f, indent=4)

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def add_wallet(pubkey: str, wallet_file: str, password: str):
    db = load_db()
    db[pubkey] = {
        "wallet_file": wallet_file,
        "password_hash": hash_password(password)
    }
    save_db(db)

def wallet_exists(pubkey: str) -> bool:
    return pubkey in load_db()

def get_wallet_info(pubkey: str):
    return load_db().get(pubkey)

def verify_password(pubkey: str, password: str) -> bool:
    info = get_wallet_info(pubkey)
    if not info:
        return False
    return hash_password(password) == info["password_hash"]
