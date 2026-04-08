# Comments SPA

A single-page application for nested comments with JWT authentication, real-time WebSocket updates, and file attachment support.

## Tech Stack

**Backend**
- Python 3.13, Django 5.2, Django REST Framework
- PostgreSQL 16, Redis 7
- Celery 5 (task queue)
- Django Channels + channels-redis (WebSocket)
- JWT authentication (djangorestframework-simplejwt)
- CAPTCHA (django-simple-captcha)
- Gunicorn + Uvicorn (ASGI)

**Frontend**
- Vue 3 (Composition API)
- Vue Router 5, Pinia
- Vite 8, Sass
- Axios

**Infrastructure**
- Docker, Docker Compose
- Nginx (reverse proxy + static files)

## Features

- Nested (threaded) comments
- Top-level comments displayed as a sortable table (by Username, E-mail, date)
- Pagination — 25 comments per page (LIFO)
- XSS protection: allowed HTML tags `<a>`, `<code>`, `<i>`, `<strong>`
- File attachments: images JPG/GIF/PNG (max 320×240), text files TXT (max 100 KB)
- Message preview without page reload
- WebSocket — new comments appear in real time
- Lightbox for viewing attachments
- CAPTCHA on comment submission
- JWT authentication (access 60 min, refresh 7 days)

## Getting Started

### Requirements

- Docker and Docker Compose
- Make

### Environment Variables

Copy the templates and fill in the values:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Example `backend/.env`:

```env
# Django
DEBUG=False
SECRET_KEY=your-secret-key
CSRF_TRUSTED_ORIGINS=http://localhost
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SERVER_PORT=8000
NGINX_PORT=80
PAGE_SIZE=25

# PostgreSQL
DB_NAME=comments
DB_USER=postgres
DB_HOST=comments-spa-postgres
DB_PASS=your-db-password
DB_PORT=5432
DB_LOCAL_PORT=5433

# Redis
REDIS_HOST=comments-spa-redis
REDIS_PASS=your-redis-password
REDIS_PORT=6379
REDIS_LOCAL_PORT=6380
REDIS_CACHE_DB=1

# Celery
CELERY_BROKER_DB=0
```

Example `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/comments/
```

### Run (production)

```bash
make up-prod
```

### Run (dev)

```bash
make up-dev
```

> Dev mode uses `backend/.env.dev` and runs the project as a separate Docker project `comments-spa-dev`.

### Stop

```bash
# prod
make down-prod

# dev
make down-dev
```

### Logs

```bash
make logs-prod
make logs-dev
```

## Docker Services

| Service | Description |
|---|---|
| `comments-spa-postgres` | PostgreSQL 16 database |
| `comments-spa-redis` | Redis 7 (cache, Channels, Celery broker) |
| `comments-spa-backend` | Django ASGI app (Gunicorn + Uvicorn) |
| `comments-spa-worker` | Celery worker |
| `comments-spa-frontend` | Vue 3 (static build) |
| `comments-spa-nginx` | Nginx (reverse proxy, static and frontend serving) |

## Project Structure

```
comments-spa/
├── backend/
│   ├── comments/       # Comments app
│   ├── users/          # Custom user model
│   ├── config/         # Django settings, ASGI, Celery, routing
│   ├── .env.example    # Environment variables template
│   └── entrypoint.sh   # Migrations, collectstatic, server start
├── frontend/
│   └── src/
│       ├── components/ # CommentForm, CommentItem, CommentList, AppHeader
│       └── views/      # HomeView, LoginView, RegisterView
├── deploy/
│   ├── docker-compose.yaml
│   └── nginx/
└── Makefile
```

## API Docs

Available after startup:

- Swagger UI: `http://localhost/api/schema/swagger-ui/`
- ReDoc: `http://localhost/api/schema/redoc/`

## Database Schema

The database schema file (MySQL Workbench compatible) is located in the repository root: [db_schema.mwb](db_schema.mwb)