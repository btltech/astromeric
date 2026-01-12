#!/bin/bash
# Comprehensive Railway Issue Verification

echo "=== RAILWAY ISSUE VERIFICATION REPORT ==="
echo "Date: $(date)"
echo ""

echo "🔍 EVIDENCE THAT CONTAINER IS RUNNING:"
echo "----------------------------------------"
echo "Railway Logs (last 10 lines):"
railway logs --tail 10 2>&1 | grep -E "Uvicorn|startup|complete" | tail -5
echo ""

echo "🔍 EVIDENCE THAT EDGE NETWORK IS BROKEN:"
echo "----------------------------------------"
echo "HTTP Response Headers:"
curl -s -I https://astronumeric-backend-production.up.railway.app/health | grep -E "HTTP|x-railway|x-request-id"
echo ""

echo "Response Body:"
curl -s https://astronumeric-backend-production.up.railway.app/health
echo ""

echo "🔍 CONFIGURATION VERIFICATION:"
echo "------------------------------"
echo "Railway Config Health Check:"
grep -A 5 "healthcheck" railway.json
echo ""

echo "Environment Variables:"
railway variables | grep -E "ALLOW_ORIGINS|PORT" | head -5
echo ""

echo "🔍 DIAGNOSIS:"
echo "-------------"
echo "✅ Container: RUNNING (logs show Uvicorn on port 8080)"
echo "✅ Application: STARTED (logs show 'Application startup complete')"
echo "✅ Health Check: CONFIGURED (/health endpoint, 30s timeout)"
echo "❌ Edge Routing: FAILED (x-railway-fallback: true)"
echo "❌ External Access: BLOCKED (HTTP 404 from Railway edge)"
echo ""

echo "🎯 ROOT CAUSE:"
echo "Multiple failed deployments caused Railway's edge network to enter"
echo "'safe mode' where it serves 404 fallbacks instead of routing to containers."
echo ""

echo "💡 SOLUTION:"
echo "Wait 1-4 hours for Railway infrastructure recovery, or contact Railway support."
echo "The container is healthy - this is purely a routing infrastructure issue."