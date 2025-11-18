# LangGraph Studio Launcher (Windows)
# Launches Chrome dev profile with Studio UI ready

# Configuration
$CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$DEV_PROFILE = "$env:USERPROFILE\chrome-langgraph-dev"
$STUDIO_URL = "https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"

Write-Host "🚀 LangGraph Studio Launcher" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Chrome exists
if (-not (Test-Path $CHROME_PATH)) {
    Write-Host "❌ Chrome not found at: $CHROME_PATH" -ForegroundColor Red
    Write-Host "Please update CHROME_PATH in this script" -ForegroundColor Yellow
    exit 1
}

# Check if dev profile exists
$firstRun = -not (Test-Path $DEV_PROFILE)

if ($firstRun) {
    Write-Host "📝 First time setup..." -ForegroundColor Yellow
    Write-Host "Creating dev profile at: $DEV_PROFILE" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: After Chrome opens, you need to:" -ForegroundColor Yellow
    Write-Host "   1. Navigate to: chrome://flags/#block-insecure-private-network-requests" -ForegroundColor White
    Write-Host "   2. Set to 'Disabled'" -ForegroundColor White
    Write-Host "   3. Click 'Relaunch' button" -ForegroundColor White
    Write-Host "   4. Bookmark the flags page for easy access later" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key to continue and open Chrome dev profile..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

    # Launch Chrome with dev profile (will open default page)
    Start-Process $CHROME_PATH -ArgumentList "--user-data-dir=`"$DEV_PROFILE`"", "chrome://flags/#block-insecure-private-network-requests"

    Write-Host ""
    Write-Host "✅ Chrome dev profile created!" -ForegroundColor Green
    Write-Host "⚠️  After you disable the flag and relaunch Chrome, run this script again" -ForegroundColor Yellow
    exit 0
}

# Dev profile exists - normal launch
Write-Host "✅ Using dev profile: $DEV_PROFILE" -ForegroundColor Green

# Start LangGraph server in background
Write-Host "🔧 Starting LangGraph server..." -ForegroundColor Cyan
$backend = "$PSScriptRoot\.."

# Check if server is already running
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:2024/assistants" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "✅ LangGraph server already running" -ForegroundColor Green
    $serverRunning = $true
} catch {
    Write-Host "⏳ Starting LangGraph server (this takes ~30 seconds)..." -ForegroundColor Yellow
    $serverRunning = $false

    # Start server in new window
    $serverScript = @"
Set-Location '$backend'
poetry run langgraph dev
"@

    $serverScriptPath = "$env:TEMP\langgraph-server.ps1"
    $serverScript | Out-File -FilePath $serverScriptPath -Encoding UTF8

    Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$serverScriptPath`"" -WindowStyle Normal

    Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow

    # Wait for server to be ready (max 60 seconds)
    $maxWait = 60
    $waited = 0
    while ($waited -lt $maxWait) {
        Start-Sleep -Seconds 2
        $waited += 2

        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:2024/assistants" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
            Write-Host "✅ Server ready!" -ForegroundColor Green
            $serverRunning = $true
            break
        } catch {
            Write-Host "." -NoNewline -ForegroundColor Gray
        }
    }

    if (-not $serverRunning) {
        Write-Host ""
        Write-Host "⚠️  Server is taking longer than expected" -ForegroundColor Yellow
        Write-Host "Check the server window for errors" -ForegroundColor Yellow
    }
}

Write-Host ""

# Launch Chrome with Studio URL
Write-Host "🎨 Opening LangGraph Studio..." -ForegroundColor Cyan
Start-Process $CHROME_PATH -ArgumentList "--user-data-dir=`"$DEV_PROFILE`"", $STUDIO_URL

Write-Host ""
Write-Host "✨ Done!" -ForegroundColor Green
Write-Host ""
Write-Host "Studio URL: $STUDIO_URL" -ForegroundColor Cyan
Write-Host "API Docs:   http://127.0.0.1:2024/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   - This Chrome profile is for dev work only" -ForegroundColor Gray
Write-Host "   - Your main Chrome browser stays secure" -ForegroundColor Gray
Write-Host "   - Server runs in separate window (don't close it)" -ForegroundColor Gray
Write-Host ""
