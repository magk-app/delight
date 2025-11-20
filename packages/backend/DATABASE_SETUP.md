# Database Setup Guide

## Problem

If you're seeing errors like:

- `[Errno 11001] getaddrinfo failed`
- `Failed to create conversation: [Errno 11001] getaddrinfo failed`
- `Failed to get conversations: [Errno 11001] getaddrinfo failed`

This means the backend can't connect to the database because `DATABASE_URL` is not set or incorrect.

## Solution

### Step 1: Create `.env` file

Create a `.env` file in `packages/backend/` if it doesn't exist:

```bash
cd packages/backend
cp env.example .env
```

### Step 2: Set DATABASE_URL

Edit `packages/backend/.env` and set your `DATABASE_URL`:

#### Option A: Local PostgreSQL (if you have PostgreSQL installed)

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/delight
```

**Note:** Make sure PostgreSQL is running and the database `delight` exists.

#### Option B: Supabase (Cloud PostgreSQL)

**Important:**

- If you're on Windows and getting `[Errno 11001] getaddrinfo failed`, use the **Connection Pooler** URL instead of the direct connection.
- **For SQLAlchemy:** Use **Session Mode** (port 5432), NOT Transaction Mode (port 6543), because SQLAlchemy's asyncpg dialect requires prepared statements.

1. Go to your Supabase project: https://supabase.com/dashboard
2. Go to **Settings** → **Database**
3. Look for **Connection Pooling** section
4. Copy the **Connection String** from the **Session Mode** pooler (port 5432)
   - Session Mode URL: `aws-1-us-east-2.pooler.supabase.com:5432` (supports prepared statements)
   - Transaction Mode URL: `aws-1-us-east-2.pooler.supabase.com:6543` (does NOT support prepared statements)
5. Replace `[YOUR-PASSWORD]` with your actual database password
6. Add it to `.env`:

```env
# Use Session Mode pooler (port 5432) - REQUIRED for SQLAlchemy
DATABASE_URL=postgresql://postgres.zllzszxipezzmgfjllox:[YOUR-PASSWORD]@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

**Note:**

- **Session Mode (port 5432)** supports prepared statements and works with SQLAlchemy
- **Transaction Mode (port 6543)** does NOT support prepared statements and will cause errors with SQLAlchemy

#### Option C: Railway PostgreSQL

If you're using Railway:

1. Go to your Railway project
2. Add a PostgreSQL service
3. Railway will automatically create a `DATABASE_URL` environment variable
4. Copy it to your local `.env` file

### Step 3: Run Database Migrations

After setting `DATABASE_URL`, run migrations to create the tables:

```bash
cd packages/backend
poetry run alembic upgrade head
```

### Step 4: Restart Backend

Restart your backend server:

```bash
cd packages/backend
poetry run python experiments/web/dashboard_server.py
```

## Verify Setup

Check that the database connection works:

```bash
cd packages/backend
poetry run python -c "from app.core.config import settings; print('Database URL:', settings.async_database_url[:50] + '...')"
```

If you see an error about `DATABASE_URL` not being set, make sure:

1. The `.env` file exists in `packages/backend/`
2. The `.env` file contains `DATABASE_URL=...`
3. You restarted the backend after creating/editing `.env`

## Troubleshooting

### "DATABASE_URL is not set" error

- Make sure `.env` file exists in `packages/backend/`
- Check that `DATABASE_URL` is in the file (no quotes needed)
- Restart the backend server

### "getaddrinfo failed" error

- Check that the database hostname in `DATABASE_URL` is correct
- Make sure the database server is running (if local)
- Verify network connectivity to the database (if cloud)
- Check that the database port (usually 5432) is accessible

### "password authentication failed" error

- Verify the password in `DATABASE_URL` is correct
- Make sure special characters in the password are URL-encoded

### "database does not exist" error

- Create the database: `CREATE DATABASE delight;`
- Or use an existing database name in your `DATABASE_URL`
