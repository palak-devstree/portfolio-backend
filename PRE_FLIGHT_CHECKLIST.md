# 🚀 Pre-Flight Checklist — Local Docker Testing

## ✅ Setup Status

### Files Created (47 total)
- ✅ Core application files (8)
- ✅ Models (6)
- ✅ Schemas (9)
- ✅ Routers (11)
- ✅ Services (5)
- ✅ Tests (9)
- ✅ Docker configuration
- ✅ Database migrations
- ✅ Documentation

### Configuration Files
- ✅ `docker-compose.yml` — PostgreSQL + Redis + API
- ✅ `Dockerfile` — Multi-stage Python build
- ✅ `.env` — Local development config
- ✅ `.env.example` — Template for deployment
- ✅ `pyproject.toml` — Python dependencies
- ✅ `alembic.ini` — Database migrations config

### Documentation
- ✅ `README.md` — Full documentation
- ✅ `QUICKSTART.md` — 5-minute local setup guide
- ✅ `PRE_FLIGHT_CHECKLIST.md` — This file

---

## 🔧 What You Need to Do

### Step 1: Add Your Gemini API Key

Edit `backend/.env` and replace:
```bash
AI_API_KEY=your-gemini-api-key-here
```

With your actual key from https://makersuite.google.com/app/apikey:
```bash
AI_API_KEY=AIzaSy...your-actual-key
```

### Step 2: Start Docker

```bash
cd backend
docker-compose up --build
```

**First build takes 2-3 minutes** (installs Python dependencies).

### Step 3: Wait for Startup

Watch logs until you see:
```
✓ application_ready
```

### Step 4: Test the API

Open http://localhost:8000/docs

Try:
- **GET** `/health` → `{"status": "healthy"}`
- **GET** `/api/v1/dashboard` → Dashboard stats
- **POST** `/api/v1/chatbot/query` → AI chatbot

---

## 🧪 Testing Checklist

### Basic Health Checks
- [ ] `/health` returns 200 OK
- [ ] `/docs` shows Swagger UI
- [ ] `/api/v1/dashboard` returns stats

### Authentication
- [ ] Login with `admin` / `admin123`
- [ ] Receive JWT access token
- [ ] Use token in "Authorize" button

### CRUD Operations (requires auth)
- [ ] Create a project
- [ ] Create a blog post
- [ ] Create a system design
- [ ] List all items
- [ ] Update an item
- [ ] Delete an item

### AI Chatbot
- [ ] Simple query: "What projects do you have?"
- [ ] Complex query: "Explain your system architecture"
- [ ] Check response includes context from database

### Cache Verification
```bash
docker-compose exec redis redis-cli
> KEYS *
> GET dashboard:metrics
```

### Database Verification
```bash
docker-compose exec db psql -U portfolio -d portfolio
> \dt
> SELECT * FROM projects;
```

---

## 🎯 What Works Locally

✅ **Full API functionality**
- All CRUD endpoints
- Authentication & authorization
- AI chatbot with Gemini API
- Dashboard metrics
- File upload endpoints (structure only)

✅ **Database**
- PostgreSQL with async SQLAlchemy
- Automatic migrations on startup
- Sample data creation via API

✅ **Caching**
- Redis for dashboard metrics
- Chatbot response caching
- Graceful degradation if Redis fails

✅ **Logging**
- Structured JSON logs
- Request/response tracking
- Error monitoring

---

## ⚠️ What's NOT Active Locally

❌ **GitHub Sync** — No token configured
- `/api/v1/internal/sync-github` returns empty stats
- Cron jobs won't run (GitHub Actions)

❌ **Cloudinary Uploads** — No credentials configured
- `/api/v1/uploads/*` endpoints will fail
- Everything else works fine

❌ **Production Services** — Using local Docker instead
- Not using Neon PostgreSQL (using local)
- Not using Upstash Redis (using local)
- Not deployed to Render/Railway

---

## 🐛 Troubleshooting

### Port Conflicts
If ports 8000, 5432, or 6379 are in use:

Edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change external port
```

### Database Not Ready
Wait 10-20 seconds after `docker-compose up` for PostgreSQL initialization.

### Migrations Failed
Run manually:
```bash
docker-compose exec api alembic upgrade head
```

### Redis Connection Errors
Check Redis is running:
```bash
docker-compose ps redis
docker-compose logs redis
```

### API Not Starting
Check logs:
```bash
docker-compose logs api
```

Common issues:
- Missing Gemini API key (chatbot will fail)
- Port already in use
- Docker out of memory

### Rebuild from Scratch
```bash
docker-compose down -v
docker-compose up --build
```

---

## 📊 Expected Behavior

### Startup Sequence (30-40 seconds)
1. PostgreSQL starts → health check passes
2. Redis starts → health check passes
3. API starts → installs dependencies
4. Alembic runs migrations
5. Cache warming (dashboard metrics)
6. `application_ready` logged
7. API listening on port 8000

### First Request
- Dashboard cache is pre-warmed
- Response time: ~50-100ms
- Subsequent requests: ~10-20ms (cached)

### Chatbot Behavior
- Simple queries: Rule-based (instant, zero cost)
- Complex queries: Gemini API (1-2 seconds, uses API quota)
- Responses cached for 1 hour

### Database
- Auto-creates tables on first run
- Persists data in Docker volume
- Survives container restarts

---

## 🚀 Next Steps After Local Testing

### 1. Deploy to Render (Free Tier)
- Create Render account
- Connect GitHub repo
- Use `render.yaml` blueprint
- Set environment variables

### 2. Set Up Cloud Services
- **Neon PostgreSQL**: 0.5GB free
- **Upstash Redis**: 10k commands/day free
- **GitHub Token**: For project sync

### 3. Configure GitHub Actions
- Add secrets: `INTERNAL_SYNC_TOKEN`, `API_BASE_URL`
- Enable cron workflows (sync, aggregate, cleanup)

### 4. Set Up Monitoring
- **UptimeRobot**: Ping `/health` every 10min
- **Render Logs**: Monitor errors
- **Upstash Console**: Track Redis usage

### 5. Frontend Integration
- Update `CORS_ORIGINS` in `.env`
- Point frontend to `http://localhost:8000`
- Test all API calls from UI

---

## 📝 Quick Reference

### Useful Commands

**Start everything:**
```bash
docker-compose up --build
```

**Stop everything:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f api
```

**Run tests:**
```bash
docker-compose exec api pytest
```

**Access database:**
```bash
docker-compose exec db psql -U portfolio -d portfolio
```

**Access Redis:**
```bash
docker-compose exec redis redis-cli
```

**Rebuild from scratch:**
```bash
docker-compose down -v && docker-compose up --build
```

### API Endpoints

**Public:**
- `GET /health`
- `GET /api/v1/dashboard`
- `GET /api/v1/projects`
- `GET /api/v1/blog`
- `GET /api/v1/system-designs`
- `GET /api/v1/lab`
- `POST /api/v1/chatbot/query`

**Authenticated (requires JWT):**
- `POST /api/v1/projects`
- `PUT /api/v1/projects/{id}`
- `DELETE /api/v1/projects/{id}`
- `POST /api/v1/blog`
- `PUT /api/v1/blog/{id}`
- `DELETE /api/v1/blog/{id}`
- (Same for system-designs, lab)

**Internal (requires INTERNAL_SYNC_TOKEN):**
- `POST /api/v1/internal/sync-github`
- `POST /api/v1/internal/aggregate-analytics`
- `POST /api/v1/internal/cleanup-old-data`

### Default Credentials

**Admin Login:**
- Username: `admin`
- Password: `admin123`

**Database:**
- Host: `localhost:5432`
- User: `portfolio`
- Password: `portfolio`
- Database: `portfolio`

**Redis:**
- Host: `localhost:6379`
- No password

---

## ✨ Architecture Highlights

### Design Patterns
- **Repository Pattern**: `DatabaseService` abstracts SQLAlchemy
- **Service Layer**: Business logic in `services/`
- **Factory Pattern**: `create_app()` in `main.py`
- **Strategy Pattern**: Switchable AI providers (Gemini/OpenAI)
- **Dependency Injection**: FastAPI's `Depends()`

### SOLID Principles
- **Single Responsibility**: Each service has one purpose
- **Open/Closed**: Extensible via interfaces (AI providers)
- **Liskov Substitution**: AI providers are interchangeable
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Depend on abstractions (DatabaseService)

### Free-Tier Optimizations
- **Stable Cache Keys**: `hashlib.md5` for consistent hashing
- **Atomic Redis Ops**: `SETEX` (1 cmd) vs `SET+EXPIRE` (2 cmds)
- **Rule-Based Chatbot**: First-pass classification (zero cost)
- **No SystemLog Model**: Client-side JS logging only
- **Graceful Degradation**: Works without Redis/GitHub

---

## 🎉 You're Ready!

Everything is set up. Just add your Gemini API key and run:

```bash
cd backend
docker-compose up --build
```

Then open http://localhost:8000/docs and start testing!

See `QUICKSTART.md` for detailed testing instructions.
