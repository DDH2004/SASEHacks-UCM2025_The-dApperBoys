#!/usr/bin/env python3
"""
server2.py

Flask server using MongoDB for wallet storage and
minting custom SPL tokens on /api/validate.
"""

import hashlib
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

import requests
import openfoodfacts
from solana.rpc.api import Client
from solders.pubkey import Pubkey

from walletGenMongo import generate_wallet
from wallet_manager_mongo import add_wallet, wallet_exists, get_wallet_info, verify_password
from tokenGenMongo import mint_spl_token, get_spl_balance

app = Flask(__name__)
CORS(app)

def fetch_product(barcode_id: str):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_id}.json"
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        return None
    d = r.json()
    if d.get("status") == 1:
        return d["product"]
    return None

def map_score_to_tokens(score: int) -> int:
    return min(5, max(1, score // 20 + 1))

@app.route("/signup", methods=["POST"])
def signup():
    pubkey, secret_key, password = generate_wallet()
    add_wallet(pubkey, secret_key, password)
    return jsonify({"pubkey":pubkey,"password":password})

@app.route("/signin", methods=["POST"])
def signin():
    d = request.get_json() or {}
    pk, pw = d.get("pubkey"), d.get("password")
    if not pk or not pw:
        return jsonify({"error":"pubkey & password required"}),400
    if not wallet_exists(pk):
        return jsonify({"error":"wallet not found"}),404
    if not verify_password(pk,pw):
        return jsonify({"error":"invalid password"}),403
    info    = get_wallet_info(pk)
    spl_bal = get_spl_balance(pk)
    return jsonify({"wallet_info":info,"spl_balance":spl_bal})

@app.route("/api/validate", methods=["POST"])
def validate_and_mint():
    form, files = request.form, request.files
    for f in ("barcode_id","pubkey","password"):
        if f not in form:
            return jsonify({"error":f"Missing {f}"}),400
    if "image" not in files:
        return jsonify({"error":"Missing image"}),400

    b, pk, pw = form["barcode_id"], form["pubkey"], form["password"]
    if not wallet_exists(pk):
        return jsonify({"error":"wallet not found"}),404
    if not verify_password(pk,pw):
        return jsonify({"error":"invalid credentials"}),403

    product = fetch_product(b)
    if not product:
        return jsonify({"error":"invalid barcode"}),400

    image_hash    = hashlib.sha256(files["image"].read()).hexdigest()
    score         = product.get("ecoscore_data",{}).get("adjustments",{}).get("packaging",{}).get("value",0)
    tokens        = map_score_to_tokens(score)
    submission_id = hashlib.sha256(f"{b}|{image_hash}|{datetime.utcnow().isoformat()}".encode()).hexdigest()

    mint_tx    = mint_spl_token(pk, tokens)
    spl_bal    = get_spl_balance(pk)

    return jsonify({
        "status":          "success",
        "barcode_id":      b,
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
        return jsonify({"error":"wallet not found"}),404
    info    = get_wallet_info(pubkey)
    spl_bal = get_spl_balance(pubkey)
    return jsonify({"wallet_info":info,"spl_balance":spl_bal})

if __name__=="__main__":
    app.run(debug=True)
