#!/bin/bash
# Setup Script for API Keys (Environment Variables)
# Run this script to configure your API credentials

echo "=================================================="
echo "🔑 API Keys Setup - Phase 2 Integrations"
echo "=================================================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "❌ Setup cancelled. Edit .env manually."
        exit 0
    fi
fi

# Copy example
cp .env.example .env
echo "✅ Created .env file from template"
echo ""

# Interactive setup
echo "Let's configure your API keys..."
echo ""

# Reddit
echo "1️⃣  REDDIT API"
echo "   Get credentials: https://www.reddit.com/prefs/apps"
read -p "   Reddit Client ID: " reddit_id
read -p "   Reddit Client Secret: " reddit_secret

# X (Twitter)
echo ""
echo "2️⃣  X (TWITTER) API"
echo "   Get credentials: https://developer.twitter.com/"
read -p "   X Bearer Token: " x_token

# Update .env file
echo ""
echo "💾 Saving credentials to .env..."

# Use sed to replace values
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/REDDIT_CLIENT_ID=.*/REDDIT_CLIENT_ID=$reddit_id/" .env
    sed -i '' "s/REDDIT_CLIENT_SECRET=.*/REDDIT_CLIENT_SECRET=$reddit_secret/" .env
    sed -i '' "s/X_BEARER_TOKEN=.*/X_BEARER_TOKEN=$x_token/" .env
else
    # Linux
    sed -i "s/REDDIT_CLIENT_ID=.*/REDDIT_CLIENT_ID=$reddit_id/" .env
    sed -i "s/REDDIT_CLIENT_SECRET=.*/REDDIT_CLIENT_SECRET=$reddit_secret/" .env
    sed -i "s/X_BEARER_TOKEN=.*/X_BEARER_TOKEN=$x_token/" .env
fi

echo "✅ Credentials saved!"
echo ""

# Load environment variables
echo "=================================================="
echo "🚀 Setup Complete!"
echo "=================================================="
echo ""
echo "To use your API keys, run:"
echo ""
echo "  source .env              # Load variables in current shell"
echo "  export \$(cat .env | xargs)  # Alternative method"
echo ""
echo "Or use python-dotenv (already installed):"
echo "  from dotenv import load_dotenv"
echo "  load_dotenv()"
echo ""
echo "Test with:"
echo "  python test_phase2.py"
echo ""
echo "=================================================="
