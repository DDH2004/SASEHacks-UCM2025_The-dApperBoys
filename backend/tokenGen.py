import json
from solana.rpc.api import Client
from solders.keypair import Keypair
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey

# Configuration
LOCAL_RPC = "http://127.0.0.1:8899"
MINT_AUTHORITY_FILE = "/Users/lalkattil/my-solana-wallet.json"
MINT_ADDRESS = "CzMUHT5wpcF331PyEvquERyrMeEnTXLQxQyKirPvnNo2"

def load_keypair(path: str) -> Keypair:
    with open(path, "r") as f:
        secret = json.load(f)
    return Keypair.from_bytes(bytes(secret))

def mint_spl_token(pubkey_str: str, submission_id: str, amount: int) -> str:
    """
    Mint `amount` SPL tokens to `pubkey_str`. Returns transaction signature.
    """
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
        amount=amount,
        opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed"),
    )
    return str(resp.value)

def get_spl_balance(pubkey_str: str) -> int:
    """
    Return the SPL token balance for the given public key.
    """
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
