from bson import ObjectId
from datetime import datetime
from src.db.models import get_db

class TagService:
    def __init__(self):
        self.db = get_db()
    
    def get_all_tags(self):
        """Get all tags"""
        try:
            tags = list(self.db.tags.find().sort('created_at', -1))
            return tags
        except Exception as e:
            print(f"Error getting tags: {e}")
            return []
    
    def get_tag(self, tag_uid: str):
        """Get a single tag by ID"""
        try:
            tag = self.db.tags.find_one({'_id': ObjectId(tag_uid)})
            return tag
        except:
            return None
    
    def get_tag_by_name(self, name: str):
        """Get tag by name"""
        try:
            tag = self.db.tags.find_one({'name': name})
            return tag
        except:
            return None
    
    def create_tag(self, tag_data: dict):
        """Create a new tag"""
        try:
            # Check if tag already exists
            existing_tag = self.get_tag_by_name(tag_data['name'])
            if existing_tag:
                return {'error': 'Tag already exists'}, 400
            
            # Create tag document
            tag_doc = {
                'name': tag_data['name'],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.db.tags.insert_one(tag_doc)
            tag_doc['_id'] = result.inserted_id
            
            return tag_doc, 201
            
        except Exception as e:
            return {'error': f'Error creating tag: {str(e)}'}, 500
    
    def add_tags_to_book(self, book_uid: str, tags_data: dict):
        """Add tags to a book"""
        try:
            # Check if book exists
            from src.books.service import BookService
            book_service = BookService()
            book = book_service.get_book(book_uid)
            
            if not book:
                return {'error': 'Book not found'}, 404
            
            tag_ids = []
            
            # Process each tag in the request
            for tag_item in tags_data['tags']:
                tag_name = tag_item['name']
                
                # Find or create tag
                existing_tag = self.get_tag_by_name(tag_name)
                if existing_tag:
                    tag_id = str(existing_tag['_id'])
                else:
                    # Create new tag
                    new_tag, status = self.create_tag({'name': tag_name})
                    if status == 201:
                        tag_id = str(new_tag['_id'])
                    else:
                        continue  # Skip if tag creation failed
                
                tag_ids.append(tag_id)
            
            # Update book with tags (using book_tags collection for many-to-many)
            for tag_id in tag_ids:
                # Check if tag already associated with book
                existing_book_tag = self.db.book_tags.find_one({
                    'book_uid': book_uid,
                    'tag_uid': tag_id
                })
                
                if not existing_book_tag:
                    # Create book-tag relationship
                    book_tag_doc = {
                        'book_uid': book_uid,
                        'tag_uid': tag_id,
                        'created_at': datetime.utcnow()
                    }
                    self.db.book_tags.insert_one(book_tag_doc)
            
            # Return success message
            return {'message': 'Tags added to book successfully'}, 200
            
        except Exception as e:
            return {'error': f'Error adding tags to book: {str(e)}'}, 500
    
    def get_book_tags(self, book_uid: str):
        """Get all tags for a specific book"""
        try:
            # Get book-tag relationships
            book_tags = list(self.db.book_tags.find({'book_uid': book_uid}))
            
            # Get tag details for each relationship
            tags = []
            for book_tag in book_tags:
                tag = self.db.tags.find_one({'_id': ObjectId(book_tag['tag_uid'])})
                if tag:
                    tags.append(tag)
            
            return tags
        except Exception as e:
            print(f"Error getting book tags: {e}")
            return []
    
    def delete_tag(self, tag_uid: str):
        """Delete a tag"""
        try:
            # Check if tag exists
            tag = self.get_tag(tag_uid)
            if not tag:
                return {'error': 'Tag not found'}, 404
            
            # Delete tag from tags collection
            result = self.db.tags.delete_one({'_id': ObjectId(tag_uid)})
            
            # Also delete all book-tag relationships
            self.db.book_tags.delete_many({'tag_uid': tag_uid})
            
            if result.deleted_count > 0:
                return {'message': 'Tag deleted successfully'}, 200
            else:
                return {'error': 'Failed to delete tag'}, 500
                
        except Exception as e:
            return {'error': f'Error deleting tag: {str(e)}'}, 500