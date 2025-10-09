# Quick Start Script for NyayaLens
# Run this to test the application locally

Write-Host "🏛️ NyayaLens - AI-Powered Judicial Insights" -ForegroundColor Blue
Write-Host "=============================================" -ForegroundColor Blue
Write-Host ""

# Check Python version
Write-Host "📋 Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "   $pythonVersion" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "   ✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host ""
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

Write-Host "   ✅ Dependencies installed" -ForegroundColor Green

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "⚙️ Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "   ✅ .env file created" -ForegroundColor Green
}

# Display info
Write-Host ""
Write-Host "=============================================" -ForegroundColor Blue
Write-Host "🚀 Starting NyayaLens Application..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Blue
Write-Host ""
Write-Host "📍 The app will open in your browser at:" -ForegroundColor Cyan
Write-Host "   http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "⌨️  Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run Streamlit
streamlit run app.py
