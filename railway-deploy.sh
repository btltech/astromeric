#!/bin/bash
# railway-deploy.sh - Deploy script for Railway CLI

set -e

echo "🚀 Deploying AstroNumerology to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install from: https://docs.railway.app/cli/install"
    exit 1
fi

# Initialize project
echo "📦 Initializing Railway project..."
railway init --name astromeric-backend || true

# Build and deploy
echo "🏗️ Building and deploying..."
railway up

# Get the deployed URL
echo ""
echo "✅ Deployment complete!"
echo "Getting service URL..."
railway status

echo ""
echo "📝 Next steps:"
echo "1. Copy the service URL from above"
echo "2. Set ALLOW_ORIGINS in Railway dashboard to your frontend domain"
echo "3. Use the URL as VITE_API_URL in your frontend"
