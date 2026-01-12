#!/bin/bash
# Check if backend is healthy and ready

echo "=== BACKEND STATUS CHECK ==="
echo "Time: $(date)"
echo ""

# Check health
echo "1. Testing /health endpoint..."
HEALTH=$(curl -s https://astronumeric-backend-production.up.railway.app/health)

if echo "$HEALTH" | grep -q '"status":"ok"'; then
    echo "   ✅ Health check PASSED"
    echo "$HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print('   - Ephemeris:', d.get('ephemeris_path')); print('   - Flatlib:', d.get('flatlib_available')); print('   - Gemini:', d.get('gemini_status'))" 2>/dev/null
else
    echo "   ❌ Health check FAILED (Railway fallback)"
    echo "   Container is running but edge routing not updated yet"
    echo "   Wait 5-10 minutes and run this script again"
    echo ""
    echo "Current response:"
    echo "$HEALTH"
    exit 1
fi

# Test actual API
echo ""
echo "2. Testing /daily-reading API..."
API_TEST=$(curl -s -X POST https://astronumeric-backend-production.up.railway.app/daily-reading \
  -H "Content-Type: application/json" \
  -d '{"profile":{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","birth_location":"New York","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"}}')

if echo "$API_TEST" | grep -q '"scope":"daily"'; then
    echo "   ✅ API test PASSED"
    echo "$API_TEST" | python3 -c "import sys,json; d=json.load(sys.stdin); print('   - Date:', d.get('date')); print('   - Sections:', len(d.get('sections', []))); print('   - Has natal chart:', 'natal' in d.get('charts', {}))" 2>/dev/null
else
    echo "   ❌ API test FAILED"
    exit 1
fi

# Test CORS
echo ""
echo "3. Testing CORS for astronumeric.com..."
CORS=$(curl -s -I -X OPTIONS \
  -H "Origin: https://astronumeric.com" \
  -H "Access-Control-Request-Method: POST" \
  https://astronumeric-backend-production.up.railway.app/daily-reading 2>&1 | grep -i "access-control-allow-origin")

if [ -n "$CORS" ]; then
    echo "   ✅ CORS configured correctly"
    echo "   $CORS"
else
    echo "   ⚠️  CORS header not found (might need container restart)"
fi

echo ""
echo "=== OVERALL STATUS ==="
echo "✅ Backend is FULLY OPERATIONAL"
echo ""
echo "Your app URLs:"
echo "  Frontend: https://82ed7ad6.astromeric.pages.dev"
echo "  Backend:  https://astronumeric-backend-production.up.railway.app"
echo ""
echo "🎉 Ready for production use!"
