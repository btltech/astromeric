#!/bin/bash
# Check if backend is healthy and ready

echo "=== BACKEND STATUS CHECK ==="
echo "Time: $(date)"
echo ""

# Check health
echo "1. Testing /health endpoint..."
HEALTH=$(curl -s https://astromeric-backend-production.up.railway.app/health)

if echo "$HEALTH" | grep -q '"status":"ok"'; then
    echo "   ✅ Health check PASSED"
    echo "$HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print('   - Ephemeris:', d.get('ephemeris_path')); print('   - Gemini AI:', 'active' if d.get('features', {}).get('cosmic_guide') else 'inactive')" 2>/dev/null
else
    echo "   ❌ Health check FAILED (Railway fallback)"
    echo "   Container is running but edge routing not updated yet"
    echo "   Wait 5-10 minutes and run this script again"
    echo ""
    echo "Current response:"
    echo "$HEALTH"
    exit 1
fi

# Test actual API (v2 daily features)
echo ""
echo "2. Testing /v2/daily/reading API..."
API_TEST=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/daily/reading \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","place_of_birth":"New York","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York","house_system":"Placidus"}')

if echo "$API_TEST" | grep -q '"status":"success"'; then
    echo "   ✅ API test PASSED"
    echo "$API_TEST" | python3 -c "import sys,json; d=json.load(sys.stdin); data=d.get('data',{}); print('   - Has affirmation:', bool(data.get('affirmation'))); print('   - Lucky numbers:', data.get('lucky_numbers'))" 2>/dev/null
else
    echo "   ❌ API test FAILED"
    echo "$API_TEST" | head -c 300
    echo ""
    exit 1
fi

# Test v2 forecast date handling (regression guard)
echo ""
echo "2b. Testing /v2/forecasts/daily date handling..."
V2_A=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/forecasts/daily \
  -H "Content-Type: application/json" \
  -d '{"profile":{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"},"scope":"daily","date":"2000-01-01","include_details":true}')
V2_B=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/forecasts/daily \
  -H "Content-Type: application/json" \
  -d '{"profile":{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"},"scope":"daily","date":"2099-12-31","include_details":true}')

if echo "$V2_A" | grep -q '"status":"success"' && echo "$V2_B" | grep -q '"status":"success"'; then
    SAME=$(python3 - "$V2_A" "$V2_B" <<'PY'
import json
import sys

a = json.loads(sys.argv[1])
b = json.loads(sys.argv[2])
print("same" if a.get("data", {}).get("sections") == b.get("data", {}).get("sections") else "diff")
PY
)
    if [ "$SAME" = "diff" ]; then
        echo "   ✅ v2 forecast date impacts output"
    else
        echo "   ❌ v2 forecast output identical across dates (date may be ignored)"
        exit 1
    fi
else
    echo "   ❌ v2 forecast test failed"
    exit 1
fi

# Test v2 natal profile endpoint (regression guard)
echo ""
echo "2c. Testing /v2/profiles/natal..."
V2_NATAL=$(curl -s -o /tmp/v2_natal.json -w "%{http_code}" -X POST https://astromeric-backend-production.up.railway.app/v2/profiles/natal \
  -H "Content-Type: application/json" \
  -d '{"profile":{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"},"include_asteroids":false,"include_aspects":true,"orb":8.0}')

if [ "$V2_NATAL" = "200" ]; then
    echo "   ✅ v2 natal profile operational"
else
    echo "   ❌ v2 natal profile failed (HTTP $V2_NATAL)"
    cat /tmp/v2_natal.json || true
    exit 1
fi

# Test v2 daily tarot endpoint
echo ""
echo "2d. Testing /v2/daily/tarot..."
V2_TAROT=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/daily/tarot)

if echo "$V2_TAROT" | grep -q '"status":"success"'; then
    echo "   ✅ v2 daily tarot operational"
else
    echo "   ❌ v2 daily tarot failed"
    echo "$V2_TAROT" | head -c 300
    echo ""
    exit 1
fi

# Test v2 numerology endpoints (profile + compatibility)
echo ""
echo "2e. Testing /v2/numerology/profile..."
V2_NUMEROLOGY=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/numerology/profile \
  -H "Content-Type: application/json" \
  -d '{"profile":{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"},"language":"en"}')

if echo "$V2_NUMEROLOGY" | grep -q '"status":"success"'; then
    echo "   ✅ v2 numerology profile operational"
else
    echo "   ❌ v2 numerology profile failed"
    echo "$V2_NUMEROLOGY" | head -c 300
    echo ""
    exit 1
fi

echo ""
echo "2f. Testing /v2/numerology/compatibility..."
V2_NUM_COMP=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/numerology/compatibility \
  -H "Content-Type: application/json" \
  -d '{"profile":{"name":"Alice","date_of_birth":"1992-05-15","time_of_birth":"08:30:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"},"person_b":{"name":"Bob","date_of_birth":"1990-08-20","time_of_birth":"11:00:00","latitude":34.0522,"longitude":-118.2437,"timezone":"America/Los_Angeles"},"language":"en"}')

if echo "$V2_NUM_COMP" | grep -q '"status":"success"'; then
    echo "   ✅ v2 numerology compatibility operational"
else
    echo "   ❌ v2 numerology compatibility failed"
    echo "$V2_NUM_COMP" | head -c 300
    echo ""
    exit 1
fi

# Test v2 year-ahead forecast
echo ""
echo "2g. Testing /v2/year-ahead/forecast..."
V2_YEAR_AHEAD=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/year-ahead/forecast \
  -H "Content-Type: application/json" \
  -d '{"profile":{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"},"year":2026}')

if echo "$V2_YEAR_AHEAD" | grep -q '"status":"success"'; then
    echo "   ✅ v2 year-ahead forecast operational"
else
    echo "   ❌ v2 year-ahead forecast failed"
    echo "$V2_YEAR_AHEAD" | head -c 300
    echo ""
    exit 1
fi

# Test v2 timing endpoints
echo ""
echo "2h. Testing /v2/timing/activities..."
V2_TIMING_ACTIVITIES=$(curl -s https://astromeric-backend-production.up.railway.app/v2/timing/activities)

if echo "$V2_TIMING_ACTIVITIES" | grep -q '"status":"success"'; then
    echo "   ✅ v2 timing activities operational"
else
    echo "   ❌ v2 timing activities failed"
    echo "$V2_TIMING_ACTIVITIES" | head -c 300
    echo ""
    exit 1
fi

echo ""
echo "2i. Testing /v2/timing/advice..."
V2_TIMING_ADVICE=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/timing/advice \
  -H "Content-Type: application/json" \
  -d '{"activity":"creative_work","profile":{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"}}')

if echo "$V2_TIMING_ADVICE" | grep -q '"status":"success"'; then
    echo "   ✅ v2 timing advice operational"
else
    echo "   ❌ v2 timing advice failed"
    echo "$V2_TIMING_ADVICE" | head -c 300
    echo ""
    exit 1
fi

# Test v2 moon endpoints
echo ""
echo "2j. Testing /v2/moon/phase..."
V2_MOON_PHASE=$(curl -s https://astromeric-backend-production.up.railway.app/v2/moon/phase)
if echo "$V2_MOON_PHASE" | grep -q '"status":"success"'; then
    echo "   ✅ v2 moon phase operational"
else
    echo "   ❌ v2 moon phase failed"
    echo "$V2_MOON_PHASE" | head -c 300
    echo ""
    exit 1
fi

echo ""
echo "2k. Testing /v2/moon/ritual..."
V2_MOON_RITUAL=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/moon/ritual \
  -H "Content-Type: application/json" \
  -d '{"profile":{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"}}')
if echo "$V2_MOON_RITUAL" | grep -q '"status":"success"'; then
    echo "   ✅ v2 moon ritual operational"
else
    echo "   ❌ v2 moon ritual failed"
    echo "$V2_MOON_RITUAL" | head -c 300
    echo ""
    exit 1
fi

# Test v2 charts endpoints
echo ""
echo "2l. Testing /v2/charts/progressed..."
V2_PROGRESSED=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/charts/progressed \
  -H "Content-Type: application/json" \
  -d '{"profile":{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"},"target_date":"2026-02-04"}')
if echo "$V2_PROGRESSED" | grep -q '"status":"success"'; then
    echo "   ✅ v2 progressed chart operational"
else
    echo "   ❌ v2 progressed chart failed"
    echo "$V2_PROGRESSED" | head -c 300
    echo ""
    exit 1
fi

echo ""
echo "2m. Testing /v2/charts/synastry..."
V2_SYNASTRY=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/charts/synastry \
  -H "Content-Type: application/json" \
  -d '{"person_a":{"name":"Alice","date_of_birth":"1992-05-15","time_of_birth":"08:30:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"},"person_b":{"name":"Bob","date_of_birth":"1990-08-20","time_of_birth":"11:00:00","latitude":34.0522,"longitude":-118.2437,"timezone":"America/Los_Angeles"}}')
if echo "$V2_SYNASTRY" | grep -q '"status":"success"'; then
    echo "   ✅ v2 synastry chart operational"
else
    echo "   ❌ v2 synastry chart failed"
    echo "$V2_SYNASTRY" | head -c 300
    echo ""
    exit 1
fi

echo ""
echo "2n. Testing /v2/charts/composite..."
V2_COMPOSITE=$(curl -s -X POST https://astromeric-backend-production.up.railway.app/v2/charts/composite \
  -H "Content-Type: application/json" \
  -d '{"person_a":{"name":"Alice","date_of_birth":"1992-05-15","time_of_birth":"08:30:00","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"},"person_b":{"name":"Bob","date_of_birth":"1990-08-20","time_of_birth":"11:00:00","latitude":34.0522,"longitude":-118.2437,"timezone":"America/Los_Angeles"}}')
if echo "$V2_COMPOSITE" | grep -q '"status":"success"'; then
    echo "   ✅ v2 composite chart operational"
else
    echo "   ❌ v2 composite chart failed"
    echo "$V2_COMPOSITE" | head -c 300
    echo ""
    exit 1
fi

# Test daily affirmation + oracle (yes/no)
echo ""
echo "2o. Testing /v2/daily/affirmation..."
V2_AFFIRMATION=$(curl -s https://astromeric-backend-production.up.railway.app/v2/daily/affirmation)
if echo "$V2_AFFIRMATION" | grep -q '"status":"success"'; then
    echo "   ✅ v2 daily affirmation operational"
else
    echo "   ❌ v2 daily affirmation failed"
    echo "$V2_AFFIRMATION" | head -c 300
    echo ""
    exit 1
fi

echo ""
echo "2p. Testing /v2/daily/yes-no..."
V2_YESNO=$(curl -s -X POST "https://astromeric-backend-production.up.railway.app/v2/daily/yes-no?question=Should%20I%20travel%20today%3F" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","date_of_birth":"1990-06-15","time_of_birth":"12:00:00","place_of_birth":"New York","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York","house_system":"Placidus"}')
if echo "$V2_YESNO" | grep -q '"status":"success"'; then
    echo "   ✅ v2 oracle yes/no operational"
else
    echo "   ❌ v2 oracle yes/no failed"
    echo "$V2_YESNO" | head -c 300
    echo ""
    exit 1
fi

# Test habits list (read-only)
echo ""
echo "2q. Testing /v2/habits/list..."
V2_HABITS=$(curl -s https://astromeric-backend-production.up.railway.app/v2/habits/list)
if echo "$V2_HABITS" | grep -q '"status":"success"'; then
    echo "   ✅ v2 habits list operational"
else
    echo "   ❌ v2 habits list failed"
    echo "$V2_HABITS" | head -c 300
    echo ""
    exit 1
fi

# Test CORS
echo ""
echo "3. Testing CORS for astronumeric.com..."
CORS=$(curl -s -I -X OPTIONS \
  -H "Origin: https://astronumeric.com" \
  -H "Access-Control-Request-Method: POST" \
  https://astromeric-backend-production.up.railway.app/v2/daily/reading 2>&1 | grep -i "access-control-allow-origin")

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
echo "  Backend:  https://astromeric-backend-production.up.railway.app"
echo ""
echo "🎉 Ready for production use!"
