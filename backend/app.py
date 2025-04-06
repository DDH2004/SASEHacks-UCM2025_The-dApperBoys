from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import hashlib
from solana.rpc.api import Client
from solders.keypair import Keypair
import openfoodfacts
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage for demo purposes
# In production, use a proper database
submissions = []

@app.route('/api/proof', methods=['POST'])
def receive_proof():
    try:
        if 'barcode_id' not in request.form or 'image' not in request.files:
            return jsonify({'error': 'Missing barcode_id or image'}), 400

        barcode_id = request.form['barcode_id']
        image_file = request.files['image']
        image_data = image_file.read()
        image_hash = hashlib.sha256(image_data).hexdigest()

        print("✅ Received barcode:", barcode_id)
        print("🔐 Image hash:", image_hash)

        return jsonify({
            'status': 'success',
            'message': 'Proof received',
            'barcode': barcode_id,
            'image_hash': image_hash
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)