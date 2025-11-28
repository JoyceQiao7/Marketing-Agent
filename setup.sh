#!/bin/bash

# Mulan Marketing Agent - Quick Setup Script
# This script helps set up the development environment

set -e

echo "🚀 Mulan Marketing Agent - Setup Script"
echo "========================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $python_version"

# Check Node version
echo ""
echo "📋 Checking Node.js version..."
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "✅ Found Node.js $node_version"
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check Redis
echo ""
echo "📋 Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is installed but not running"
        echo "   Start it with: redis-server"
    fi
else
    echo "❌ Redis not found. Please install Redis"
    exit 1
fi

# Setup backend
echo ""
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

cd ..

# Setup frontend
echo ""
echo "📦 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
else
    echo "✅ Node modules already installed"
fi

cd ..

# Check for .env file
echo ""
echo "🔑 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "   Please create .env file with your credentials"
    echo "   See README.md for required variables"
else
    echo "✅ .env file exists"
fi

# Summary
echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Configure .env file with your API credentials"
echo "   2. Run database schema in Supabase (scripts/schema.sql)"
echo "   3. Start services (see README.md for commands)"
echo ""
echo "🚀 Quick start:"
echo "   Terminal 1: cd backend && source venv/bin/activate && uvicorn api.main:app --reload"
echo "   Terminal 2: cd backend && source venv/bin/activate && celery -A tasks.celery_app worker -l info"
echo "   Terminal 3: cd backend && source venv/bin/activate && celery -A tasks.celery_app beat -l info"
echo "   Terminal 4: cd frontend && npm run dev"
echo ""
echo "✨ Happy lead hunting!"

