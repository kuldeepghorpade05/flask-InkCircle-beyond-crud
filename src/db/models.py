from pymongo import MongoClient, ASCENDING, DESCENDING
from flask import current_app

client = None
db = None

def init_db(app):
    global client, db
    client = MongoClient(app.config['MONGODB_URI'])
    db = client[app.config['MONGODB_DB']]
    
    # Create indexes
    db.users.create_index('email', unique=True)
    db.users.create_index('username', unique=True)
    
    print("✅ MongoDB connected and indexes created")

def get_db():
    return db

def get_collection(collection_name):
    return db[collection_name]