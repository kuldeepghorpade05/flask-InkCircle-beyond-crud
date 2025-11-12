# 📚 Flask InkCircle Backend

## 🌐 Live Deployment

**Production URL:**
🔗 [https://kuldeepghorpade-flask-inkcircle.duckdns.org/](https://kuldeepghorpade-flask-inkcircle.duckdns.org/)
📘 API Docs (Swagger UI):
🔗 [https://kuldeepghorpade-flask-inkcircle.duckdns.org/docs](https://kuldeepghorpade-flask-inkcircle.duckdns.org/docs)

---

## 🧩 Overview

**Flask InkCircle** is a **book review API platform** built using Flask, providing endpoints for managing users, books, tags, and reviews — all secured with JWT authentication.
The backend is **Dockerized**, deployed on an **AWS VM**, served via **Nginx reverse proxy**, and secured with **Certbot SSL certificates** using a **DuckDNS subdomain**.

---

## 🏗️ Tech Stack

### ⚙️ Backend

* **Flask (2.3.3)** — Core web framework
* **Flask-RESTX (1.3.2)** — REST API + Swagger docs
* **Flask-JWT-Extended (4.7.1)** — JWT authentication
* **PyMongo (4.15.3)** — MongoDB driver
* **Celery (5.5.3)** — Async background tasks
* **Redis (5.3.1)** — Cache & Celery broker

### 🔒 Security

* **bcrypt (4.0.1)** — Password hashing
* **python-jose (3.5.0)** — JWT handling
* **passlib (1.7.4)** — Password policies
* **itsdangerous (2.2.0)** — Secure signing
* **CORS** — Cross-origin resource sharing

### 📦 DevOps & Deployment

* **Docker + Docker Compose** — Containerization
* **Nginx** — Reverse proxy and SSL termination
* **Certbot + Let’s Encrypt** — HTTPS certificates
* **DuckDNS** — Free dynamic DNS subdomain
* **AWS VM (Ubuntu)** — Production hosting

### 🧰 Other Tools

* **Poetry** — Dependency management
* **Marshmallow (3.26.1)** — Schema validation
* **Flask-Mail (0.9.1)** — Email notifications
* **python-dotenv (1.2.1)** — Env management

---

## 📁 Updated Project Structure

```
flask-InkCircle-beyond-crud/
├── Dockerfile                  # Docker build configuration
├── docker-compose.yml          # Multi-container setup (Flask + Redis)
├── celery_tasks.py             # Celery worker configuration
├── pyproject.toml              # Poetry dependencies
├── poetry.lock
├── requirements.txt
├── run.py                      # Flask entry point
├── src/
│   ├── app.py                  # Flask application factory
│   ├── config.py               # Configuration settings
│   ├── extensions.py           # Initialize Flask extensions
│   ├── errors.py               # Error handlers
│   ├── db/
│   │   ├── models.py           # MongoDB models
│   │   └── __init__.py
│   ├── auth/
│   │   ├── routes.py           # Auth routes
│   │   ├── service.py          # Auth logic
│   │   ├── schemas.py          # Auth schemas
│   │   ├── utils.py            # JWT helpers
│   │   ├── dependencies.py
│   │   └── __init__.py
│   ├── books/
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── __init__.py
│   ├── reviews/
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── __init__.py
│   ├── tags/
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── __init__.py
│   └── __init__.py
└── __pycache__/
```

---

## 🐳 Docker Setup

### 1️⃣ Build and Start Containers

```bash
docker-compose up -d --build
```

### 2️⃣ Check Running Containers

```bash
docker ps
```

### 3️⃣ Stop Containers

```bash
docker-compose down
```

---

## 🌍 Nginx + Certbot (Reverse Proxy & SSL)

### Nginx configuration snippet:

```nginx
server {
    server_name kuldeepghorpade-flask-inkcircle.duckdns.org;

    location / {
        proxy_pass http://127.0.0.1:8000;
        include proxy_params;
    }

    listen 80;
}
```

### Enable HTTPS:

```bash
sudo certbot --nginx -d kuldeepghorpade-flask-inkcircle.duckdns.org
```

Certbot automatically updates the Nginx config for HTTPS and renews certificates.

---

## 🔌 API Endpoints

Swagger Docs → [https://kuldeepghorpade-flask-inkcircle.duckdns.org/docs](https://kuldeepghorpade-flask-inkcircle.duckdns.org/docs)

| Category | Example Endpoint                        | Auth   |
| -------- | --------------------------------------- | ------ |
| Auth     | `/api/auth/login`, `/api/auth/register` | Public |
| Books    | `/api/books`, `/api/books/<id>`         | JWT    |
| Reviews  | `/api/books/<id>/reviews`               | JWT    |
| Tags     | `/api/tags`                             | Admin  |
| Users    | `/api/users/profile`                    | JWT    |

---

## ⚙️ Environment Variables (`.env`)

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key

MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/inkcircle
MONGODB_DB_NAME=inkcircle

REDIS_URL=redis://redis:6379/0

JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

---

## 🚀 Deployment Summary

* **Server:** AWS EC2 (Ubuntu)
* **Reverse Proxy:** Nginx
* **SSL/TLS:** Certbot (Let’s Encrypt)
* **Containers:** Flask API + Redis
* **DNS:** DuckDNS subdomain
* **Ports:**

  * 443 → HTTPS (Flask via Nginx proxy)
  * 80 → Redirect to HTTPS

---

## 🔒 Security Highlights

* JWT authentication + refresh tokens
* HTTPS enforced with Certbot
* Passwords hashed with bcrypt
* Input validation with Marshmallow
* CORS protection enabled
* Reverse proxy hiding backend port 8000

---

## 📈 Performance Optimizations

* Redis caching for frequent data
* Celery background tasks
* MongoDB indexes
* Pagination for large data
* Async mail delivery

---

## 🤝 Contributing

```bash
git checkout -b feature/new-feature
# Make your changes
git commit -m "Add new feature"
git push origin feature/new-feature
# Submit a PR
```

---

## 🧠 Author

**Kuldeep Ghorpade**
📍 Deployed on AWS
🔗 [https://kuldeepghorpade-flask-inkcircle.duckdns.org](https://kuldeepghorpade-flask-inkcircle.duckdns.org)

