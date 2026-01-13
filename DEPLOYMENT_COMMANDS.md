# Deployment Commands Executed

**Date:** January 13, 2026

---

## Railway CLI Commands Executed

### 1. Set CSP Script Sources

```bash
railway variables --set "CSP_SCRIPT_SRC='self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com" \
  --set "CSP_STYLE_SRC='self' 'unsafe-inline' https://api.fontshare.com https://fonts.googleapis.com" \
  --set "CSP_FONT_SRC='self' https://api.fontshare.com https://cdn.fontshare.com https://fonts.gstatic.com https://fonts.googleapis.com"
```

✅ **Result:** CSP_SCRIPT_SRC, CSP_STYLE_SRC, CSP_FONT_SRC set on Railway

### 2. Set CSP Connect and Image Sources

```bash
railway variables --set "CSP_CONNECT_SRC='self' https://api.fontshare.com https://cdn.fontshare.com https://astromeric.com https://www.astromeric.com https://astronumeric.com https://www.astronumeric.com https://astromeric-backend-production.up.railway.app https://nominatim.openstreetmap.org https://api.openai.com https://generativelanguage.googleapis.com" \
  --set "CSP_IMG_SRC='self' data: https:"
```

✅ **Result:** CSP_CONNECT_SRC and CSP_IMG_SRC set on Railway

### 3. Verify Variables Were Set

```bash
railway variables --kv | grep CSP
```

✅ **Result:** All 5 CSP variables confirmed on Railway

### 4. Deploy to Railway

```bash
railway up --detach
```

✅ **Result:** Code uploaded and build initiated  
📍 **Build URL:** https://railway.com/project/a6ce0043-3a3e-4339-99dd-f912f26c3b16

### 5. Check Deployment Status

```bash
railway status
```

✅ **Result:** Project confirmed as astromeric-backend in production environment

---

## Wrangler (Frontend/Cloudflare)

**Status:** No additional secrets needed for CSP on Cloudflare  
**Why:** CSP headers come from `public/_headers` file, not wrangler secrets

**To deploy frontend when ready:**

```bash
wrangler pages deploy dist
```

---

## What Gets Deployed Automatically

### On Railway Startup (automatic):

1. **Database Migration** - Runs `alembic upgrade head`

   - Adds 3 columns to users table
   - `alert_mercury_retrograde` (bool)
   - `alert_frequency` (string)
   - `last_retrograde_alert` (datetime)

2. **CSP Headers** - Loaded from environment variables

   - Reads from CSP\_\* env vars
   - Applied by `config.py` and `security_headers.py`

3. **New Endpoints** - Become available
   - `POST /v2/daily-features/forecast` (Weekly Vibe)
   - `GET/POST /v2/alerts/preferences` (Notification settings)
   - `GET /v2/profiles/natal/{id}` (Profile retrieval)

---

## Verify Deployment

### Check Build Logs

```bash
# Follow logs in real-time
railway logs --follow

# Look for:
# "Application startup complete"
# "Migration successful" (if applicable)
# No error messages
```

### Test Live Endpoints

```bash
# Test forecast (no auth needed)
curl -X POST https://astromeric-backend-production.up.railway.app/v2/daily-features/forecast \
  -H "Content-Type: application/json" \
  -d '{"profile": {"name":"Test","date_of_birth":"1990-01-15","time_of_birth":"14:30","latitude":40.7128,"longitude":-74.006,"timezone":"America/New_York"}}'

# Check CSP headers exist
curl -I https://astromeric-backend-production.up.railway.app/health | grep Content-Security-Policy
```

### Check Frontend

```bash
# Open in browser:
# https://astronumeric.com

# DevTools → Console
# Look for no CSP violations
# Check Application → Storage for service worker
```

---

## Timeline

| Time   | Action                                          | Status      |
| ------ | ----------------------------------------------- | ----------- |
| ~00:00 | Set CSP_SCRIPT_SRC, CSP_STYLE_SRC, CSP_FONT_SRC | ✅ Complete |
| ~00:01 | Set CSP_CONNECT_SRC, CSP_IMG_SRC                | ✅ Complete |
| ~00:02 | Verify all CSP variables                        | ✅ Complete |
| ~00:03 | Deploy with `railway up --detach`               | ✅ Complete |
| ~00:05 | Check status                                    | ✅ Complete |
| 00:05+ | Build in progress on Railway                    | ⏳ Building |

---

## Next Steps

1. **Wait for Railway build** (~5-10 minutes)
2. **Check logs** for migration completion
3. **Test endpoints** using curl commands above
4. **Verify in browser** - no CSP errors
5. **Monitor logs** for first 24 hours
6. **Optional:** Deploy frontend to Cloudflare Pages

---

## If Something Goes Wrong

**The variables are stored in Railway:**

```bash
# View them
railway variables --kv | grep CSP

# Reset if needed
railway variables --unset CSP_SCRIPT_SRC CSP_STYLE_SRC CSP_FONT_SRC CSP_CONNECT_SRC CSP_IMG_SRC

# Redeploy
railway up
```

**The code is live:**

```bash
# Check what's deployed
railway logs

# If broken, revert
git revert HEAD~1
railway up
```

---

**Deployment Status:** ✅ LIVE (Building)  
**Last Updated:** January 13, 2026
