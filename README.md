# FastAPI Realtime Tasks

This is a FastAPI-based web application that provides real-time task management capabilities with WebSocket support and MongoDB as the database. The application includes user authentication, task management, and real-time updates through WebSockets.

## Features

- User authentication (registration and login)
- JWT-based security
- Real-time task updates via WebSockets
- Asynchronous MongoDB operations using Motor
- Celery for background task processing
- Docker and Docker Compose support
- RESTful API endpoints

## Technology Stack

- FastAPI
- Python 3.13.3
- MongoDB 7.0
- Motor (Async MongoDB driver)
- Celery (Background task processing)
- Redis (Message broker and result backend)
- WebSockets
- Docker
- Poetry (dependency management)

## Folder Structure

```
fastapi-realtime-tasks/
├── app/
│   ├── auth/           # Authentication routes, schemas and services
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── celery_task/    # Celery tasks
│   │   └── task.py
│   ├── core/           # Core configurations, dependencies and security
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── security.py
│   ├── database/       # Database configurations and models
│   │   ├── asyncdb/
│   │   │   ├── collections.py
│   │   │   ├── core.py
│   │   │   ├── models.py
│   │   │   └── mongo_handler.py
│   │   └── constant.py
│   ├── tasks/          # Task-related routes, schemas and services
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── websockets/     # WebSocket manager and router
│   │   ├── manager.py
│   │   └── router.py
│   ├── worker/         # Celery worker configuration
│   │   └── celer_worker.py
│   └── main.py         # Application entry point
├── .env               # Environment variables
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── pyproject.toml     # Project dependencies
└── README.md
```

## MongoDB Connection

The application uses Motor, an asynchronous MongoDB driver for Python, to connect to MongoDB. Here's how the connection is established:

1. **Configuration**: The MongoDB URI is configured in the `.env` file as `MONGO_URI`
2. **Connection Setup**: In `app/database/asyncdb/core.py`, an `AsyncIOMotorClient` is created using the configured URI
3. **Database Access**: The application accesses the default database through this client
4. **Collection Access**: Specific collections are accessed through the `app/database/asyncdb/collections.py` module
5. **Models**: The `app/database/asyncdb/models.py` file defines model classes that inherit from `MongoDbHandler` to interact with specific collections

### Connection Code Flow

1. `app/core/config.py` reads the `MONGO_URI` from environment variables
2. `app/database/asyncdb/core.py` creates a global `AsyncIOMotorClient` instance
3. Collections are defined in `app/database/asyncdb/collections.py`
4. Model classes in `app/database/asyncdb/models.py` provide structured access to collections
5. The `MongoDbHandler` class in `app/database/asyncdb/mongo_handler.py` provides common database operations


## Running the Application

### Using Docker (Recommended)

1. Make sure Docker and Docker Compose are installed
2. Create a `.env` file with the required environment variables
3. Run the application:

```bash
docker-compose up --build
```

This will start the following services:
- FastAPI application on port 8000
- MongoDB on port 27018 (for local access)
- Redis on port 6380 (for Celery)
- Celery worker for background tasks

### Without Docker

1. Run like this ```poetry run uvicorn app.main:app```

The application will be available at `http://localhost:8000`

### Development

The application exposes MongoDB on port 27018 and Redis on port 6380 for local access (in addition to the internal container network).

## API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user details (authentication required)
- `GET/POST/PUT/DELETE /tasks/` - Task management (authentication required)
- `GET /websocket` - WebSocket endpoint for real-time updates

## Database Collections

- `Users` - Stores user information (email, password hash, name, role)
- `Tasks` - Stores task information

## Background Task Processing

The application includes Celery for handling background tasks:

- `app/celery_task/task.py` - Contains background task definitions
- `app/worker/celer_worker.py` - Celery worker configuration
- Uses Redis as both the message broker and result backend

To run the Celery worker:

```bash
poetry run celery -A app.worker.celer_worker worker --loglevel=info -Q default_queue
```

## Environment Variables for Celery

Add these variables to your `.env` file for Celery configuration:

```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

