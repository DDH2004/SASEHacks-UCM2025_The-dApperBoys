#!/usr/bin/env python3
"""
server.py

Flask server providing endpoints for:
  • POST /signup    — generate a new user wallet and password
  • POST /signin    — authenticate and mint a token
  • POST /api/validate — validate a barcode/image proof and mint a token

Dependencies:
  pip install flask flask-cors solana spl-token solders openfoodfacts

Make sure walletGen.py, wallet_manager.py, and tokenGen.py (if used) are in the same folder.
"""

import json
import getpass
import secrets
import hashlib
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

from solana.rpc.api import Client
from solders.keypair import Keypair
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey

import openfoodfacts

from walletGen import generate_wallet
from wallet_manager import add_wallet, wallet_exists, get_wallet_info, verify_password

app = Flask(__name__)
CORS(app)

# Configuration
LOCAL_RPC = "http://127.0.0.1:8899"
MINT_AUTHORITY_FILE = "/Users/lalkattil/my-solana-wallet.json"
MINT_ADDRESS = "CzMUHT5wpcF331PyEvquERyrMeEnTXLQxQyKirPvnNo2"

def generate_random_password(length: int = 16) -> str:
    return secrets.token_urlsafe(length)

def load_keypair_from_file(filepath: str) -> Keypair:
    with open(filepath, "r") as f:
        secret = json.load(f)
    return Keypair.from_bytes(bytes(secret))

def mint_token(pubkey_str: str) -> str:
    """Mint 1 token to the given wallet public key on the local validator."""
    # Load mint authority
    mint_auth = load_keypair_from_file(MINT_AUTHORITY_FILE)
    client = Client(LOCAL_RPC)
    token = Token(
        conn=client,
        pubkey=Pubkey.from_string(MINT_ADDRESS),
        program_id=TOKEN_PROGRAM_ID,
        payer=mint_auth,
    )
    ata = token.create_account(Pubkey.from_string(pubkey_str))
    resp = token.mint_to(
        dest=ata,
        mint_authority=mint_auth,
        amount=1,
        opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed"),
    )
    return str(resp.value)

def barcode_handling(barcode_id: str) -> str:
    """Fetch product info and generate a unique submission ID."""
    api = openfoodfacts.API(user_agent="MyAwesomeApp/1.0")
    product = api.product.get(barcode_id) or {}
    name = product.get('product_name', 'unknown_product')
    score = (
        product
        .get('ecoscore_data', {})
        .get('adjustments', {})
        .get('packaging', {})
        .get('value', 0)
    )
    raw = f"{name}|{score}|{datetime.utcnow().isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()

@app.route("/signup", methods=["POST"])
def signup():
    """Generate a new wallet and password for a user."""
    wallet = generate_wallet()
    password = generate_random_password()
    wallet_file = f"wallet_{wallet.pubkey()}.json"

    # Persist secret key
    with open(wallet_file, "w") as f:
        json.dump(list(wallet.to_bytes()), f)

    # Store in DB
    add_wallet(str(wallet.pubkey()), wallet_file, password)

    return jsonify({
        "pubkey": str(wallet.pubkey()),
        "wallet_file": wallet_file,
        "password": password
    })

@app.route("/signin", methods=["POST"])
def signin():
    """Authenticate user and mint a token."""
    data = request.get_json() or {}
    pubkey   = data.get("pubkey")
    password = data.get("password")
    if not pubkey or not password:
        return jsonify({"error":"pubkey and password required"}), 400
    if not wallet_exists(pubkey):
        return jsonify({"error":"wallet not found"}), 400
    if not verify_password(pubkey, password):
        return jsonify({"error":"invalid password"}), 400

    info = get_wallet_info(pubkey)
    tx_sig = mint_token(pubkey)
    return jsonify({
        "wallet_info": info,
        "mint_tx": tx_sig
    })

@app.route("/api/validate", methods=["POST"])
def validate_and_mint():
    """
    Validate a barcode proof and mint a token.
    Expects multipart/form-data:
      - barcode_id (str)
      - image (file)
      - pubkey (str)
      - password (str)
    """
    form = request.form
    files = request.files
    for field in ("barcode_id","pubkey","password"):
        if field not in form:
            return jsonify({"error":f"Missing field '{field}'"}), 400
    if "image" not in files:
        return jsonify({"error":"Missing image file"}), 400

    barcode_id = form["barcode_id"]
    pubkey     = form["pubkey"]
    password   = form["password"]

    if not wallet_exists(pubkey):
        return jsonify({"error":"wallet not found"}), 400
    if not verify_password(pubkey, password):
        return jsonify({"error":"invalid credentials"}), 400

    img = files["image"].read()
    image_hash    = hashlib.sha256(img).hexdigest()
    submission_id = barcode_handling(barcode_id)
    mint_tx       = mint_token(pubkey)

    return jsonify({
        "status": "success",
        "barcode_id": barcode_id,
        "image_hash": image_hash,
        "submission_id": submission_id,
        "mint_tx": mint_tx
    })

if __name__ == "__main__":
    app.run(debug=True)
