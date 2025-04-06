#!/usr/bin/env python3
"""
server2.py

Flask server with endpoints:
  • POST /signup         — generate wallet + password
  • POST /signin         — authenticate and return wallet info + SPL balance
  • POST /api/validate   — verify barcode is real, validate image, mint tokens based on recyclability
  • GET  /wallet/<pubkey>— retrieve wallet info + SPL balance
"""

import json
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import openfoodfacts

from solana.rpc.api import Client
from solders.pubkey import Pubkey

from walletGen import generate_wallet
from wallet_manager import add_wallet, wallet_exists, get_wallet_info, verify_password
from tokenGen import mint_spl_token, get_spl_balance

import requests

app = Flask(__name__)
CORS(app)

def fetch_product(barcode_id: str):
    """
    Fetch product data via the OpenFoodFacts REST API.
    Returns the 'product' dict if status == 1, else None.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_id}.json"
    resp = requests.get(url, timeout=5)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if data.get("status") == 1:
        return data["product"]
    return None

def fetch_packaging_score(product: dict) -> int:
    """Extract packaging ecoscore (0–100) from product dict."""
    return product.get("ecoscore_data", {}) \
                  .get("adjustments", {}) \
                  .get("packaging", {}) \
                  .get("value", 0)

def map_score_to_tokens(score: int) -> int:
    """Map a 0–100 score into 1–5 tokens."""
    return min(5, max(1, score // 20 + 1))

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
    info    = get_wallet_info(pk)
    spl_bal = get_spl_balance(pk)
    return jsonify({"wallet_info": info, "spl_balance": spl_bal})

@app.route("/api/validate", methods=["POST"])
def validate_and_mint():
    form, files = request.form, request.files
    for f in ("barcode_id","pubkey","password"):
        if f not in form:
            return jsonify({"error":f"Missing {f}"}), 400
    if "image" not in files:
        return jsonify({"error":"Missing image"}), 400

    barcode_id = form["barcode_id"]
    pubkey     = form["pubkey"]
    password   = form["password"]

    # 1) Authenticate
    if not wallet_exists(pubkey):
        return jsonify({"error":"wallet not found"}), 404
    if not verify_password(pubkey, password):
        return jsonify({"error":"invalid credentials"}), 403

    # 2) Verify barcode is real
    product = fetch_product(barcode_id)
    if product is None:
        return jsonify({"error":"invalid barcode"}), 400

    # 3) Compute image hash
    image_hash = hashlib.sha256(files["image"].read()).hexdigest()

    # 4) Compute recyclability score & token count
    score  = fetch_packaging_score(product)
    tokens = map_score_to_tokens(score)

    # 5) Unique submission ID
    submission_id = hashlib.sha256(
        f"{barcode_id}|{image_hash}|{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()

    # 6) Mint tokens
    mint_tx   = mint_spl_token(pubkey, submission_id, tokens)
    spl_bal   = get_spl_balance(pubkey)

    return jsonify({
        "status":          "success",
        "barcode_id":      barcode_id,
        "image_hash":      image_hash,
        "packaging_score": score,
        "tokens_minted":   tokens,
        "submission_id":   submission_id,
        "mint_tx":         mint_tx,
        "spl_balance":     spl_bal
    })

@app.route("/wallet/<pubkey>", methods=["GET"])
def wallet_info(pubkey):
    if not wallet_exists(pubkey):
        return jsonify({"error":"wallet not found"}), 404
    info    = get_wallet_info(pubkey)
    spl_bal = get_spl_balance(pubkey)
    return jsonify({"wallet_info": info, "spl_balance": spl_bal})

if __name__=="__main__":
    app.run(debug=True)
