# tokenGenvoting.py
import json
from solana.rpc.api import Client
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey
from solders.keypair import Keypair

LOCAL_RPC = "http://127.0.0.1:8899"
PRIMARY_MINT = "BF1WUaksg6FkFGwDYeztCLvCT9Lwywu6MgvQpYdADpzo"
REWARD_MINT  = "Fc6JFBpVDYmWRKtDxx2keGrne3uWFSMYSvTxYFJDiZ7T"
MINT_AUTH_PUBKEY = "7bS2Vfj9p2Nuz6sgEqtpsMCRqzWRRFo24Xv2M5db7EA3"

def load_authority():
    with open("reward-wallet.json", "r") as f:
        secret = json.load(f)
    wallet = Keypair.from_bytes(bytes(secret))
    print("🔍 Loaded mint authority pubkey:", wallet.pubkey())
    return wallet

def mint_spl_token(pubkey_str: str, amount: int, mint_address: str) -> str:
    auth = load_authority()
    client = Client(LOCAL_RPC)
    token = Token(conn=client, pubkey=Pubkey.from_string(mint_address),
                  program_id=TOKEN_PROGRAM_ID, payer=auth)
    user_pubkey = Pubkey.from_string(pubkey_str)
    ata = get_associated_token_address(user_pubkey, token.pubkey)
    try:
        token.get_account_info(ata)
    except Exception:
        token.create_associated_token_account(user_pubkey)
    resp = token.mint_to(ata, auth, amount, opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed"))
    return str(resp.value)

def mint_primary(pubkey_str: str, amount: int) -> str:
    return mint_spl_token(pubkey_str, amount, PRIMARY_MINT)

def mint_reward(pubkey_str: str, amount: int) -> str:
    return mint_spl_token(pubkey_str, amount, REWARD_MINT)

def get_spl_balance(pubkey_str: str, mint_address: str) -> int:
    auth = load_authority()
    client = Client(LOCAL_RPC)
    token = Token(conn=client, pubkey=Pubkey.from_string(mint_address),
                  program_id=TOKEN_PROGRAM_ID, payer=auth)
    total = 0
    for acct in token.get_accounts_by_owner(Pubkey.from_string(pubkey_str)).value:
        bal = client.get_token_account_balance(Pubkey.from_string(str(acct.pubkey)))
        total += int(bal.value.amount)
    return total

def get_primary_balance(pubkey_str: str) -> int:
    return get_spl_balance(pubkey_str, PRIMARY_MINT)

def get_reward_balance(pubkey_str: str) -> int:
    return get_spl_balance(pubkey_str, REWARD_MINT)
