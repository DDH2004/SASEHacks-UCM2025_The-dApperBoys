from pymongo import MongoClient
import hashlib

client = MongoClient("mongodb://localhost:27017/")
db     = client["sasehacks"]
col    = db["wallets"]

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def add_wallet(pubkey: str, secret_key: list, password: str):
    col.insert_one({
        "_id": pubkey,
        "secret_key": secret_key,
        "password_hash": hash_password(password)
    })

def wallet_exists(pubkey: str) -> bool:
    return col.count_documents({"_id": pubkey}, limit=1) == 1

def get_wallet_info(pubkey: str):
    doc = col.find_one({"_id": pubkey}, {"secret_key":0, "password_hash":0})
    if doc:
        doc["pubkey"] = doc.pop("_id")
    return doc

def verify_password(pubkey: str, password: str) -> bool:
    doc = col.find_one({"_id": pubkey})
    if not doc:
        return False
    return hash_password(password) == doc["password_hash"]

def load_keypair_from_db(pubkey: str):
    from solders.keypair import Keypair
    doc = col.find_one({"_id": pubkey}, {"secret_key":1})
    if not doc:
        return None
    return Keypair.from_bytes(bytes(doc["secret_key"]))
