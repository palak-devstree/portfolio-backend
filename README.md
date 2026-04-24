# Portfolio Backend System

FastAPI-based backend service for AI Backend Engineer portfolio website, built entirely on free-tier cloud services.

## Architecture

- **Framework**: FastAPI 0.104+
- **Database**: Neon PostgreSQL (serverless, 0.5GB free)
- **Cache**: Upstash Redis (10k commands/day free)
- **AI**: Google Gemini API (1500 req/day free) with rule-based fallback
- **Hosting**: Render (free tier) or Railway ($5/mo credit)
- **Background Jobs**: GitHub Actions cron workflows

## Features

- RESTful APIs for projects, blog posts, system designs, lab experiments
- AI-powered chatbot with hybrid approach (rule-based + Gemini)
- Analytics tracking with IP anonymization
- JWT authentication for admin endpoints
- Redis caching with command-budget awareness
- GitHub project synchronization via cron
- Health check endpoint for keep-alive

## Project Structure

```
backend/
├── app/
│   ├── core/           # Configuration, auth, middleware, logging
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic validation schemas
│   ├── routers/        # API endpoint routers
│   ├── services/       # Business logic services
│   └── main.py         # FastAPI application entry point
├── alembic/            # Database migrations
├── tests/              # Test suite
├── docker-compose.yml  # Local development environment
├── Dockerfile          # Container image
├── .env.example        # Environment variables template
└── pyproject.toml      # Dependencies and configuration
```

## Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for local development)
- Poetry (optional, for dependency management)

### Local Development

1. **Clone and navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` with your credentials**:
   - Database URL (Neon PostgreSQL)
   - Redis URL (Upstash)
   - Secret keys
   - API keys (GitHub, Gemini/OpenAI, Cloudinary)

4. **Start services with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - OpenAPI docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Without Docker

1. **Install dependencies**:
   ```bash
   poetry install
   # or
   pip install -r requirements.txt
   ```

2. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

3. **Start the server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Testing

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_health.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=app --cov-report=html
```

## Deployment

### Render (Free Tier)

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy using `render.yaml` blueprint

### Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Set environment variables
4. Deploy using `railway.toml` configuration

### GitHub Actions Workflows

Three cron workflows are included:

- **sync-github.yml**: Syncs GitHub repositories hourly
- **aggregate-analytics.yml**: Aggregates analytics daily at midnight UTC
- **cleanup.yml**: Cleans up old logs weekly on Sunday at 2am UTC

Set these secrets in your GitHub repository:
- `API_BASE_URL`: Your deployed API URL
- `INTERNAL_SYNC_TOKEN`: Token for internal endpoints

## API Endpoints

### Public Endpoints

- `GET /health` - Health check
- `GET /api/v1/dashboard` - Dashboard statistics
- `GET /api/v1/projects` - List projects (paginated)
- `GET /api/v1/projects/{id}` - Get project by ID
- `GET /api/v1/blog` - List blog posts (paginated)
- `GET /api/v1/blog/{slug}` - Get blog post by slug
- `GET /api/v1/system-designs` - List system designs
- `GET /api/v1/system-designs/{id}` - Get system design by ID
- `GET /api/v1/lab` - List lab experiments
- `GET /api/v1/lab/{id}` - Get lab experiment by ID
- `POST /api/v1/chatbot/query` - Query AI chatbot

### Admin Endpoints (JWT Required)

- `POST /api/v1/auth/login` - Admin login
- `POST /api/v1/projects` - Create project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project
- (Similar CRUD for blog, system-designs, lab)
- `POST /api/v1/uploads/diagram` - Upload diagram to Cloudinary

### Internal Endpoints (Token Required)

- `POST /internal/sync/github` - Sync GitHub repositories
- `POST /internal/aggregate` - Aggregate analytics
- `POST /internal/cleanup` - Clean up old data

## Environment Variables

See `.env.example` for all required environment variables.

## Design Patterns

- **Repository Pattern**: DatabaseService abstracts data access
- **Service Layer**: Business logic separated from routes
- **Dependency Injection**: FastAPI's Depends for service injection
- **Factory Pattern**: Configuration and service initialization
- **Strategy Pattern**: Switchable AI providers (Gemini/OpenAI)

## SOLID Principles

- **Single Responsibility**: Each service has one clear purpose
- **Open/Closed**: Extensible via interfaces (e.g., AI providers)
- **Liskov Substitution**: Services implement consistent interfaces
- **Interface Segregation**: Focused service interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

## Free-Tier Constraints

- **Render**: Spins down after 15min idle → UptimeRobot pings every 10min
- **Upstash Redis**: 10k commands/day → Long TTLs, minimal SCAN operations
- **Neon**: 0.5GB storage → Daily aggregation, 90-day retention
- **Gemini API**: 1500 req/day → Rule-based first-pass for simple queries
- **GitHub Actions**: 2000 min/month → ~50 min/day usage

## License

MIT
