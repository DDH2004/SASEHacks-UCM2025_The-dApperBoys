from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['green_rewards_db']

# Collections
wallets_collection = db['wallets']
submissions_collection = db['submissions']
points_collection = db['points']

# Create index for wallet lookup
points_collection.create_index('wallet_address', unique=True)