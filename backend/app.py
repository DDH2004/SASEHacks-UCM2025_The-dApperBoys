from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import hashlib
import base58
from datetime import datetime
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.transaction import Transaction
import openfoodfacts

app = Flask(__name__)
CORS(app)

# In-memory storage for demo purposes
# In production, use a proper database
submissions = []

def get_solana_client(use_testnet=True):
    if use_testnet:
        return Client("http://127.0.0.1:8899")
    else:
        return Client("https://api.mainnet-beta.solana.com")

def record_disposal_proof(barcode_id, image_hash, wallet_address=None):
    try:
        client = get_solana_client()
        
        tx_id = str(uuid.uuid4())

        payer = Keypair()

        combined_hash = hashlib.sha256(f"{barcode_id}:{image_hash}".encode()).hexdigest()

        submission = {
            'id': tx_id,
            'barcode_id': barcode_id,
            'image_hash': image_hash,
            'combined_hash': combined_hash,
            'wallet_address': wallet_address,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'completed',
            'tokens_minted': 10,  # For demo, always mint 10 tokens
        }

        submissions.append(submission)

        print(f"💰 Simulated minting 10 tokens to wallet {wallet_address}")
        print(f"📝 Transaction recorded with ID: {tx_id}")

        return {
            'success': True,
            'tx_id': tx_id,
            'tokens_minted': 10,
            'submission': submission
        }

    except Exception as e:
        print(f"❌ Error recording on blockchain: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/api/proof', methods=['POST'])
def receive_proof():
    try:
        if 'barcode_id' not in request.form or 'image' not in request.files:
            return jsonify({'error': 'Missing barcode_id or image'}), 400

        barcode_id = request.form['barcode_id']
        image_file = request.files['image']
        image_data = image_file.read()
        image_hash = hashlib.sha256(image_data).hexdigest()
        
        # Get the user's wallet address
        wallet_address = request.form.get('wallet_address')
        if not wallet_address:
            return jsonify({'error': 'Missing wallet_address'}), 400

        print("✅ Received barcode:", barcode_id)
        print("🔐 Image hash:", image_hash)
        print("👛 Wallet address:", wallet_address)
        
        # Record on blockchain and mint tokens
        result = record_disposal_proof(barcode_id, image_hash, wallet_address)
        
        if not result['success']:
            return jsonify({
                'status': 'error',
                'message': 'Failed to record proof on blockchain',
                'error': result.get('error')
            }), 500

        return jsonify({
            'status': 'success',
            'message': 'Recycling proof recorded and tokens minted',
            'barcode': barcode_id,
            'image_hash': image_hash[:10] + '...',  # Truncate for display
            'transaction_id': result['tx_id'],
            'tokens_minted': result['tokens_minted'],
            'wallet': wallet_address
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """Get all recorded submissions"""
    try:
        # For a real app, you'd implement pagination
        return jsonify({
            'status': 'success',
            'count': len(submissions),
            'submissions': submissions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submissions/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    """Get a specific submission by ID"""
    try:
        submission = next((s for s in submissions if s['id'] == submission_id), None)
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
            
        return jsonify({
            'status': 'success',
            'submission': submission
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)