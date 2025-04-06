#!/usr/bin/env python3
"""
server2.py

Flask server with endpoints:
  • POST   /signup
  • POST   /signin
  • POST   /api/validate
  • GET    /wallet/<pubkey>   — now returns stored info + SPL balance
"""

import json
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import openfoodfacts

from solana.rpc.api import Client
from solders.keypair import Keypair
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey

from walletGen import generate_wallet
from wallet_manager import add_wallet, wallet_exists, get_wallet_info, verify_password
from tokenGen import mint_spl_token, load_keypair, LOCAL_RPC, MINT_ADDRESS, MINT_AUTHORITY_FILE

app = Flask(__name__)
CORS(app)

def get_spl_balance(pubkey_str: str) -> int:
    """Return the SPL token balance for the given public key."""
    client = Client(LOCAL_RPC)
    token = Token(
        conn=client,
        pubkey=Pubkey.from_string(MINT_ADDRESS),
        program_id=TOKEN_PROGRAM_ID,
        payer=load_keypair(MINT_AUTHORITY_FILE),
    )
    total = 0
    for acct in token.get_accounts_by_owner(Pubkey.from_string(pubkey_str)).value:
        bal = client.get_token_account_balance(Pubkey.from_string(str(acct.pubkey)))
        total += int(bal.value.amount)
    return total

def barcode_handling(barcode_id: str) -> str:
    api = openfoodfacts.API(user_agent="MyApp/1.0")
    product = api.product.get(barcode_id) or {}
    name = product.get('product_name', 'unknown')
    score = product.get('ecoscore_data', {}) \
                   .get('adjustments', {}) \
                   .get('packaging', {}) \
                   .get('value', 0)
    raw = f"{name}|{score}|{datetime.utcnow().isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()

@app.route("/signup", methods=["POST"])
def signup():
    wallet, password, wallet_file = generate_wallet()
    add_wallet(str(wallet.pubkey()), wallet_file, password)
    return jsonify({
        "pubkey": str(wallet.pubkey()),
        "wallet_file": wallet_file,
        "password": password
    })

@app.route("/signin", methods=["POST"])
def signin():
    data = request.get_json() or {}
    pk, pw = data.get("pubkey"), data.get("password")
    if not pk or not pw:
        return jsonify({"error":"pubkey & password required"}), 400
    if not wallet_exists(pk):
        return jsonify({"error":"wallet not found"}), 404
    if not verify_password(pk, pw):
        return jsonify({"error":"invalid password"}), 403
    info   = get_wallet_info(pk)
    balance = get_spl_balance(pk)
    return jsonify({
        "wallet_info": info,
        "spl_balance": balance
    })

@app.route("/api/validate", methods=["POST"])
def validate_and_mint():
    form, files = request.form, request.files
    for f in ("barcode_id","pubkey","password"):
        if f not in form:
            return jsonify({"error":f"Missing {f}"}), 400
    if "image" not in files:
        return jsonify({"error":"Missing image"}), 400

    b, pk, pw = form["barcode_id"], form["pubkey"], form["password"]
    if not wallet_exists(pk):
        return jsonify({"error":"wallet not found"}), 404
    if not verify_password(pk, pw):
        return jsonify({"error":"invalid credentials"}), 403

    img_hash = hashlib.sha256(files["image"].read()).hexdigest()
    sub_id   = barcode_handling(b)
    tx       = mint_spl_token(pk)
    balance  = get_spl_balance(pk)
    return jsonify({
        "status": "success",
        "barcode_id": b,
        "image_hash": img_hash,
        "submission_id": sub_id,
        "spl_balance": balance,
        "mint_tx": tx
    })

@app.route("/wallet/<pubkey>", methods=["GET"])
def wallet_info(pubkey):
    if not wallet_exists(pubkey):
        return jsonify({"error":"wallet not found"}), 404
    info    = get_wallet_info(pubkey)
    balance = get_spl_balance(pubkey)
    return jsonify({
        "wallet_info": info,
        "spl_balance": balance
    })

if __name__ == "__main__":
    app.run(debug=True)
