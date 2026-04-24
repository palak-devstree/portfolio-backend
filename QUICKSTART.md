# Quick Start — Local Docker Development

## Prerequisites
- Docker and Docker Compose installed
- Your Gemini API key from https://makersuite.google.com/app/apikey

## Setup (5 minutes)

### 1. Add your Gemini API key

Edit `backend/.env` and replace this line:
```bash
AI_API_KEY=your-gemini-api-key-here
```

With your actual key:
```bash
AI_API_KEY=AIzaSy...your-actual-key
```

### 2. Start everything

```bash
cd backend
docker-compose up --build
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI API (port 8000)

### 3. Wait for startup

Watch the logs until you see:
```
application_ready
```

### 4. Test the API

Open http://localhost:8000/docs in your browser — you'll see the interactive API documentation.

Try these endpoints:
- **GET** `/health` — should return `{"status": "healthy"}`
- **GET** `/api/v1/dashboard` — returns dashboard stats
- **POST** `/api/v1/chatbot/query` — test the AI chatbot

### 5. Login as admin

In the Swagger UI at http://localhost:8000/docs:

1. Click **POST** `/api/v1/auth/login`
2. Click "Try it out"
3. Use credentials:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
4. Copy the `access_token` from the response
5. Click the "Authorize" button at the top
6. Paste: `Bearer <your-token-here>`
7. Now you can test admin endpoints (create/update/delete)

## Test the Chatbot

**POST** `/api/v1/chatbot/query`:
```json
{
  "query": "Tell me about your projects",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

The chatbot will:
- Use rule-based classification for simple queries (zero cost)
- Call Gemini API for complex queries (uses your API key)

## Create Sample Data

Use the Swagger UI to create test data:

### Create a Project
**POST** `/api/v1/projects` (requires auth):
```json
{
  "name": "Portfolio Backend",
  "description": "FastAPI backend built on free-tier cloud services with AI chatbot",
  "stack": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
  "status": "done",
  "github_url": "https://github.com/yourusername/portfolio-backend",
  "featured": true,
  "display_order": 1
}
```

### Create a Blog Post
**POST** `/api/v1/blog` (requires auth):
```json
{
  "title": "Building a Zero-Cost Portfolio Backend",
  "slug": "building-zero-cost-portfolio-backend",
  "content": "# Introduction\n\nThis is a detailed blog post about building a portfolio backend on free-tier services...\n\n## Architecture\n\nThe system uses FastAPI, Neon PostgreSQL, Upstash Redis, and Google Gemini API.",
  "preview": "Learn how to build a production-quality portfolio backend using only free-tier cloud services.",
  "tags": ["backend", "fastapi", "python", "free-tier"],
  "published_date": "2026-01-15T10:00:00Z",
  "read_time_minutes": 8,
  "is_published": true,
  "meta_description": "Build a portfolio backend on free-tier services with FastAPI, PostgreSQL, Redis, and AI."
}
```

### Create a System Design
**POST** `/api/v1/system-designs` (requires auth):
```json
{
  "title": "Scalable API Gateway with Rate Limiting",
  "description": "Design for a high-throughput API gateway with Redis-based rate limiting and JWT authentication",
  "stack": ["FastAPI", "Redis", "PostgreSQL", "Docker", "Nginx"],
  "notes": [
    "Token bucket algorithm for rate limiting",
    "Redis for distributed rate limit counters",
    "JWT with short-lived access tokens",
    "Health check endpoint for load balancer",
    "Graceful degradation when Redis is unavailable"
  ],
  "complexity_level": "intermediate"
}
```

## View the Data

- **GET** `/api/v1/projects` — list all projects
- **GET** `/api/v1/blog` — list published blog posts
- **GET** `/api/v1/system-designs` — list system designs
- **GET** `/api/v1/dashboard` — see aggregated stats

## Database Access

Connect to PostgreSQL directly:
```bash
docker-compose exec db psql -U portfolio -d portfolio
```

View tables:
```sql
\dt
SELECT * FROM projects;
SELECT * FROM blog_posts;
```

## Redis Access

Connect to Redis:
```bash
docker-compose exec redis redis-cli
```

View cached keys:
```
KEYS *
GET dashboard:metrics
```

## Logs

View API logs:
```bash
docker-compose logs -f api
```

View all logs:
```bash
docker-compose logs -f
```

## Stop Everything

```bash
docker-compose down
```

Keep data (volumes persist):
```bash
docker-compose down
```

Delete everything including data:
```bash
docker-compose down -v
```

## Troubleshooting

### Port already in use
If port 8000, 5432, or 6379 is already in use, edit `docker-compose.yml` and change the port mappings:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

### Database connection errors
Wait 10-20 seconds after `docker-compose up` for PostgreSQL to fully initialize.

### Migrations not running
Run manually:
```bash
docker-compose exec api alembic upgrade head
```

### Cache errors
The app degrades gracefully if Redis is unavailable. Check Redis is running:
```bash
docker-compose ps redis
```

## What's NOT needed for local testing

- ❌ Neon PostgreSQL (using local PostgreSQL)
- ❌ Upstash Redis (using local Redis)
- ❌ GitHub token (sync endpoint will return empty stats)
- ❌ Cloudinary (upload endpoint will fail, but everything else works)
- ❌ Render/Railway deployment
- ❌ GitHub Actions workflows

## Next Steps

Once local testing works:
1. Deploy to Render (free tier) using `render.yaml`
2. Set up Neon PostgreSQL (0.5GB free)
3. Set up Upstash Redis (10k commands/day free)
4. Add GitHub token for project sync
5. Configure GitHub Actions secrets for cron jobs
6. Set up UptimeRobot for keep-alive pings

See `README.md` for full deployment instructions.
