#!/bin/bash
# Personal AI Assistant - Mac/Linux Installer

echo ""
echo "================================================"
echo "  Personal AI Assistant - Setup"
echo "================================================"
echo ""

# Check Python
echo "Checking Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 not found"
    echo "Install from: https://python.org"
    exit 1
fi
echo "✓ Python found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo "✓ Virtual environment created"

# Activate
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment active"

# Install packages
echo ""
echo "Installing Python packages..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi
echo "✓ Packages installed"

# Setup
echo ""
echo "Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file"
else
    echo "✓ .env already exists"
fi

mkdir -p logs
echo "✓ Created logs directory"

echo ""
echo "================================================"
echo "  SETUP COMPLETE!"
echo "================================================"
echo ""
echo "NEXT STEPS:"
echo "1. Edit .env file and add your Claude API key"
echo "2. Run: python main.py"
echo "3. Open browser: http://localhost:8000"
echo ""
echo "To activate virtual environment next time:"
echo "  source venv/bin/activate"
echo ""
