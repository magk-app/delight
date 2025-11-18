# LangGraph Studio with ngrok

**Best option if you don't want to change browser settings.**

---

## Quick Start

### 1. Install ngrok (One Time)

**Download & Install:**
```bash
# Download from: https://ngrok.com/download

# Or use chocolatey
choco install ngrok

# Or use scoop
scoop install ngrok
```

**Sign up & Configure:**
```bash
# 1. Sign up at: https://dashboard.ngrok.com/signup
# 2. Copy your authtoken
# 3. Configure:
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### 2. Run the Launcher

```powershell
cd packages/backend
.\launch-studio-ngrok.ps1
```

**What it does:**
- ✅ Starts LangGraph server
- ✅ Creates ngrok HTTPS tunnel
- ✅ Gets your public URL
- ✅ Creates Studio URL automatically
- ✅ Copies URL to clipboard
- ✅ Opens Studio in browser

### 3. Done!

Studio opens with your agent accessible via HTTPS tunnel. No browser changes needed!

---

## Manual Setup (If Script Doesn't Work)

### Terminal 1: Start Server
```bash
cd packages/backend
poetry run langgraph dev
```

### Terminal 2: Start ngrok
```bash
ngrok http 2024
```

**Copy the HTTPS URL:**
```
Forwarding    https://abc123-456-789.ngrok-free.app -> http://localhost:2024
              ↑ Copy this URL
```

### Open Studio

Paste into browser:
```
https://smith.langchain.com/studio/?baseUrl=https://abc123-456-789.ngrok-free.app
                                              ↑ Your ngrok URL here
```

---

## How It Works

### The Problem (Before ngrok)
```
Studio (HTTPS) ──X──> localhost (HTTP)
                 ↑
            Blocked by browser
```

### The Solution (With ngrok)
```
Studio (HTTPS) ──✓──> ngrok (HTTPS) ──✓──> localhost (HTTP)
                       ↑
                  Public tunnel
```

**ngrok creates an HTTPS tunnel** to your localhost:
- Studio sees: `https://abc123.ngrok-free.app` (HTTPS public URL)
- Browser: "HTTPS→HTTPS, allowed ✅"
- ngrok forwards to: `http://localhost:2024`

---

## Features

### ngrok Web Interface

Monitor requests at: `http://127.0.0.1:4040`

**You can see:**
- All requests from Studio
- Request/response details
- Replay requests
- Inspect traffic

### Studio URL Format

```
https://smith.langchain.com/studio/?baseUrl=https://YOUR-NGROK-URL.ngrok-free.app
                                     ↑
                              This tells Studio where your API is
```

**You don't change anything in Studio settings.** The `baseUrl` parameter does it all.

---

## Pros & Cons

### ✅ Pros
- **No browser changes** - works in any browser
- **HTTPS** - proper security
- **Shareable** - teammates can access your local agent
- **Web interface** - monitor all requests
- **Works everywhere** - mobile, tablet, other computers

### ⚠️ Cons
- **External service** - data goes through ngrok's servers
- **URL changes** - new URL each time (free tier)
- **Latency** - slight delay (usually <50ms)
- **Rate limits** - free tier has limits

### Free Tier Limits
- ✅ 1 ngrok process
- ✅ 40 connections/minute
- ✅ HTTPS included
- ⚠️ URL changes each restart
- ⚠️ Session timeout after inactivity

**For development:** Free tier is plenty!

---

## Security Note

**What goes through ngrok:**
- ✅ API requests/responses
- ✅ Graph execution
- ✅ Your prompts and responses

**What stays local:**
- ✅ OpenAI API key (never sent through ngrok)
- ✅ Database credentials
- ✅ Local files

**Risk:** Low - but don't use for sensitive production data.

**For testing Eliza agent:** Totally fine! ✅

---

## Troubleshooting

### Issue: "command not found: ngrok"

**Solution:** Add ngrok to PATH or use full path:
```bash
# Windows (if installed via chocolatey)
C:\ProgramData\chocolatey\bin\ngrok.exe http 2024

# Or download .exe and run directly
.\ngrok.exe http 2024
```

### Issue: "failed to validate account"

**Solution:** Configure authtoken:
```bash
ngrok config add-authtoken YOUR_TOKEN_FROM_DASHBOARD
```

Get token from: https://dashboard.ngrok.com/get-started/your-authtoken

### Issue: ngrok URL changes every time

**Solution:** Upgrade to paid plan for static domain, or just use new URL each time.

### Issue: "tunnel not found" in Studio

**Solution:** Make sure ngrok is still running. Check Terminal 2.

---

## Comparison: ngrok vs Browser Flag

| Feature | ngrok | Browser Flag |
|---------|-------|--------------|
| Setup time | 5 min (one time) | 30 sec |
| Browser changes | None | Disable security flag |
| Works on mobile | ✅ Yes | ❌ No |
| Shareable | ✅ Yes | ❌ No |
| Data privacy | ⚠️ Goes through ngrok | ✅ All local |
| Cost | Free tier OK | Free |
| Convenience | 2 commands | 1 command |

**Recommendation:**
- **Solo dev work:** Browser flag (faster, more private)
- **Team testing:** ngrok (shareable)
- **Mobile testing:** ngrok (only option)
- **Paranoid about data:** Browser flag (all local)

---

## Alternative: Static Domain (Paid)

**ngrok Pro ($10/mo):**
- Custom subdomain: `your-app.ngrok.app`
- Doesn't change
- No session limits
- Faster speeds

**Worth it if:**
- Using Studio daily
- Hate updating URL
- Working with team

**Not worth it if:**
- Just testing occasionally
- OK with browser flag alternative

---

## Next Steps

Once Studio is working:
1. Test your Eliza agent
2. Send test messages
3. Watch state flow through nodes
4. Debug emotion detection
5. Monitor token usage

Then integrate into your chat API (Story 2.5)!

---

**Created:** 2025-11-18
**Tested:** Windows 10/11, PowerShell 5.1+
**ngrok Version:** 3.x
