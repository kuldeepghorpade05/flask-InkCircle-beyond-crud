from flask import Flask, jsonify
from flask_restx import Api
from src.config import config
from src.extensions import jwt, mail

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    jwt.init_app(app)
    mail.init_app(app)
    
    # Initialize MongoDB
    from src.db.models import init_db
    init_db(app)
    
    # =========================
    # Root Route - Hello Message
    # =========================
    @app.route('/')
    def hello():
        return jsonify({
            "message": "Hello from Kuldeep Ghorpade - flask-InkCircle-beyond-crud",
            "version": "1.0.0",
            "documentation": "/docs",
            "endpoints": {
                "auth": "/api/v1/auth",
                "books": "/api/v1/books",
                "reviews": "/api/v1/reviews",
                "tags": "/api/v1/tags"
            }
        })
    
    # Create API
    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Add a JWT token as: Bearer <token>'
        }
    }
    
    api = Api(
    app, 
    doc='/docs', 
    title='InkCircle API | Kuldeep Ghorpade',
    version='1.0',
    authorizations=authorizations,
    security='Bearer Auth'
    )
    
    # imported namespaces
    from src.auth.routes import auth_ns
    from src.books.routes import books_ns
    from src.reviews.routes import reviews_ns
    from src.tags.routes import tags_ns 
    
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(books_ns, path='/api/v1/books')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(tags_ns, path='/api/v1/tags') 
    
    # Register error handlers
    from src.errors import register_error_handlers
    register_error_handlers(app)
    
    print("✅ Flask app initialized successfully")
    return app