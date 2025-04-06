# save_authority.py

from pymongo import MongoClient
import hashlib
import json

# Load the secret_key list from the JSON file
with open("authority.json","r") as f:
    SECRET_KEY_LIST = json.load(f)

# Your new authority pubkey
MINT_AUTH_PUBKEY = "GckMqwD5e17U2tadgLm5TDsG6x41CpJdVhZkTSijtw1y"

client = MongoClient("mongodb://localhost:27017/")
db     = client["sasehacks"]
col    = db["wallets"]

dummy_pw_hash = hashlib.sha256(b"authority").hexdigest()

col.replace_one(
    {"_id": MINT_AUTH_PUBKEY},
    {
        "_id": MINT_AUTH_PUBKEY,
        "secret_key": SECRET_KEY_LIST,
        "password_hash": dummy_pw_hash,
        "points": 0
    },
    upsert=True
)

print(f"Authority {MINT_AUTH_PUBKEY} upserted into MongoDB.")
