#!/bin/bash
# Quick Start Script for NyayaLens (Linux/Mac)

echo "🏛️ NyayaLens - AI-Powered Judicial Insights"
echo "============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "   ✅ Dependencies installed"

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "   ✅ .env file created"
fi

# Display info
echo ""
echo "============================================="
echo "🚀 Starting NyayaLens Application..."
echo "============================================="
echo ""
echo "📍 The app will open in your browser at:"
echo "   http://localhost:8501"
echo ""
echo "⌨️  Press Ctrl+C to stop the server"
echo ""

# Run Streamlit
streamlit run app.py
