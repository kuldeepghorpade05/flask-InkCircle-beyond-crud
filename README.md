# Flask InkCircle Backend

## 📚 Project Overview
Flask InkCircle is a comprehensive book review API built with Flask that allows users to manage books, submit reviews, and interact with a reading community. The application features JWT authentication, RESTful APIs, background task processing, and MongoDB integration.

## 🚀 Technologies Used

### Backend Framework
- **Flask 2.3.3** - Web framework
- **Flask-RESTX 1.3.2** - API framework with Swagger documentation
- **Flask-JWT-Extended 4.7.1** - JWT authentication

### Database & Caching
- **MongoDB Atlas** - Cloud database (via PyMongo 4.15.3)
- **Redis 5.3.1** - Caching and Celery broker

### Authentication & Security
- **bcrypt 4.0.1** - Password hashing
- **python-jose 3.5.0** - JWT token handling
- **passlib 1.7.4** - Password policy enforcement
- **itsdangerous 2.2.0** - Security-related utilities

### Task Queue & Background Jobs
- **Celery 5.5.3** - Distributed task queue
- **Redis** - Message broker for Celery

### Email & Notifications
- **flask-mail 0.9.1** - Email sending capabilities

### Data Validation & Serialization
- **marshmallow 3.26.1** - Object serialization/deserialization

### Environment & Configuration
- **python-dotenv 1.2.1** - Environment variable management

### Package Management
- **Poetry** - Dependency management and packaging

## 📁 Project Structure

```
flask-InkCircle-beyond-crud/
├── src/                         # Source code
│   ├── app.py                  # Main Flask application
│   ├── __init__.py             # Package initialization
│   ├── config.py               # Configuration settings
│   ├── extensions.py           # Flask extensions initialization
│   ├── errors.py               # Error handlers
│   ├── db/                     # Database layer
│   │   ├── __init__.py
│   │   ├── models.py           # MongoDB models
│   │   └── __pycache__/
│   ├── auth/                   # Authentication module
│   │   ├── __init__.py
│   │   ├── routes.py           # Auth endpoints
│   │   ├── schemas.py          # Auth schemas
│   │   ├── service.py          # Auth business logic
│   │   ├── dependencies.py     # Auth dependencies
│   │   ├── utils.py            # Auth utilities
│   │   └── __pycache__/
│   ├── books/                  # Books module
│   │   ├── __init__.py
│   │   ├── routes.py           # Book endpoints
│   │   ├── schemas.py          # Book schemas
│   │   ├── service.py          # Book business logic
│   │   └── __pycache__/
│   ├── reviews/                # Reviews module
│   │   ├── __init__.py
│   │   ├── routes.py           # Review endpoints
│   │   ├── schemas.py          # Review schemas
│   │   ├── service.py          # Review business logic
│   │   └── __pycache__/
│   ├── tags/                   # Tags/Categories module
│   │   ├── __init__.py
│   │   ├── routes.py           # Tag endpoints
│   │   ├── schemas.py          # Tag schemas
│   │   ├── service.py          # Tag business logic
│   │   └── __pycache__/
│   └── __pycache__/
├── celery_tasks.py             # Celery tasks configuration
├── run.py                      # Application entry point
├── notes/                      # Development notes
│   ├── authpy.txt
│   ├── bookspy.txt
│   ├── cms.txt
│   └── note1.txt
├── pyproject.toml              # Poetry configuration
├── poetry.lock                 # Dependency lock file
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## 🔌 API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/api/auth/register` | User registration | Public |
| POST | `/api/auth/login` | User login | Public |
| POST | `/api/auth/logout` | User logout | Required |
| POST | `/api/auth/refresh` | Refresh JWT token | Required |
| POST | `/api/auth/forgot-password` | Request password reset | Public |
| POST | `/api/auth/reset-password` | Reset password | Public |

### User Management Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/api/users/profile` | Get user profile | Required |
| PUT | `/api/users/profile` | Update user profile | Required |
| GET | `/api/users/reviews` | Get user's reviews | Required |
| GET | `/api/users/books` | Get user's books | Required |

### Book Management Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/api/books` | Get all books (with pagination) | Optional |
| POST | `/api/books` | Create new book | Required |
| GET | `/api/books/<book_id>` | Get book details | Optional |
| PUT | `/api/books/<book_id>` | Update book | Required (Owner/Admin) |
| DELETE | `/api/books/<book_id>` | Delete book | Required (Owner/Admin) |
| GET | `/api/books/search` | Search books | Optional |
| GET | `/api/books/categories` | Get book categories | Optional |

### Review Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/api/books/<book_id>/reviews` | Add review to book | Required |
| GET | `/api/books/<book_id>/reviews` | Get book reviews | Optional |
| PUT | `/api/reviews/<review_id>` | Update review | Required (Owner) |
| DELETE | `/api/reviews/<review_id>` | Delete review | Required (Owner/Admin) |
| POST | `/api/reviews/<review_id>/like` | Like/unlike review | Required |
| GET | `/api/reviews/trending` | Get trending reviews | Optional |

### Tag Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/api/tags` | Get all tags | Optional |
| POST | `/api/tags` | Create new tag | Required (Admin) |
| GET | `/api/tags/<tag_id>/books` | Get books by tag | Optional |

## 🛠️ Setup and Installation

### Prerequisites
- Python 3.9+
- MongoDB Atlas account
- Redis server
- Poetry (for dependency management)

### Installation Steps

1. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   # or on Windows
   pip install poetry
   ```

2. **Clone and setup project**
   ```bash
   git clone <repository-url>
   cd flask-InkCircle-beyond-crud
   
   # Install dependencies using Poetry
   poetry install
   
   # Activate virtual environment
   poetry shell
   ```

3. **Environment configuration**
   ```bash
   # Create .env file from template
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Configure MongoDB Atlas**
   - Create a MongoDB Atlas account at https://www.mongodb.com/atlas
   - Create a new cluster
   - Get your connection string
   - Add IP to whitelist
   - Create database user

5. **Run the application**
   ```bash
   # Development server
   poetry run python run.py
   
   # Start Celery worker (in separate terminal)
   poetry run celery -A celery_tasks worker --loglevel=info
   ```

## ⚙️ Configuration

### Environment Variables for MongoDB Atlas
```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key

# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://username:password@cluster-name.mongodb.net/inkcircle?retryWrites=true&w=majority
MONGODB_DB_NAME=inkcircle

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES=86400  # 24 hours

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Key Files Description

- **`src/app.py`**: Main Flask application factory
- **`src/config.py`**: Configuration classes for different environments
- **`src/extensions.py`**: Flask extensions initialization (JWT, Mongo, etc.)
- **`src/errors.py`**: Custom error handlers
- **`src/db/models.py`**: MongoDB models and schemas
- **`celery_tasks.py`**: Celery configuration and task definitions
- **`run.py`**: Application entry point

### Poetry Commands Reference
```bash
# Add new dependency
poetry add package-name

# Add development dependency
poetry add --dev package-name

# Update dependencies
poetry update

# Show dependency tree
poetry show --tree

# Export to requirements.txt
poetry export -f requirements.txt --output requirements.txt

# Run script within poetry environment
poetry run python run.py
```

## 🚀 Deployment with MongoDB Atlas

### MongoDB Atlas Setup
1. **Create Cluster**: Go to MongoDB Atlas → Create new cluster
2. **Network Access**: Add your IP address to whitelist (0.0.0.0/0 for all IPs in development)
3. **Database Access**: Create database user with read/write permissions
4. **Connection String**: Get your connection string from "Connect" button

### Production Deployment Steps
1. **Set up Redis** (if not using cloud Redis)
2. **Configure environment variables** on your server
3. **Use production WSGI server** (Gunicorn, uWSGI)
4. **Set up reverse proxy** (Nginx, Apache)
5. **Configure SSL/TLS certificates**
6. **Set up process manager** (systemd, supervisor)

## 📊 API Documentation

Once running, access the interactive API documentation at:
```
http://localhost:8000/
```

The Swagger UI provides complete endpoint documentation with the ability to test APIs directly from the browser.

## 🔒 Security Features

- JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- CORS configuration
- Input validation with Marshmallow
- Rate limiting capabilities
- Secure headers configuration

## 📈 Performance Features

- Redis caching for frequent queries
- Celery background tasks for heavy operations
- MongoDB indexing for optimal queries
- Pagination for large datasets
- Async email sending

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

