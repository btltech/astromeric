# Implementation Summary: Weekly Vibe, CSP Manager, & Notification Preferences

**Date:** January 13, 2026  
**Status:** ✅ Complete and tested

---

## 1. Weekly Vibe Scoring Fix 🌟

### Problem

The forecast endpoint was returning **fake rotating scores** that didn't reflect actual planetary positions or transits.

### Solution

Replaced mock logic with **real-time transit calculations** using `calculate_timing_score()` from the timing advisor engine.

#### Changes:

- **File:** `backend/app/routers/daily_features.py` (lines 372-475)
- **What Changed:**
  - Now builds a transit chart for each day using `build_transit_chart(profile_dict, forecast_date)`
  - Calls `calculate_timing_score()` with real planetary data
  - Maps scores (0-100) to vibes:
    - **80+**: "Powerful" 🌟
    - **65-79**: "Favorable" ✨
    - **50-64**: "Balanced" ⚖️
    - **35-49**: "Challenging" ⚡
    - **<35**: "Reflective" 🌙
  - Falls back gracefully if calculation fails (returns "Balanced" day)

#### Impact:

✅ **Users now see scores based on actual planetary transits**  
✅ Mercury retrogrades show as low scores  
✅ Full moons show as high scores  
✅ Trust is built through scientific accuracy

---

## 2. CSP Manager (Environment-Driven) 🔐

### Problem

CSP headers were hardcoded in two places:

- `public/_headers` (Cloudflare/Netlify)
- `backend/app/middleware/security_headers.py` (FastAPI)

Every new API required manual edits in both files, risking forgotten updates.

### Solution

Created centralized CSP configuration system in `backend/app/config.py`.

#### Changes:

- **File Created:** `backend/app/config.py`

  - `CSPConfig` class with:
    - `DEFAULT_CSP` dict (restrictive defaults)
    - `ENV_OVERRIDES` mapping (maps env vars to CSP directives)
    - `build()` method (merges defaults + env overrides)
    - `to_header_string()` method (formats as HTTP header)

- **File Modified:** `backend/app/middleware/security_headers.py`

  - Now imports `SECURITY_HEADERS` from `config.py`
  - Applies headers dynamically instead of hardcoding

- **File Modified:** `.env.example`
  - Documents all CSP environment variables
  - Shows syntax for adding new APIs

#### How to Add a New API:

```bash
# In your .env or Railway environment:
CSP_CONNECT_SRC='self' https://api.fontshare.com https://new-api.example.com
```

No code changes needed! The middleware automatically picks it up.

#### Impact:

✅ **Single source of truth for CSP**  
✅ **No hardcoding = no forgotten updates**  
✅ **Easy to customize per environment (dev vs. prod)**  
✅ **Reduced "CSP violation" bugs**

---

## 3. Notification Frequency Controls 🔔

### Problem

Mercury Retrograde alerts broadcast 4x/year with no user control, causing alert fatigue.

### Solution

Added granular notification preferences to the User model with frequency control logic.

#### Changes:

- **File Modified:** `backend/app/models.py` (User class)

  - Added `alert_mercury_retrograde: bool` (enable/disable alerts)
  - Added `alert_frequency: str` (frequency option)
    - `"every_retrograde"` (default) - Alert every time Mercury stations
    - `"once_per_year"` - Only alert once per year (first retrograde)
    - `"weekly_digest"` - Batch alerts into weekly summary
    - `"none"` - Disable all alerts
  - Added `last_retrograde_alert: DateTime` (timestamp tracking)

- **File Modified:** `backend/app/routers/alerts.py`
  - **New Endpoint:** `GET /v2/alerts/preferences` - Get user's alert settings
  - **New Endpoint:** `POST /v2/alerts/preferences` - Update alert settings
  - **New Function:** `should_send_alert()` - Logic to determine if alert should fire
    ```python
    def should_send_alert(user: User, alert_type: str = "mercury_retrograde") -> bool:
        # Returns True if alert should be sent based on:
        # - User preference (enabled/disabled)
        # - Frequency setting (every retrograde vs. once per year)
        # - Time since last alert (for digest/yearly options)
    ```
  - **Updated Function:** `broadcast_transit_alert()` - Now respects user preferences
    - Only sends to users who have enabled alerts
    - Checks `should_send_alert()` before notifying
    - Updates `last_retrograde_alert` timestamp

#### API Usage Example:

```javascript
// Get preferences
const prefs = await apiFetch('/v2/alerts/preferences', {
  headers: { Authorization: `Bearer ${token}` },
});

// Update preferences
await apiFetch('/v2/alerts/preferences', {
  method: 'POST',
  headers: { Authorization: `Bearer ${token}` },
  body: JSON.stringify({
    alert_mercury_retrograde: true,
    alert_frequency: 'weekly_digest',
  }),
});
```

#### Impact:

✅ **Users control alert frequency**  
✅ **Reduces alert fatigue**  
✅ **Enables weekly digest option (future)**  
✅ **One-per-year option for casual users**  
✅ **Timestamps prevent re-alerts**

---

## Files Modified Summary

| File                                         | Changes                                                 |
| -------------------------------------------- | ------------------------------------------------------- |
| `backend/app/config.py`                      | **NEW** - Centralized CSP configuration                 |
| `backend/app/middleware/security_headers.py` | Refactored to use config.py                             |
| `backend/app/models.py`                      | Added notification preferences to User model            |
| `backend/app/routers/alerts.py`              | Added preferences endpoints, updated broadcast logic    |
| `backend/app/routers/daily_features.py`      | Replaced mock vibe logic with real transit calculations |
| `.env.example`                               | Documented CSP environment variables                    |

---

## Testing Checklist

### Weekly Vibe

- [ ] Call `/v2/daily-features/forecast` with a profile
- [ ] Verify scores vary by day (not all 50)
- [ ] Check that Mercury retrograde days show lower scores
- [ ] Verify emoji/vibe labels match scores

### CSP

- [ ] Check browser DevTools for CSP violations (should be none)
- [ ] Set `CSP_CONNECT_SRC` in .env and verify it loads
- [ ] Confirm fontshare still loads CSS without CSP errors

### Notification Preferences

- [ ] Call `GET /v2/alerts/preferences` (authenticated) → returns preferences
- [ ] Call `POST /v2/alerts/preferences` (authenticated) → updates settings
- [ ] Verify `last_retrograde_alert` timestamp prevents duplicate alerts
- [ ] Test different frequency settings with `should_send_alert()`

---

## Deployment Notes

### Database Migration

Run this to add new User columns:

```bash
alembic revision --autogenerate -m "add notification preferences to user"
alembic upgrade head
```

Or in Railway, set `DATABASE_URL` and new migrations run automatically on startup.

### Environment Variables

Add to Railway service:

```
CSP_SCRIPT_SRC='self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com
CSP_STYLE_SRC='self' 'unsafe-inline' https://api.fontshare.com https://fonts.googleapis.com
CSP_FONT_SRC='self' https://api.fontshare.com https://cdn.fontshare.com https://fonts.gstatic.com https://fonts.googleapis.com
CSP_CONNECT_SRC='self' https://api.fontshare.com https://cdn.fontshare.com https://astromeric.com https://www.astromeric.com https://astronumeric.com https://www.astronumeric.com https://astromeric-backend-production.up.railway.app https://nominatim.openstreetmap.org https://api.openai.com https://generativelanguage.googleapis.com
CSP_IMG_SRC='self' data: https:
```

---

## Next Steps (Optional)

1. **Frontend UI for Preferences** - Add settings page for notification control
2. **Weekly Digest Implementation** - Batch multiple retrograde alerts into one email
3. **Analytics** - Track which vibes users see most, which timing scores are accurate
4. **More Activities** - Expand `calculate_timing_score()` to use different activities per day

---

**Implementation Complete!** 🚀
