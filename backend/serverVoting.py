#!/usr/bin/env python3

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import hashlib

from walletGenVoting import generate_wallet
from wallet_manager_voting import (
    add_wallet, wallet_exists, get_wallet_info, verify_password
)
from tokenGenVoting import (
    mint_primary, get_primary_balance,
    mint_reward, get_reward_balance,
    load_authority, PRIMARY_MINT, REWARD_MINT
)

from solders.pubkey import Pubkey

from solana.rpc.api import Client
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.pubkey import Pubkey

from solana.rpc.types import MemcmpOpts


app = Flask(__name__)
CORS(app)

def fetch_product(barcode_id):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_id}.json"
    r = requests.get(url, timeout=5)
    if r.status_code != 200: return None
    d = r.json()
    return d["product"] if d.get("status") == 1 else None

def map_score_to_tokens(score):
    return min(5, max(1, score // 20 + 1))

@app.route("/signup", methods=["POST"])
def signup():
    pk, sk, pwd = generate_wallet()
    add_wallet(pk, sk, pwd)
    return jsonify({"pubkey": pk, "password": pwd})

@app.route("/signin", methods=["POST"])
def signin():
    d = request.get_json() or {}
    pk, pw = d.get("pubkey"), d.get("password")
    if not pk or not pw:
        return jsonify({"error": "pubkey & password required"}), 400
    if not wallet_exists(pk):
        return jsonify({"error": "wallet not found"}), 404
    if not verify_password(pk, pw):
        return jsonify({"error": "invalid password"}), 403
    return jsonify({
        "wallet_info": get_wallet_info(pk),
        "primary_balance": get_primary_balance(pk),
        "reward_balance": get_reward_balance(pk)
    })

@app.route("/api/validate", methods=["POST"])
def validate_and_mint():
    form, files = request.form, request.files
    for f in ("barcode_id", "pubkey", "password"):
        if f not in form: return jsonify({"error": f"Missing {f}"}), 400
    if "image" not in files:
        return jsonify({"error": "Missing image"}), 400

    b, pk, pw = form["barcode_id"], form["pubkey"], form["password"]
    if not wallet_exists(pk):
        return jsonify({"error": "wallet not found"}), 404
    if not verify_password(pk, pw):
        return jsonify({"error": "invalid credentials"}), 403

    prod = fetch_product(b)
    if not prod: return jsonify({"error": "invalid barcode"}), 400

    img_hash = hashlib.sha256(files["image"].read()).hexdigest()
    score = prod.get("ecoscore_data", {}).get("adjustments", {}).get("packaging", {}).get("value", 0)
    tokens = map_score_to_tokens(score)
    sub_id = hashlib.sha256(f"{b}|{img_hash}|{datetime.utcnow().isoformat()}".encode()).hexdigest()

    tx_primary = mint_primary(pk, tokens)
    primary = get_primary_balance(pk)

    return jsonify({
        "status": "success", "barcode_id": b, "image_hash": img_hash,
        "packaging_score": score, "tokens_minted": tokens,
        "submission_id": sub_id, "primary_mint_tx": tx_primary,
        "primary_balance": primary
    })

@app.route("/distribute", methods=["GET"])
def distribute_rewards():
    print("⚡ Distribute route triggered")
    auth = load_authority()
    client = Client("http://127.0.0.1:8899")

    # Use base64 encoding to avoid JSON decoding issues
    resp = client.get_program_accounts(
        TOKEN_PROGRAM_ID,
        encoding="base64",  # <- avoids SerdeJSONError
        filters=[
            MemcmpOpts(offset=0, bytes=PRIMARY_MINT)
        ]
    )

    holders = {}
    total_votes = 0

    # Step through each account and check token balance + owner
    for acct in resp.value:
        account_pubkey = acct.pubkey
        bal_resp = client.get_token_account_balance(account_pubkey)
        info_resp = client.get_account_info(account_pubkey)

        amount = int(bal_resp.value.amount)
        owner = str(info_resp.value.owner)

        if amount > 0:
            holders[owner] = holders.get(owner, 0) + amount
            total_votes += amount

    if total_votes == 0:
        return jsonify({"error": "no holders"}), 400

    # Proportional reward calculation
    distribution = {}
    tokens_left = 100
    for owner, votes in holders.items():
        amt = (votes * 100) // total_votes
        distribution[owner] = amt
        tokens_left -= amt

    sorted_holders = sorted(holders.items(), key=lambda x: x[1], reverse=True)
    idx = 0
    while tokens_left > 0:
        o = sorted_holders[idx % len(sorted_holders)][0]
        distribution[o] += 1
        tokens_left -= 1
        idx += 1

    # Mint rewards
    reward_token = Token(
        conn=client,
        pubkey=Pubkey.from_string(REWARD_MINT),
        program_id=TOKEN_PROGRAM_ID,
        payer=auth
    )

    tx_results = {}
    for owner, amt in distribution.items():
        owner_pubkey = Pubkey.from_string(owner)
        try:
            ata = reward_token.create_associated_token_account(owner_pubkey)
        except Exception:
            ata = reward_token.get_associated_token_address(owner_pubkey)
        reward_token.mint_to(ata, auth, amt)
        tx_results[owner] = amt


    return jsonify({
        "distribution": tx_results,
        "reward_mint": REWARD_MINT
    })






@app.route("/wallet/<pubkey>", methods=["GET"])
def wallet_info(pubkey):
    if not wallet_exists(pubkey): return jsonify({"error": "wallet not found"}), 404
    return jsonify({
        "wallet_info": get_wallet_info(pubkey),
        "primary_balance": get_primary_balance(pubkey),
        "reward_balance": get_reward_balance(pubkey)
    })

if __name__ == "__main__":
    app.run(port=8888, debug=True)
