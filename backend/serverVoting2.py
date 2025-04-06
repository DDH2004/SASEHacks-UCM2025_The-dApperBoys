#!/usr/bin/env python3
"""
serverVoting2.py

Flask server with endpoints:
  • POST /signup
  • POST /signin
  • POST /api/validate
  • GET  /wallet/<pubkey>
  • GET  /distribute
"""

import hashlib
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

from walletGenVoting2 import generate_wallet
from wallet_manager_voting2 import (
    add_wallet, wallet_exists, get_wallet_info,
    verify_password, add_points, get_points, get_all_points, col
)
from tokenGenVoting2 import mint_reward, get_reward_balance, REWARD_MINT

app = Flask(__name__)
CORS(app)

def fetch_product(barcode_id):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_id}.json"
    r = requests.get(url, timeout=5)
    if r.status_code != 200:
        return None
    d = r.json()
    return d["product"] if d.get("status") == 1 else None

def map_score_to_points(score: int) -> int:
    # Map a packaging score (0-100) to points (1-5)
    return min(5, max(1, score // 20 + 1))

@app.route("/signup", methods=["POST"])
def signup():
    pk, sk, pwd = generate_wallet()
    add_wallet(pk, sk, pwd)
    return jsonify({"pubkey": pk, "password": pwd})

@app.route("/signin", methods=["POST"])
def signin():
    data = request.get_json() or {}
    pk, pw = data.get("pubkey"), data.get("password")
    if not pk or not pw:
        return jsonify({"error": "pubkey & password required"}), 400
    if not wallet_exists(pk):
        return jsonify({"error": "wallet not found"}), 404
    if not verify_password(pk, pw):
        return jsonify({"error": "invalid password"}), 403
    info = get_wallet_info(pk)
    return jsonify({
        "wallet_info": info,
        "points": info.get("points", 0),
        "reward_balance": get_reward_balance(pk)
    })

@app.route("/api/validate", methods=["POST"])
def validate_and_award():
    form, files = request.form, request.files
    for field in ("barcode_id", "pubkey", "password"):
        if field not in form:
            return jsonify({"error": f"Missing {field}"}), 400
    if "image" not in files:
        return jsonify({"error": "Missing image"}), 400

    barcode = form["barcode_id"]
    pk = form["pubkey"]
    pw = form["password"]

    if not wallet_exists(pk):
        return jsonify({"error": "wallet not found"}), 404
    if not verify_password(pk, pw):
        return jsonify({"error": "invalid credentials"}), 403

    prod = fetch_product(barcode)
    if not prod:
        return jsonify({"error": "invalid barcode"}), 400
    
    if "image" not in files:
        return jsonify({"error": "Missing image"}), 400

    # Read image bytes and compute its SHA256 hash
    img_bytes = files["image"].read()
    img_hash = hashlib.sha256(img_bytes).hexdigest()

    score = prod.get("ecoscore_data", {}).get("adjustments", {}).get("packaging", {}).get("value", 0)
    pts = map_score_to_points(score)
    add_points(pk, pts)
    total_pts = get_points(pk)
    submission_id = hashlib.sha256(f"{barcode}|{img_hash}|{datetime.utcnow().isoformat()}".encode()).hexdigest()

    return jsonify({
        "status": "success",
        "barcode_id": barcode,
        "image_hash": img_hash,
        "packaging_score": score,
        "points_awarded": pts,
        "total_points": total_pts,
        "submission_id": submission_id
    })

@app.route("/wallet/<pubkey>", methods=["GET"])
def wallet_info(pubkey):
    # Comment out the existing logic
    if not wallet_exists(pubkey):
        return jsonify({"error": "wallet not found"}), 404
    info = get_wallet_info(pubkey)
    return jsonify({
        "wallet_info": info,
        "points": info.get("points", 0),
        "reward_balance": get_reward_balance(pubkey)
    })

    # Example response for testing
    # return jsonify({
    #     "wallet_info": {
    #         "pubkey": "DbF9bJhRDpteh9Q8nF13r4GiPN5m1eDfZp6rT4KFwyjC",
    #         "points": 3
    #     },
    #     "points": 3,
    #     "reward_balance": 0
    # })

@app.route("/distribute", methods=["GET"])
def distribute_rewards():
    pts_map = get_all_points()
    total_pts = sum(pts_map.values())
    if total_pts == 0:
        return jsonify({"error": "no points to distribute"}), 400

    # Compute proportional shares of 100 tokens.
    raw_shares = {pk: (pts / total_pts) * 100 for pk, pts in pts_map.items()}
    floor_shares = {pk: int(raw_shares[pk]) for pk in raw_shares}
    distributed = sum(floor_shares.values())
    remainder = 100 - distributed

    # Distribute any remainder to wallets with the largest fractional parts.
    sorted_keys = sorted(raw_shares.keys(), key=lambda k: raw_shares[k] - floor_shares[k], reverse=True)
    for pk in sorted_keys[:remainder]:
        floor_shares[pk] += 1

    txs = {}
    for pk, amt in floor_shares.items():
        if amt > 0:
            txs[pk] = mint_reward(pk, amt)
    # Reset all wallet points
    col.update_many({}, {"$set": {"points": 0}})
    return jsonify({
        "distribution": floor_shares,
        "reward_mint": REWARD_MINT,
        "txs": txs
    })

RPC_URL = "http://127.0.0.1:8899"
from solders.pubkey import Pubkey
from solana.rpc.api import Client

@app.route("/total", methods=["GET"])
def total_supply():
    """
    Return the total minted supply of the reward token.
    """
    client = Client(RPC_URL)
    resp = client.get_token_supply(Pubkey.from_string(REWARD_MINT))
    if not resp or not resp.value:
        return jsonify({"error": "could not fetch supply"}), 500

    # amount is a string, decimals is an int
    amount = int(resp.value.amount)
    decimals = resp.value.decimals

    # present a human‑readable value
    human = amount / (10 ** decimals)
    return jsonify({
        "mint": REWARD_MINT,
        "amount_raw": amount,
        "decimals": decimals,
        "amount": human
    })

if __name__ == "__main__":
    app.run(port=8888, debug=True)
