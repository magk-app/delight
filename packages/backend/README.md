# Delight Backend API

FastAPI backend for the Delight AI companion platform.

## ⚠️ IMPORTANT: Before Starting Development

**If you're testing authentication or user creation, you need ngrok running!**

### Quick Checklist:

- [ ] **Backend running:** `poetry run uvicorn main:app --reload`
- [ ] **ngrok tunnel active:** `ngrok http 8000` (in separate terminal)
- [ ] **Clerk webhook URL updated** to your current ngrok URL
- [ ] **Environment variables set** (`.env` file configured)

**Why?** Clerk webhooks need a public URL to reach your local backend. Without ngrok, users won't be created automatically via webhooks (though lazy user creation will still work).

📖 **Full webhook setup guide:** See `docs/dev/1-3-WEBHOOK-SETUP-GUIDE.md`

## Quick Start

```bash
# Install dependencies
poetry install

# Start development server
poetry run uvicorn main:app --reload
```

**For webhook testing, also start ngrok in a separate terminal:**

```bash
ngrok http 8000
# Copy the HTTPS URL and update Clerk webhook configuration
```

Visit:

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **ngrok Dashboard:** http://localhost:4040 (when ngrok is running)

## Project Structure

```
app/
├── api/v1/         # API routes
│   └── health.py   # Health check endpoint
├── core/           # Configuration and dependencies
├── models/         # SQLAlchemy database models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
├── agents/         # LangGraph AI agents
├── workers/        # ARQ background jobs
└── db/             # Database setup and migrations
```

## Development

### Development Server

The backend uses **hot-reload** for fast iteration during development:

```bash
# Basic reload mode (recommended for most development)
poetry run uvicorn main:app --reload

# Bind to all interfaces (useful for Docker/WSL)
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Debug mode with verbose logging
poetry run uvicorn main:app --reload --log-level debug

# Custom port (if 8000 is already in use)
poetry run uvicorn main:app --reload --port 8001
```

**How Reload Works:**

- Uvicorn watches Python files for changes
- When you save a file, the server automatically restarts
- API stays available during reload (brief interruption)
- No need to manually restart the server

### Code Quality

```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest -v --cov=app --cov-report=html

# Lint code
poetry run ruff check .

# Format code
poetry run black .

# Type check
poetry run mypy .
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

- **INFRA_MODE**: `cloud-dev` or `local`
- **DATABASE_URL**: PostgreSQL connection string
- **REDIS_URL**: Redis connection string
- **CLERK_SECRET_KEY**: Clerk authentication secret
- **CLERK_WEBHOOK_SECRET**: Clerk webhook signature validation
- **CLERK_JWKS_URL**: Clerk JWKS endpoint (see setup below)
- **OPENAI_API_KEY**: OpenAI API key

See `.env.example` for detailed configuration instructions.

### Setting Up CLERK_JWKS_URL (Required)

The `CLERK_JWKS_URL` is **required** for JWT signature verification. Without it, you'll see a 404 error during authentication.

**Step-by-step setup:**

1. **Go to your Clerk Dashboard:** https://dashboard.clerk.com
2. **Navigate to:** Your App → **API Keys** → **Advanced** section
3. **Find the JWKS endpoint** (JSON Web Key Set URL)
4. **Copy the URL** - it should look like:
   ```
   https://[your-instance].clerk.accounts.dev/.well-known/jwks.json
   ```
5. **Add to your `.env` file:**
   ```bash
   CLERK_JWKS_URL=https://your-instance.clerk.accounts.dev/.well-known/jwks.json
   ```
6. **Restart the backend server** for changes to take effect

**Important:** The JWKS URL is **instance-specific**. Each Clerk application has a unique URL. Don't use a generic URL like `https://api.clerk.com/.well-known/jwks.json` (this won't work).

## Troubleshooting

### JWT Verification Failed: HTTP Error 404

**Error Message:**

```
PyJWKClientConnectionError: Fail to fetch data from the url, err: "HTTP Error 404: Not Found"
```

**Cause:** Missing or incorrect `CLERK_JWKS_URL` in your `.env` file.

**Solution:**

1. Follow the "Setting Up CLERK_JWKS_URL" section above
2. Make sure the URL is your **instance-specific** JWKS endpoint
3. Restart the backend server after adding the variable

### Port Already in Use (Address Already in Use)

**Error Message:**

```
OSError: [Errno 48] Address already in use
```

**Cause:** Another process is using port 8000.

**Solution:**

**Option 1: Kill the existing process**

```bash
# Find what's using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process (replace PID with the actual process ID)
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

**Option 2: Use a different port**

```bash
poetry run uvicorn main:app --reload --port 8001
```

### Database Connection Failed

**Error Message:**

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Cause:** Invalid `DATABASE_URL` or database not accessible.

**Solution:**

1. **Check your `.env` file** has the correct `DATABASE_URL`
2. **Verify Supabase connection string:**
   - Go to Supabase Dashboard → Project Settings → Database
   - Copy the connection string (URI mode)
   - Make sure it uses `postgresql+asyncpg://` prefix
3. **Test connection:**
   ```bash
   poetry run python -c "from app.db.session import engine; import asyncio; asyncio.run(engine.connect())"
   ```

### OpenAI API Key Invalid

**Error Message:**

```
openai.error.AuthenticationError: Incorrect API key provided
```

**Cause:** Missing or invalid `OPENAI_API_KEY`.

**Solution:**

1. Get your API key from https://platform.openai.com/api-keys
2. Add to `.env` file:
   ```bash
   OPENAI_API_KEY=sk-proj-...
   ```
3. Make sure the key starts with `sk-` and is not expired
4. Restart the backend server

### Import Errors or Missing Dependencies

**Error Message:**

```
ModuleNotFoundError: No module named 'xxx'
```

**Cause:** Dependencies not installed or virtual environment not activated.

**Solution:**

```bash
# Reinstall dependencies
poetry install

# If still failing, try clearing cache
poetry cache clear pypi --all
poetry install

# Verify you're in the correct directory
pwd  # Should show .../delight/packages/backend
```

### Database Migrations Out of Sync

**Error Message:**

```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxx'
```

**Cause:** Local migration state doesn't match database state.

**Solution:**

```bash
# Check current migration status
poetry run alembic current

# Apply all pending migrations
poetry run alembic upgrade head

# If completely broken, stamp to current version
poetry run alembic stamp head
```

## Additional Resources

- **Main Docs:** See `/docs` directory in project root
- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **SQLAlchemy 2.0 Docs:** https://docs.sqlalchemy.org/en/20/
- **Clerk Docs:** https://clerk.com/docs
