#!/bin/bash

# Mkaguzi App Dependencies Installation Script
# This script installs Python dependencies for the Mkaguzi Internal Audit Management System

set -e  # Exit on any error

echo "🚀 Installing Mkaguzi App Dependencies"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found in current directory"
    echo "Please run this script from the mkaguzi app directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check Python version (should be >= 3.10 as per pyproject.toml)
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $PYTHON_VERSION detected. Python >= $REQUIRED_VERSION is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed or not in PATH"
    exit 1
fi

echo "✅ pip3 detected"

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
echo "This may take a few minutes depending on your internet connection."
echo ""

pip3 install -r requirements.txt

echo ""
echo "✅ Dependencies installed successfully!"
echo ""
echo "🎉 Mkaguzi App is ready to use!"
echo ""
echo "Next steps:"
echo "1. Run 'bench migrate' to apply any database changes"
echo "2. Start the development server with 'bench start'"
echo "3. Access the application in your browser"