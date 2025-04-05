from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import hashlib

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

if __name__ == '__main__':
    app.run(debug=True)