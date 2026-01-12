#!/bin/bash
# Monitor Railway backend until it recovers

echo "=== MONITORING RAILWAY BACKEND RECOVERY ==="
echo "This will check every 5 minutes until backend is accessible"
echo "Press Ctrl+C to stop monitoring"
echo ""

ATTEMPT=1
while true; do
    echo "Attempt $ATTEMPT - $(date)"

    # Test health endpoint
    RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" https://astronumeric-backend-production.up.railway.app/health)
    HTTP_CODE=$(echo $RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

    if [ "$HTTP_CODE" = "200" ]; then
        echo "🎉 SUCCESS! Backend is now accessible!"
        echo ""
        echo "✅ Health endpoint: HTTP 200"
        echo "✅ Railway edge routing recovered"
        echo ""
        echo "Your app URLs:"
        echo "  Frontend: https://82ed7ad6.astromeric.pages.dev"
        echo "  Backend:  https://astronumeric-backend-production.up.railway.app"
        echo ""
        echo "🚀 Ready for production!"
        exit 0
    else
        echo "   ❌ Still failing (HTTP $HTTP_CODE)"
        echo "   Railway edge network not routing yet"
    fi

    echo "   Waiting 5 minutes before next check..."
    echo ""
    sleep 300
    ATTEMPT=$((ATTEMPT + 1))
done