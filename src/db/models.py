from pymongo import MongoClient, ASCENDING, DESCENDING
from flask import current_app

client = None
db = None

def init_db(app):
    global client, db
    client = MongoClient(app.config['MONGODB_URI'])
    db = client[app.config['MONGODB_DB']]
    
    # Create indexes for users
    db.users.create_index('email', unique=True)
    db.users.create_index('username', unique=True)
    
    # Create indexes for books
    db.books.create_index('title')
    db.books.create_index('author')
    db.books.create_index([('user_uid', ASCENDING), ('created_at', DESCENDING)])
    
    # Create indexes for reviews
    db.reviews.create_index([('book_uid', ASCENDING), ('created_at', DESCENDING)])
    db.reviews.create_index([('user_uid', ASCENDING), ('book_uid', ASCENDING)], unique=True)
    db.reviews.create_index('user_uid')
    db.reviews.create_index('book_uid')
    
    # Create indexes for tags
    db.tags.create_index('name', unique=True)
    db.book_tags.create_index([('book_uid', ASCENDING), ('tag_uid', ASCENDING)], unique=True)
    db.book_tags.create_index('book_uid')
    db.book_tags.create_index('tag_uid')
    
    print("✅ MongoDB connected and indexes created")

def get_db():
    return db

def get_collection(collection_name):
    return db[collection_name]