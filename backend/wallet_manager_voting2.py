from pymongo import MongoClient
import hashlib
from solders.keypair import Keypair

client = MongoClient("mongodb://localhost:27017/")
db = client["sasehacks"]
col = db["wallets"]

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def add_wallet(pubkey: str, secret_key: list, password: str):
    col.insert_one({
        "_id": pubkey,
        "secret_key": secret_key,
        "password_hash": hash_password(password),
        "points": 0
    })

def wallet_exists(pubkey: str) -> bool:
    return col.count_documents({"_id": pubkey}, limit=1) == 1

def get_wallet_info(pubkey: str):
    doc = col.find_one({"_id": pubkey}, {"secret_key": 0, "password_hash": 0})
    if doc:
        doc["pubkey"] = pubkey
        doc["points"] = doc.get("points", 0)
    return doc

def verify_password(pubkey: str, password: str) -> bool:
    doc = col.find_one({"_id": pubkey})
    if not doc:
        return False
    return hash_password(password) == doc["password_hash"]

def load_keypair_from_db(pubkey: str):
    doc = col.find_one({"_id": pubkey}, {"secret_key": 1})
    if not doc or not doc.get("secret_key"):
        return None
    return Keypair.from_bytes(bytes(doc["secret_key"]))

def add_points(pubkey: str, pts: int):
    col.update_one({"_id": pubkey}, {"$inc": {"points": pts}})

def get_points(pubkey: str) -> int:
    doc = col.find_one({"_id": pubkey}, {"points": 1})
    return doc["points"] if doc else 0

def get_all_points() -> dict:
    return {d["_id"]: d.get("points", 0) for d in col.find({}, {"points": 1})}
