from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import hashlib
from solana.rpc.api import Client
from solders.keypair import Keypair

app = Flask(__name__)
CORS(app)

# In-memory storage for demo purposes
# In production, use a proper database
submissions = []

@app.route('/api/submit', methods=['POST'])
def submit_proof():
    """
    Submit a new environmental action proof
    Expected payload:
    {
        "barcode": "123456789",
        "image_hash": "perceptual_hash_here",
        "wallet_address": "solana_wallet_address",
        "location": {"lat": 123.45, "lng": 67.89},
        "timestamp": "2024-03-14T12:00:00Z"
    }
    """
    try:
        data = request.json
        
        # Basic validation
        required_fields = ['barcode', 'wallet_address', 'location', 'timestamp']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Generate unique submission ID
        submission_id = hashlib.sha256(
            f"{data['barcode']}{data['wallet_address']}{data['timestamp']}".encode()
        ).hexdigest()
        
        # Check for duplicates
        if any(s['id'] == submission_id for s in submissions):
            return jsonify({'error': 'Duplicate submission'}), 409
        
        # Store submission
        submission = {
            'id': submission_id,
            **data,
            'verified': False,
            'processed_at': datetime.utcnow().isoformat()
        }
        submissions.append(submission)
        
        return jsonify({
            'status': 'success',
            'submission_id': submission_id,
            'message': 'Proof submitted successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submissions/<wallet_address>', methods=['GET'])
def get_submissions(wallet_address):
    """Get all submissions for a specific wallet address"""
    user_submissions = [s for s in submissions if s['wallet_address'] == wallet_address]
    return jsonify(user_submissions)

@app.route('/api/encrypt', methods=['GET'])
def encrypt_data(barcode_id, image):
    """
    Encrypt an image and a string.
    Expected payload:
    {
        "image_data": "base64_encoded_image",
        "text": "string_to_encrypt"
    }
    """
    try:
        data = request.json
            
        # Basic validation
        if 'image_data' not in data or 'text' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Combine image data and text
        combined_data = f"{data['image_data']}{data['text']}"
            
        # Encrypt using SHA-256
        encrypted_data = hashlib.sha256(combined_data.encode()).hexdigest()
            
        return jsonify({
            'status': 'success',
            'encrypted_data': encrypted_data
        }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-barcode', methods=['POST'])
def process_barcode():
    """
    Process a barcode ID and an image from the frontend
    
    Form data:
    - barcode_id: String identifier of the barcode
    - image: Image file uploaded from frontend
    """
    try:
        # Check if barcode_id was provided
        if 'barcode_id' not in request.form:
            return jsonify({'error': 'Missing barcode_id'}), 400
        
        # Check if image was provided
        if 'image' not in request.files:
            return jsonify({'error': 'Missing image file'}), 400
            
        barcode_id = request.form['barcode_id']
        image_file = request.files['image']
        
        # Read image data
        image_data = image_file.read()
        
        # Process the image and barcode as needed
        # Example: Create a unique hash from the image and barcode
        image_hash = hashlib.sha256(image_data + barcode_id.encode()).hexdigest()
        
        # Here you would add your specific processing logic
        
        return jsonify({
            'status': 'success',
            'barcode_id': barcode_id,
            'image_hash': image_hash,
            'message': 'Image and barcode processed successfully'
        }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reward', methods=['POST'])
def reward_for_recycling():
    """Reward a user for recycling actions"""
    try:
        data = request.json
        
        # Basic validation
        required_fields = ['wallet_address', 'submission_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find the submission
        submission = next((s for s in submissions if s['id'] == data['submission_id']), None)
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
            
        if submission['wallet_address'] != data['wallet_address']:
            return jsonify({'error': 'Wallet address mismatch'}), 403
            
        # Add reward logic here
        # For demonstration, we'll just mark it as rewarded
        submission['rewarded'] = True
        submission['reward_timestamp'] = datetime.utcnow().isoformat()
        
        # In a real app, you would trigger a Solana transaction here
        # Example: transfer_sol(admin_wallet, submission['wallet_address'], 0.01)
        
        return jsonify({
            'status': 'success',
            'message': 'Reward processed successfully',
            'submission_id': data['submission_id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize Solana client
def get_solana_client(use_localnet=True):
    """Get a Solana client instance"""
    if use_localnet:
        return Client("http://127.0.0.1:8899")
    else:
        return Client("https://api.mainnet-beta.solana.com")

@app.route('/api/solana/wallet/new', methods=['GET'])
def generate_wallet():
    """Generate a new Solana wallet"""
    try:
        # Create a new keypair
        keypair = Keypair()
        
        # Return the public and private keys (in practice, secure the private key)
        return jsonify({
            'status': 'success',
            'public_key': str(keypair.public_key),
            'private_key': keypair.secret_key.hex(),  # In production, never return this directly
            'message': 'New wallet generated'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solana/status', methods=['GET'])
def solana_status():
    """Check Solana connection status"""
    try:
        client = get_solana_client()
        version = client.get_version()
        return jsonify({
            'status': 'connected',
            'version': version['result']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)