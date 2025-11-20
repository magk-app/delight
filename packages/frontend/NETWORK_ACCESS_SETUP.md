# Network Access Setup Guide

This guide explains how to configure the frontend to work when accessed via network (ngrok, IP address, or domain) instead of localhost.

## Problem

When you access the frontend via:

- ngrok URL (e.g., `https://abc123.ngrok.io`)
- IP address (e.g., `http://10.90.113.250:3000`)
- Network domain

The frontend still tries to connect to `http://localhost:8001` for the backend, which fails because:

- `localhost` on the client's machine is not the same as `localhost` on your server
- The browser can't reach `localhost:8001` from a remote device

## Solution

You need to expose your backend to the network and configure the frontend to use that network-accessible URL.

### Option 1: Using ngrok (Recommended for Testing)

1. **Expose the backend with ngrok:**

   ```bash
   # In a separate terminal, expose port 8001
   ngrok http 8001
   ```

2. **Copy the ngrok URL** (e.g., `https://abc123.ngrok.io`)

3. **Set the environment variable:**

   Create or update `.env.local` in `packages/frontend/` (`.env.local` is preferred over `.env` for local development):

   ```env
   NEXT_PUBLIC_EXPERIMENTAL_API_URL=https://abc123.ngrok.io
   ```

4. **Restart the Next.js dev server:**

   ```bash
   cd packages/frontend
   pnpm dev
   ```

5. **Access your frontend** via ngrok or network IP - it will now connect to the ngrok backend URL.

### Option 2: Using Network IP Address

1. **Find your machine's IP address:**

   ```bash
   # Windows
   ipconfig

   # Mac/Linux
   ifconfig
   ```

2. **Start the backend** bound to your network IP:

   ```bash
   cd packages/backend
   # Make sure the backend accepts connections from your network IP
   poetry run python experiments/web/dashboard_server.py --host 0.0.0.0 --port 8001
   ```

3. **Set the environment variable:**

   Create or update `.env.local` in `packages/frontend/` (`.env.local` is preferred over `.env` for local development):

   ```env
   NEXT_PUBLIC_EXPERIMENTAL_API_URL=http://10.90.113.250:8001
   ```

   (Replace with your actual IP address)

4. **Restart the Next.js dev server:**
   ```bash
   cd packages/frontend
   pnpm dev
   ```

### Option 3: Using a Domain/Production URL

If you have a deployed backend (e.g., on Railway, Heroku, etc.):

1. **Set the environment variable:**

   ```env
   NEXT_PUBLIC_EXPERIMENTAL_API_URL=https://your-backend.railway.app
   ```

2. **Restart the Next.js dev server**

## Important Notes

### Environment Variables

- **`NEXT_PUBLIC_EXPERIMENTAL_API_URL`** - Must be set in `.env.local` for local development
  - Use `.env.local` (not `.env`) - it's automatically ignored by git and takes precedence
  - The `NEXT_PUBLIC_` prefix makes the variable available in the browser
  - Changes to `.env.local` require restarting the Next.js dev server

### CORS Configuration

**Good news:** The backend automatically allows all ngrok origins for development! You don't need to configure CORS manually when using ngrok.

The backend CORS configuration:

- ✅ Automatically allows all `*.ngrok.io`, `*.ngrok-free.app`, and `*.ngrok.app` origins
- ✅ Allows `localhost:3000` and `127.0.0.1:3000` by default
- ✅ Can be customized via `CORS_ORIGINS` environment variable if needed

**If you need to add custom origins**, set the `CORS_ORIGINS` environment variable in your backend:

```bash
# In packages/backend/.env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://your-custom-domain.com
```

**To disable automatic ngrok CORS** (for production), set:

```bash
ALLOW_NGROK_ORIGINS=false
```

### Security Considerations

- **Never commit `.env.local`** to version control
- For production, set environment variables in your hosting platform (Vercel, Railway, etc.)
- Use HTTPS in production (ngrok provides HTTPS automatically)

## Troubleshooting

### "Failed to fetch" Error

1. **Check the environment variable is set:**

   ```bash
   # In browser console
   console.log(process.env.NEXT_PUBLIC_EXPERIMENTAL_API_URL)
   ```

2. **Verify the backend is accessible:**

   ```bash
   # Test the backend URL directly
   curl https://your-backend-url.ngrok.io/health
   ```

3. **Check CORS settings** - Make sure your backend allows requests from your frontend origin

4. **Verify both services are running:**
   - Backend on port 8001
   - Frontend on port 3000

### Backend Not Accessible

- Make sure your firewall allows connections on port 8001
- For ngrok, verify the tunnel is active and the URL is correct
- For IP access, ensure the backend is bound to `0.0.0.0` (not just `127.0.0.1`)

## Quick Reference

| Scenario          | Frontend URL                | Backend URL                 | Environment Variable                                         |
| ----------------- | --------------------------- | --------------------------- | ------------------------------------------------------------ |
| Local development | `http://localhost:3000`     | `http://localhost:8001`     | `NEXT_PUBLIC_EXPERIMENTAL_API_URL=http://localhost:8001`     |
| ngrok frontend    | `https://abc.ngrok.io`      | `https://xyz.ngrok.io`      | `NEXT_PUBLIC_EXPERIMENTAL_API_URL=https://xyz.ngrok.io`      |
| Network IP        | `http://10.90.113.250:3000` | `http://10.90.113.250:8001` | `NEXT_PUBLIC_EXPERIMENTAL_API_URL=http://10.90.113.250:8001` |
| Production        | `https://app.example.com`   | `https://api.example.com`   | Set in hosting platform                                      |
