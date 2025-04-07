# GreenProof - Blockchain Rewards for Sustainable Actions
GreenProof is a blockchain-powered platform that incentivizes and verifies recycling activities. By scanning product barcodes and submitting proof of recycling, users earn points that can be converted to GreenTokens on the Solana blockchain.
## Features
- **Barcode Verification**: Scan product barcodes to verify recyclability and material composition
- **Points System**: Earn points based on environmental impact of recycled items
- **Blockchain Integration**: Convert points to tokens on the Solana blockchain
User Dashboard: Track contributions, points, and token balance. <br>

## Technologies Used
- **Frontend**: React, TypeScript, Tailwind CSS
- **Backend**: Python Flask
- **Database**: MongoDB
- **Blockchain**: Solana
- **Visualization**: Three.js, WebGL
- **API**: Open Food Facts

## Installation
Prerequisites:
- Node.js (v16+)
- Python (v3.8+)
- MongoDB
- Phantom Wallet

Frontend Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/GreenProof.git
cd GreenProof

# Install dependencies
npm install
```
Backend Setup
```bash
# Install Python dependencies
cd backend
`pip install -r requirements.txt`

### Configure environment variables (if needed)
cp .env.example .env
# Edit .env with your configuration
```
## Running the Application
Start MongoDB (if running locally)
```bash
# Using Docker
docker run -d --name mongodb -p 27017:27017 -v ~/mongodb/data:/data/db mongo:latest
```
Start the Backend
```bash
cd backend
flask run
# Or using Python directly
python serverVoting.py
```
Start the Frontend
```bash
# In the project root
npm start
```
## Connecting Your Wallet
1. Download and install Phantom Wallet
2. Create or import a wallet
3. Connect your wallet to the application when prompted
## Usage
1. **Sign in**: Connect your Phantom wallet
2. **Scan products**: Use the barcode scanner to verify recyclability
3. **Submit proof**: Take a photo of the item being recycled
4. **Earn points**: Points are awarded based on product eco-score
5. **Convert to tokens**: Exchange points for GreenTokens
6. **Track progress**: Monitor your environmental impact on the dashboard
## Project Structure
```
GreenProof/
├── src/                # Frontend source code
│   ├── components/     # React components
│   ├── pages/          # Page components
│   └── assets/         # Static assets
├── backend/            # Python backend
│   ├── serverVoting.py # Main server file
│   └── walletGenMongo.py # Wallet generation utilities
└── public/             # Public assets
```
## Team
GreenProof was created by The dApperBoys team during the SASE Hackathon at UC Merced 2025.
## Acknowledgments
- Open Food Facts API for product data
- Solana Foundation for blockchain infrastructure
- Three.js for visualization capabilities