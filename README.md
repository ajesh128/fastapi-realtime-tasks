# FastAPI Realtime Tasks

This is a FastAPI-based web application that provides real-time task management capabilities with WebSocket support and MongoDB as the database. The application includes user authentication, task management, and real-time updates through WebSockets.

## Features

- User authentication (registration and login)
- JWT-based security
- Real-time task updates via WebSockets
- Asynchronous MongoDB operations using Motor
- Docker and Docker Compose support
- RESTful API endpoints

## Technology Stack

- FastAPI
- Python 3.13.3
- MongoDB 7.0
- Motor (Async MongoDB driver)
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

### Without Docker

1. Run like this ```poetry run uvicorn app.main:app```

The application will be available at `http://localhost:8000`

### Development

The application exposes MongoDB on port 27017 for local access (in addition to the internal container network).

## API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET/POST/PUT/DELETE /tasks/` - Task management (authentication required)
- `GET /websocket` - WebSocket endpoint for real-time updates

## Database Collections

- `Users` - Stores user information (email, password hash, name, role)
- `Tasks` - Stores task information

