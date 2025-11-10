from flask import Flask
from flask_restx import Api
from src.config import config
from src.extensions import jwt, mail

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # DEBUG: Check what MongoDB URI is being used
    print(f"🔧 Config MONGODB_URI: {app.config.get('MONGODB_URI')}")
    
    # Initialize extensions
    jwt.init_app(app)
    mail.init_app(app)
    
    # Initialize MongoDB
    from src.db.models import init_db
    init_db(app)
    
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
        title='InkCircle API', 
        description='A book review API with Flask and MongoDB',
        authorizations=authorizations,
        security='Bearer Auth'
    )
    
    # Add namespaces
    from src.auth.routes import auth_ns
    api.add_namespace(auth_ns, path='/api/v1/auth')
    
    # Register error handlers
    from src.errors import register_error_handlers
    register_error_handlers(app)
    
    print("✅ Flask app initialized successfully")
    return app