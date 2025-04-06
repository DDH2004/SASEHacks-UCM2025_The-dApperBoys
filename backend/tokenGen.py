import json
from solana.rpc.api import Client
from solders.keypair import Keypair
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey

# Config
LOCAL_RPC = "http://127.0.0.1:8899"
MINT_AUTHORITY_FILE = "/Users/lalkattil/my-solana-wallet.json"
MINT_ADDRESS = "CzMUHT5wpcF331PyEvquERyrMeEnTXLQxQyKirPvnNo2"

def load_keypair(path: str) -> Keypair:
    with open(path) as f:
        secret = json.load(f)
    return Keypair.from_bytes(bytes(secret))

def mint_spl_token(pubkey_str: str) -> str:
    mint_auth = load_keypair(MINT_AUTHORITY_FILE)
    client = Client(LOCAL_RPC)
    token = Token(
        conn=client,
        pubkey=Pubkey.from_string(MINT_ADDRESS),
        program_id=TOKEN_PROGRAM_ID,
        payer=mint_auth
    )
    ata = token.create_account(Pubkey.from_string(pubkey_str))
    resp = token.mint_to(
        dest=ata,
        mint_authority=mint_auth,
        amount=1,
        opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed")
    )
    return str(resp.value)
