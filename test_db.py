from pymongo import MongoClient

# Replace this with your MONGO_URI
MONGO_URI = 'mongodb+srv://acolijn:I_love_mongoDB123!@cluster0.srrelu1.mongodb.net/'


client = MongoClient(MONGO_URI)

# Connect to a specific database, e.g., "testdb"
db = client.testdb

# Attempt to list the collections
try:
    collections = db.list_collection_names()
    print(f"Collections in the database: {collections}")
except Exception as e:
    print(f"An error occurred: {e}")

client.close()
