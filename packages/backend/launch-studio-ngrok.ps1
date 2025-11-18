# LangGraph Studio with ngrok - One Command Setup
# No browser security changes needed!

Write-Host "🚀 LangGraph Studio (ngrok mode)" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if ngrok is installed
try {
    $ngrokVersion = ngrok version 2>&1
    Write-Host "✅ ngrok installed: $ngrokVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ngrok not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install ngrok first:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://ngrok.com/download" -ForegroundColor White
    Write-Host "  2. Or run: choco install ngrok" -ForegroundColor White
    Write-Host "  3. Then configure: ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Start LangGraph server in background
Write-Host "🔧 Starting LangGraph server..." -ForegroundColor Cyan
$backend = "$PSScriptRoot\.."

# Check if server is already running
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:2024/assistants" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "✅ LangGraph server already running" -ForegroundColor Green
    $serverRunning = $true
} catch {
    Write-Host "⏳ Starting LangGraph server (takes ~15 seconds)..." -ForegroundColor Yellow
    $serverRunning = $false

    # Start server in new window
    $serverScript = @"
Set-Location '$backend'
Write-Host 'Starting LangGraph server...' -ForegroundColor Cyan
poetry run langgraph dev
"@

    $serverScriptPath = "$env:TEMP\langgraph-server.ps1"
    $serverScript | Out-File -FilePath $serverScriptPath -Encoding UTF8

    Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$serverScriptPath`"" -WindowStyle Normal

    # Wait for server
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

    Write-Host ""

    if (-not $serverRunning) {
        Write-Host "⚠️  Server taking longer than expected" -ForegroundColor Yellow
        Write-Host "Check the server window for errors" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "🚇 Starting ngrok tunnel..." -ForegroundColor Cyan

# Start ngrok in background and capture output
$ngrokScript = @"
ngrok http 2024 --log=stdout
"@

$ngrokScriptPath = "$env:TEMP\ngrok-tunnel.ps1"
$ngrokScript | Out-File -FilePath $ngrokScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$ngrokScriptPath`"" -WindowStyle Normal

Write-Host "⏳ Waiting for ngrok to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Get ngrok URL from API
try {
    $ngrokApi = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -Method GET
    $publicUrl = $ngrokApi.tunnels[0].public_url

    Write-Host "✅ ngrok tunnel active!" -ForegroundColor Green
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "📡 Public URL: $publicUrl" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""

    # Create Studio URL
    $studioUrl = "https://smith.langchain.com/studio/?baseUrl=$publicUrl"

    Write-Host "🎨 LangGraph Studio URL:" -ForegroundColor Cyan
    Write-Host $studioUrl -ForegroundColor White
    Write-Host ""

    # Copy to clipboard
    Set-Clipboard -Value $studioUrl
    Write-Host "✅ Studio URL copied to clipboard!" -ForegroundColor Green
    Write-Host ""

    # Ask if they want to open it
    Write-Host "Open Studio in browser? (Y/n): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host

    if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
        Start-Process $studioUrl
        Write-Host "✅ Opening Studio..." -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "💡 Tips:" -ForegroundColor Yellow
    Write-Host "  • ngrok URL changes each time (free tier)" -ForegroundColor Gray
    Write-Host "  • Keep both windows open while testing" -ForegroundColor Gray
    Write-Host "  • Monitor at: http://127.0.0.1:4040" -ForegroundColor Gray
    Write-Host "  • No browser security changes needed!" -ForegroundColor Gray
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host ""

} catch {
    Write-Host "❌ Could not get ngrok URL" -ForegroundColor Red
    Write-Host "Check the ngrok window for errors" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual setup:" -ForegroundColor Yellow
    Write-Host "  1. Check ngrok window for HTTPS URL" -ForegroundColor White
    Write-Host "  2. Copy it (looks like: https://abc123.ngrok-free.app)" -ForegroundColor White
    Write-Host "  3. Go to: https://smith.langchain.com/studio/?baseUrl=YOUR_NGROK_URL" -ForegroundColor White
    Write-Host ""
}
