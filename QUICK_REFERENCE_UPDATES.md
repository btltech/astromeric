# Quick Reference: New Features & Configuration

## 🌟 Weekly Vibe Scoring (Real Transits)

### Endpoint

```
POST /v2/daily-features/forecast
```

### Request

```json
{
  "profile": {
    "name": "John Doe",
    "date_of_birth": "1990-01-15",
    "time_of_birth": "14:30",
    "latitude": 40.7128,
    "longitude": -74.006,
    "timezone": "America/New_York"
  }
}
```

### Response

```json
{
  "status": "success",
  "data": {
    "days": [
      {
        "date": "2026-01-14T00:00:00",
        "score": 78,
        "vibe": "Favorable",
        "icon": "✨",
        "recommendation": "Good day for meetings"
      },
      {
        "date": "2026-01-15T00:00:00",
        "score": 42,
        "vibe": "Challenging",
        "icon": "⚡",
        "recommendation": "Reflect and plan"
      }
      // ... 5 more days
    ]
  }
}
```

### Score Ranges

- **80+**: Powerful 🌟
- **65-79**: Favorable ✨
- **50-64**: Balanced ⚖️
- **35-49**: Challenging ⚡
- **<35**: Reflective 🌙

---

## 🔐 CSP Configuration (Environment-Driven)

### How It Works

1. Default CSP is defined in `backend/app/config.py`
2. Environment variables override defaults
3. Middleware applies CSP to all responses

### Environment Variables

```bash
# Script sources
CSP_SCRIPT_SRC='self' 'unsafe-inline' 'unsafe-eval' https://analytics.example.com

# Styles
CSP_STYLE_SRC='self' 'unsafe-inline' https://fonts.googleapis.com

# Fonts
CSP_FONT_SRC='self' https://fonts.gstatic.com

# API connections (MOST IMPORTANT)
CSP_CONNECT_SRC='self' https://api.example.com https://analytics.example.com

# Images
CSP_IMG_SRC='self' data: https:
```

### Adding a New API

**Before (manual, error-prone):**

1. Edit `public/_headers`
2. Edit `backend/app/middleware/security_headers.py`
3. Deploy
4. Hope you didn't miss one

**After (automatic):**

1. Set environment variable:
   ```bash
   CSP_CONNECT_SRC='self' https://new-api.example.com
   ```
2. Restart app
3. Done! No code changes needed

### Current CSP_CONNECT_SRC Value

```
'self'
https://api.fontshare.com
https://cdn.fontshare.com
https://astromeric.com
https://www.astromeric.com
https://astronumeric.com
https://www.astronumeric.com
https://astromeric-backend-production.up.railway.app
https://nominatim.openstreetmap.org
https://api.openai.com
https://generativelanguage.googleapis.com
```

---

## 🔔 Notification Preferences

### Get User Preferences

```
GET /v2/alerts/preferences
Authorization: Bearer {token}
```

**Response:**

```json
{
  "alert_mercury_retrograde": true,
  "alert_frequency": "every_retrograde"
}
```

### Update User Preferences

```
POST /v2/alerts/preferences
Authorization: Bearer {token}
Content-Type: application/json

{
  "alert_mercury_retrograde": true,
  "alert_frequency": "weekly_digest"
}
```

### Frequency Options

| Option             | Behavior                                               |
| ------------------ | ------------------------------------------------------ |
| `every_retrograde` | Alert every time Mercury stations retrograde (4x/year) |
| `once_per_year`    | Alert only on first retrograde of the year             |
| `weekly_digest`    | Batch all retrograde alerts into weekly summary        |
| `none`             | Disable all alerts (but keep subscription active)      |

### Backend Logic

```python
# Auto-imported in alerts.py
def should_send_alert(user: User, alert_type: str) -> bool:
    # Returns True if alert should be sent
    # Checks: enabled? frequency setting? time since last alert?
    pass

# In broadcast_transit_alert():
for user in users_with_alerts_enabled:
    if should_send_alert(user):
        send_notification()
        user.last_retrograde_alert = now()  # Prevent re-alerts
```

---

## 🚀 Deployment Checklist

- [ ] Run database migration: `alembic upgrade head`
- [ ] Set CSP environment variables in Railway
- [ ] Test `/v2/daily-features/forecast` returns real scores
- [ ] Test `/v2/alerts/preferences` (authenticated)
- [ ] Check browser DevTools → no CSP violations
- [ ] Verify Mercury retrograde alerts respect frequency settings

---

## 📝 Files Changed

```
backend/app/
├── config.py (NEW) ← CSP configuration system
├── middleware/
│   └── security_headers.py ← Now uses config.py
├── models.py ← Added User.alert_* fields
├── routers/
│   ├── alerts.py ← New preferences endpoints
│   └── daily_features.py ← Real transit calculations

.env.example ← Documented CSP variables
IMPLEMENTATION_UPDATES.md ← Full documentation
```

---

## ⚡ Common Issues & Solutions

**Q: Weekly Vibe scores are all 50?**

- A: Check that `build_transit_chart()` is accessible and ephemeris files are in `/app/app/ephemeris`

**Q: CSP still has errors?**

- A: Make sure you set the environment variable without quotes around the entire value:

  ```bash
  # ✅ Correct
  CSP_CONNECT_SRC='self' https://api.example.com

  # ❌ Wrong
  CSP_CONNECT_SRC="'self' https://api.example.com"
  ```

**Q: Notification preferences aren't saving?**

- A: Ensure User model migration ran: `alembic upgrade head`

**Q: Still getting 401 on `/v2/alerts/preferences`?**

- A: That endpoint requires authentication. Pass Bearer token in Authorization header.

---

**Last Updated:** January 13, 2026  
**Status:** ✅ Ready for production
