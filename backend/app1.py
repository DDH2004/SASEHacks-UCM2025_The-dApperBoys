#!/usr/bin/env python3
"""
server.py

Flask server providing endpoints for:
  • POST   /signup           — generate a new user wallet and password (no mint)
  • POST   /signin           — authenticate and return wallet info & balances (no mint)
  • POST   /api/validate     — validate a barcode/image proof and mint 1 SPL token
  • GET    /wallet/<pubkey>  — retrieve stored wallet info and balances

Dependencies:
  pip install flask flask-cors solana spl-token solders openfoodfacts
"""

import json
import secrets
import hashlib
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

from solana.rpc.api import Client
from solders.keypair import Keypair
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey

import openfoodfacts

from walletGen import generate_wallet
from wallet_manager import add_wallet, wallet_exists, get_wallet_info, verify_password

app = Flask(__name__)
CORS(app)

# Config
LOCAL_RPC = "http://127.0.0.1:8899"
MINT_AUTHORITY_FILE = "/Users/lalkattil/my-solana-wallet.json"
MINT_ADDRESS = "CzMUHT5wpcF331PyEvquERyrMeEnTXLQxQyKirPvnNo2"

def generate_random_password(length=16):
    return secrets.token_urlsafe(length)

def load_keypair(path):
    with open(path) as f:
        secret = json.load(f)
    return Keypair.from_bytes(bytes(secret))

def get_balances(pubkey_str):
    client = Client(LOCAL_RPC)
    sol = client.get_balance(Pubkey.from_string(pubkey_str)).value
    token_client = Token(
        conn=client,
        pubkey=Pubkey.from_string(MINT_ADDRESS),
        program_id=TOKEN_PROGRAM_ID,
        payer=load_keypair(MINT_AUTHORITY_FILE),
    )
    spl = 0
    for acct in token_client.get_accounts_by_owner(Pubkey.from_string(pubkey_str)).value:
        spl += int(client.get_token_account_balance(Pubkey.from_string(str(acct.pubkey))).value.amount)
    return {"sol": sol, "spl": spl}

def mint_spl(pubkey_str):
    mint_auth = load_keypair(MINT_AUTHORITY_FILE)
    client = Client(LOCAL_RPC)
    token = Token(
        conn=client,
        pubkey=Pubkey.from_string(MINT_ADDRESS),
        program_id=TOKEN_PROGRAM_ID,
        payer=mint_auth,
    )
    ata = token.create_account(Pubkey.from_string(pubkey_str))
    sig = token.mint_to(
        dest=ata,
        mint_authority=mint_auth,
        amount=1,
        opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed"),
    )
    return str(sig.value)

def barcode_handling(barcode_id):
    api = openfoodfacts.API(user_agent="MyApp/1.0")
    prod = api.product.get(barcode_id) or {}
    name = prod.get("product_name","unknown")
    score = prod.get("ecoscore_data",{}).get("adjustments",{}).get("packaging",{}).get("value",0)
    raw = f"{name}|{score}|{datetime.utcnow().isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()

@app.route("/signup", methods=["POST"])
def signup():
    w = generate_wallet()
    pwd = generate_random_password()
    wf = f"wallet_{w.pubkey()}.json"
    with open(wf,"w") as f: json.dump(list(w.to_bytes()), f)
    add_wallet(str(w.pubkey()), wf, pwd)
    return jsonify({"pubkey":str(w.pubkey()),"wallet_file":wf,"password":pwd})

@app.route("/signin", methods=["POST"])
def signin():
    d = request.get_json() or {}
    pk, pw = d.get("pubkey"), d.get("password")
    if not pk or not pw: return jsonify({"error":"pubkey & password required"}),400
    if not wallet_exists(pk): return jsonify({"error":"wallet not found"}),404
    if not verify_password(pk,pw): return jsonify({"error":"invalid password"}),403
    info = get_wallet_info(pk)
    bal  = get_balances(pk)
    return jsonify({"wallet_info":info,"balances":bal})

@app.route("/api/validate", methods=["POST"])
def validate_and_mint():
    f = request.form; files = request.files
    for fld in ("barcode_id","pubkey","password"):
        if fld not in f: return jsonify({"error":f"Missing {fld}"}),400
    if "image" not in files: return jsonify({"error":"Missing image"}),400
    b, pk, pw = f["barcode_id"], f["pubkey"], f["password"]
    if not wallet_exists(pk): return jsonify({"error":"wallet not found"}),404
    if not verify_password(pk,pw): return jsonify({"error":"invalid credentials"}),403
    img_hash = hashlib.sha256(files["image"].read()).hexdigest()
    sub_id   = barcode_handling(b)
    mint_sig = mint_spl(pk)
    bal      = get_balances(pk)
    return jsonify({
        "status":"success",
        "barcode_id":b,
        "image_hash":img_hash,
        "submission_id":sub_id,
        "balances":bal,
        "mint_tx":mint_sig
    })

@app.route("/wallet/<pubkey>", methods=["GET"])
def wallet_info(pubkey):
    if not wallet_exists(pubkey): return jsonify({"error":"wallet not found"}),404
    return jsonify({"wallet_info":get_wallet_info(pubkey),"balances":get_balances(pubkey)})

if __name__=="__main__":
    app.run(debug=True)
