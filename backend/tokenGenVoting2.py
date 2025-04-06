from solana.rpc.api import Client
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey

from wallet_manager_voting2 import load_keypair_from_db

# Configuration
LOCAL_RPC = "http://127.0.0.1:8899"
# Authority keypair stored in Mongo (must be upserted via your authority setup)
MINT_AUTH_PUBKEY = "GckMqwD5e17U2tadgLm5TDsG6x41CpJdVhZkTSijtw1y"
# Reward token mint address (created with spl-token create-token)
REWARD_MINT = "F7bcyQmc6WCinDdF1eLN81qJbW88wUb1N9zJP9WHEt9B"

# Shyam pubkey- F7bcyQmc6WCinDdF1eLN81qJbW88wUb1N9zJP9WHEt9B

def load_authority():
    auth = load_keypair_from_db(MINT_AUTH_PUBKEY)
    if auth is None:
        raise RuntimeError(f"Mint authority {MINT_AUTH_PUBKEY} not found in MongoDB")
    return auth

def get_token_client(mint_address: str, authority):
    client = Client(LOCAL_RPC)
    return Token(
        conn=client,
        pubkey=Pubkey.from_string(mint_address),
        program_id=TOKEN_PROGRAM_ID,
        payer=authority
    )

def mint_spl_token(pubkey_str: str, amount: int, mint_address: str) -> str:
    auth = load_authority()
    token = get_token_client(mint_address, auth)
    # Create (or fetch) the associated token account (ATA) for the destination pubkey.
    ata = token.create_associated_token_account(Pubkey.from_string(pubkey_str))
    resp = token.mint_to(
        dest=ata,
        mint_authority=auth,
        amount=amount,
        opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed")
    )
    return str(resp.value)

def mint_reward(pubkey_str: str, amount: int) -> str:
    return mint_spl_token(pubkey_str, amount, REWARD_MINT)

def get_reward_balance(pubkey_str: str) -> int:
    auth = load_authority()
    token = get_token_client(REWARD_MINT, auth)
    total = 0
    for acct in token.get_accounts_by_owner(Pubkey.from_string(pubkey_str)).value:
        bal = token._conn.get_token_account_balance(Pubkey.from_string(str(acct.pubkey)))
        total += int(bal.value.amount)
    return total
