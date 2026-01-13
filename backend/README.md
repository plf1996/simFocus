# simFocus Backend

AI-powered virtual focus group platform backend service.

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Python**: 3.11+
- **Database**: PostgreSQL 16 with SQLAlchemy 2.0 (async)
- **Authentication**: JWT (python-jose)
- **Security**: bcrypt password hashing, AES-256 encryption
- **API Docs**: Swagger UI & ReDoc

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API route handlers
│   ├── core/            # Security, exceptions, constants
│   ├── db/              # Database session and base models
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic layer
│   ├── utils/           # Utility functions
│   ├── config.py        # Application configuration
│   └── main.py          # FastAPI application entry point
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Quick Start

### Using Docker Compose (Recommended)

1. **Copy environment file:**
   ```bash
   cp backend/.env.example backend/.env
   ```

2. **Configure secrets in .env:**
   ```bash
   # Generate secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"

   # Generate encryption key
   python -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

4. **Check health:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

### Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL:**
   ```bash
   # Using Docker
   docker run -d \
     --name simfocus-postgres \
     -e POSTGRES_DB=simfocus \
     -e POSTGRES_USER=simfocus \
     -e POSTGRES_PASSWORD=simfocus_password \
     -p 5432:5432 \
     postgres:16-alpine
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Configuration

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Environment (development/testing/production) | `development` |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `SECRET_KEY` | JWT signing secret | - |
| `ENCRYPTION_KEY` | AES-256 encryption key (base64) | - |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |
| `ANTHROPIC_API_KEY` | Anthropic API key (optional) | - |

## Development

### Code Style

- Follow PEP 8 guidelines
- Use `black` for formatting
- Use `ruff` for linting

### Running Tests

```bash
pytest tests/
```

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Docker Production Build

```bash
# Build image
docker build -t simfocus-backend:latest backend/

# Run container
docker run -d \
  --name simfocus-backend \
  -p 8000:8000 \
  --env-file backend/.env \
  simfocus-backend:latest
```

## Security Notes

- All API keys are encrypted using AES-256 before storage
- Passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes (access) or 7 days (refresh)
- CORS is configured for specific origins
- Rate limiting is enabled by default

## License

[Your License Here]
