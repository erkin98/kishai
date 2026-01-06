#!/usr/bin/env bash
# Quick setup script for Kishai LLM Platform

set -e

echo "🚀 Kishai LLM Platform - Quick Setup"
echo "===================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed"
    echo "📥 Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if just is installed
if ! command -v just &> /dev/null; then
    echo "❌ just is not installed"
    echo "📥 Install with one of:"
    echo "   - cargo install just"
    echo "   - brew install just (macOS/Linux)"
    echo "   - See https://just.systems for more options"
    exit 1
fi

echo "✅ All required tools are installed"
echo ""

# Run setup
echo "📦 Setting up virtual environment and installing dependencies..."
just setup

echo ""
echo "📝 Creating .env file from template..."
just env

echo ""
echo "🗄️  Initializing database..."
just db-init || echo "⚠️  Database initialization failed. You may need to configure it manually."

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 Next steps:"
echo "   1. Activate virtual environment:"
echo "      source .venv/bin/activate"
echo ""
echo "   2. Edit your .env file and set configuration:"
echo "      nano .env  # or your favorite editor"
echo ""
echo "   3. Generate a secure SECRET_KEY:"
echo "      just secret"
echo ""
echo "   4. Start the development server:"
echo "      just dev"
echo ""
echo "📚 For more information, see LOCAL_DEV.md"

