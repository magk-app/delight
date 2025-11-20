# LangGraph Studio - Visual Debugging Setup

**Goal:** Get the visual Studio UI working safely on Windows.

---

## 🚀 One-Click Launch (Recommended)

### First Time Setup (5 minutes)

1. **Run the launcher script:**
   ```powershell
   cd packages/backend
   .\launch-studio.ps1
   ```

2. **On first run, it will:**
   - Create a dev-only Chrome profile
   - Open Chrome flags page automatically
   - Show you exactly what to do

3. **In the Chrome window that opens:**
   - You'll see: `chrome://flags/#block-insecure-private-network-requests`
   - Change "Default" to **"Disabled"**
   - Click the blue **"Relaunch"** button
   - Chrome will restart

4. **Run the script again:**
   ```powershell
   .\launch-studio.ps1
   ```

5. **Done!** Studio opens automatically 🎉

### Every Time After

Just run:
```powershell
cd packages/backend
.\launch-studio.ps1
```

**What it does:**
- ✅ Starts LangGraph server (if not running)
- ✅ Launches Chrome dev profile
- ✅ Opens Studio UI automatically
- ✅ Your main Chrome stays secure

---

## 🎨 What You Get: Visual Studio UI

### Graph Editor
- See your agent flow visually: `recall_context` → `analyze_emotion` → `generate_response`
- Click nodes to inspect code
- Drag to rearrange
- Beautiful graph visualization

### State Inspector
- See state at each node
- Watch messages flow through
- Inspect retrieved memories
- Monitor emotional state detection

### Interactive Testing
- Type messages in the UI
- See responses stream in
- Debug with real inputs
- No API calls needed

### Token Monitoring
- See token usage per node
- Track costs in real-time
- Optimize prompts

---

## 🔒 Security: Why This is Safe

### What We're Doing
**Using a separate Chrome profile** with relaxed security **only for localhost development**.

### Your Main Browser
- ✅ **Stays completely secure**
- ✅ Normal Chrome (your default) is untouched
- ✅ All your passwords, history, extensions separate
- ✅ Can run both profiles simultaneously

### Dev Profile
- ⚠️ **Only use for localhost:2024**
- ⚠️ Don't browse random websites
- ⚠️ Only for LangGraph testing
- ✅ Isolated from your main profile

### Risk Level
- **Low** - Profile only accesses your own localhost server
- **Lower** - Not using main browser for this
- **Lowest** - Server only runs when you're actively developing

---

## 🛠️ Alternative: ngrok (No Browser Changes)

If you prefer zero browser changes:

### 1. Install ngrok
Download from: https://ngrok.com/download

### 2. Start LangGraph server
```powershell
cd packages/backend
poetry run langgraph dev
```

### 3. In another terminal, create tunnel
```powershell
ngrok http 2024
```

### 4. Copy the HTTPS URL
```
Forwarding https://abc123-456.ngrok-free.app -> http://localhost:2024
```

### 5. Open Studio with ngrok URL
```
https://smith.langchain.com/studio/?baseUrl=https://abc123-456.ngrok-free.app
```

**Pros:**
- ✅ No browser security changes
- ✅ Works on any browser
- ✅ Can share with teammates

**Cons:**
- ⚠️ Data goes through ngrok's servers (don't use for sensitive data)
- ⚠️ Free tier has session limits
- ⚠️ URL changes each time

---

## 🎯 Recommended Approach

**Use the PowerShell launcher script:**

**Why:**
1. **One command** - `.\launch-studio.ps1`
2. **Automatic** - Starts server, opens Studio
3. **Safe** - Separate Chrome profile
4. **Fast** - No external dependencies
5. **Private** - All data stays local

**When to use ngrok instead:**
- Need to demo to someone remotely
- Want to test on phone/tablet
- Multiple people testing same agent

---

## 📝 Quick Reference

### Start Studio (Recommended Way)
```powershell
cd packages/backend
.\launch-studio.ps1
```

### Manual Start (If needed)
```powershell
# Terminal 1: Start server
cd packages/backend
poetry run langgraph dev

# Terminal 2: Open Chrome dev profile
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  -ArgumentList "--user-data-dir=$env:USERPROFILE\chrome-langgraph-dev", `
  "https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
```

### Check if Flag is Disabled
In dev profile, visit:
```
chrome://flags/#block-insecure-private-network-requests
```

Should say: **"Disabled"** (not "Default")

---

## 🐛 Troubleshooting

### Issue: "Failed to fetch" in Studio

**Check:**
1. Is server running? `http://127.0.0.1:2024/docs` should work
2. Are you using the dev profile? (Check URL bar - should have separate icon)
3. Is the flag disabled? Check `chrome://flags` in dev profile

**Fix:**
```powershell
# Run launcher again - it checks everything
.\launch-studio.ps1
```

### Issue: Server won't start

**Check:**
```powershell
cd packages/backend
poetry install  # Ensure all deps installed
poetry run langgraph --version  # Should show version
```

### Issue: Can't find Chrome

Edit `launch-studio.ps1`, update line 6:
```powershell
$CHROME_PATH = "YOUR_CHROME_PATH_HERE"
```

Common locations:
- `C:\Program Files\Google\Chrome\Application\chrome.exe`
- `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`

---

## 🎓 Learning More

Once Studio is working, try:
1. Send test messages
2. Watch state flow through nodes
3. Inspect emotional detection
4. Monitor token usage
5. Test different inputs

**Visual debugging is way better than API calls!** 🚀

---

**Created:** 2025-11-18
**For:** Windows PowerShell
**Tested:** Chrome, PowerShell 5.1+
