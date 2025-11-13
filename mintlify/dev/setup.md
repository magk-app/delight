---
title: Development Setup
description: Complete environment setup guide for Delight developers
---

# Development Setup

Complete guide to setting up your Delight development environment.

## Prerequisites

- **Node.js** 20+ and **pnpm** 8+
- **Python** 3.11+ with **Poetry**
- **Supabase** account (free tier works)
- **Clerk** account (free tier works)
- **OpenAI API key**

## Quick Setup

```bash
# Clone the repository
git clone https://github.com/your-org/delight.git
cd delight

# Install dependencies
pnpm install
cd packages/backend && poetry install
```

## Environment Configuration

### Backend Setup

1. Copy the example environment file:

```bash
cp packages/backend/.env.example packages/backend/.env
```

2. Fill in your environment variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_key
CLERK_SECRET_KEY=your_clerk_secret
```

### Frontend Setup

1. Copy the example environment file:

```bash
cp packages/frontend/.env.example packages/frontend/.env.local
```

2. Fill in your environment variables:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Database Setup

Run migrations to set up your Supabase database:

```bash
cd packages/backend
poetry run python scripts/migrate.py
```

## Running the Application

### Start Both Services

From the repository root:

```bash
pnpm dev
```

This starts:

- Frontend on http://localhost:3000
- Backend API on http://localhost:8000

### Start Services Separately

```bash
# Frontend only
pnpm dev:frontend

# Backend only
pnpm dev:backend
```

## Verification

1. **Frontend**: Visit http://localhost:3000
2. **Backend API Docs**: Visit http://localhost:8000/docs (FastAPI Swagger UI)
3. **Health Check**: Visit http://localhost:8000/health

## Development Workflow

See the [Developer Guide](/dev/developer-guide) for:

- Story development workflow
- Code quality standards
- Testing guidelines
- Commit conventions

## Troubleshooting

### Port Already in Use

Change ports in:

- Frontend: `packages/frontend/package.json` scripts
- Backend: `packages/backend/main.py` uvicorn configuration

### Poetry Not Installed

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Database Connection Errors

- Verify Supabase URL and keys
- Ensure Supabase project is active
- Check migrations ran successfully

## Frontend Assets

### Favicon

To update the favicon for the frontend app:

1. **Place favicon files** in `packages/frontend/public/`:

   - `favicon.ico` - Main favicon (required)
   - `apple-touch-icon.png` - iOS home screen icon (optional, 180x180px recommended)
   - `favicon.svg` - Modern SVG favicon (optional)

2. **Update `src/app/layout.tsx`** metadata if using different filenames:

   ```typescript
   export const metadata: Metadata = {
     icons: {
       icon: "/favicon.ico",
       shortcut: "/favicon.ico",
       apple: "/apple-touch-icon.png",
     },
   };
   ```

3. **Alternative**: Next.js 15 also supports placing favicon files directly in `src/app/`:

   - `src/app/favicon.ico`
   - `src/app/icon.png` or `icon.svg`
   - These are automatically detected

4. **Restart dev server** to see changes:
   ```bash
   pnpm dev:frontend
   ```

### Images

All static images should be placed in `packages/frontend/public/images/`.

**Adding Images:**

1. **Place your image** in `packages/frontend/public/images/`:

   ```bash
   # Example
   packages/frontend/public/images/logo.png
   ```

2. **Reference in components**:

   **Option 1: Public path (for static assets)**

   ```tsx
   <img src="/images/logo.png" alt="Logo" />
   ```

   **Option 2: Import (for optimized images)**

   ```tsx
   import Image from "next/image";
   import logo from "@/public/images/logo.png";

   <Image src={logo} alt="Logo" />;
   ```

3. **Supported formats**: `.png`, `.jpg`, `.jpeg`, `.svg`, `.gif`, `.webp`

**Best Practices:**

- Use Next.js `Image` component for automatic optimization
- Keep file sizes reasonable (< 500KB for most images)
- Use SVG for logos and icons
- Use WebP or optimized PNG/JPG for photos
- Consider responsive images for different screen sizes

## Next Steps

- Read the [Developer Guide](/dev/developer-guide)
- Check the [Quick Reference](/dev/quick-reference) for commands
- Review [Contributing Guidelines](/dev/contributing)
