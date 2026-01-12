#!/bin/bash
# Force Railway edge routing refresh by triggering health checks

echo "=== FORCE RAILWAY ROUTING REFRESH ==="
echo "This will ping the health endpoint repeatedly to trigger Railway's monitoring"
echo ""

ATTEMPTS=0
MAX_ATTEMPTS=20

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    ATTEMPTS=$((ATTEMPTS + 1))
    echo "Attempt $ATTEMPTS/$MAX_ATTEMPTS: $(date +%H:%M:%S)"

    # Make health check request
    RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" https://astronumeric-backend-production.up.railway.app/health)
    HTTP_CODE=$(echo $RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ SUCCESS! Health endpoint responding with HTTP 200"
        echo ""
        echo "🎉 Railway edge routing should now be active!"
        echo "Run ./check_backend.sh to verify full functionality"
        exit 0
    else
        echo "   Still getting HTTP $HTTP_CODE (Railway fallback)"
    fi

    # Wait 15 seconds between attempts
    if [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; then
        echo "   Waiting 15 seconds before next attempt..."
        sleep 15
    fi
done

echo ""
echo "❌ Routing refresh failed after $MAX_ATTEMPTS attempts"
echo "Railway edge network may need more time to recover"
echo "Try again in 10-15 minutes, or contact Railway support"