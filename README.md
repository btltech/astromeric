# AstroNumerology – One-Stop Astrology + Numerology Platform
[View on GitHub](https://github.com/btltech/astromeric)


## Quick Start
- **Run Locally**: Backend: `cd /path/to/project && python -m uvicorn backend.app.main:app --reload`. Frontend: `npm run dev`. Open http://localhost:3000.
- **Deploy**: Push to GitHub, deploy backend to Railway, frontend to Netlify/Vercel with `VITE_API_URL` set to Railway URL.

Production-oriented stack that pairs a FastAPI engine (Railway) with a Vite + React + three.js frontend.

## Features

### Core Features
- **Daily/Weekly/Monthly Readings**: Get personalized horoscopes for different time scopes
- **5 Life Tracks**: General, Love, Money, Health, and Spiritual readings with ratings
- **TL;DR Summaries**: Quick overview of your day/week/month
- **Affirmations & Daily Actions**: Personalized affirmations and suggested activities
- **Multi-Profile Support**: Save multiple profiles for yourself, friends, or family
- **Reading History**: Access your past readings with date stamps
- **Favorites**: Save your favorite readings for quick access

### Extended Numerology
- **Expression Number**: Your natural talents and how you express yourself
- **Soul Urge Number**: Your heart's deepest desires
- **Personality Number**: How others perceive you
- **Maturity Number**: Your true self that emerges after 40-50
- **Personal Year/Month/Day**: Current cycle energies
- **Pinnacles & Challenges**: Life's major turning points and lessons

### Compatibility Tools
- **Astrology Compatibility**: Compare zodiac signs, elements, and modalities
- **Numerology Compatibility**: Life path and expression number comparisons
- **Combined Compatibility**: Full relationship analysis with scores and advice

### Learning Center
- **Zodiac Glossary**: Detailed info on all 12 signs
- **Numerology Glossary**: Explanations of all number meanings
- **Search**: Find specific terms and concepts

## Architecture
- Browser (Vite/React) → REST API → FastAPI on Railway.
- SQLite database for profiles, readings, favorites, and preferences.
- Optional Redis for caching and rate limiting.
- Engine v2: `engine/charts/*` (ephemeris wrapper), `engine/interpretation/*` (meaning blocks), `engine/rules/*` (scoring), `engine/products/*` (natal/forecast/compatibility). Library swap is isolated to `ChartEngine`; interpretation/rules stay stable.
- Legacy daily fusion: `engine/fusion.py` remains for backward compatibility; `/reading` now also returns `engine_v2` forecast output.
- Determinism: seed = `name + dob + date + scope + time_of_birth + place_of_birth` → stable results per user/day (stub ephemeris hashes inputs when flatlib/Swiss ephemeris isn’t available).

## Backend (FastAPI)
- Location: `backend/app`.
- Files:
  - `main.py`: FastAPI app, CORS, all API endpoints.
  - `models.py`: SQLAlchemy models (Profile, Reading, Favourite, Preference).
  - `engine/astrology.py`: sign calculation, element map, per-sign trait pools.
  - `engine/numerology.py`: life path + name number (Pythagorean), meanings/advice.
  - `engine/numerology_extended.py`: expression, soul urge, personality, maturity, cycles, pinnacles, challenges.
  - `engine/compatibility.py`: astrology and numerology compatibility calculations.
  - `engine/glossary.py`: zodiac and numerology educational content.
  - `engine/fusion.py`: deterministic text/rating/lucky/theme generation.
  - `Procfile`: Railway start command.
  - `requirements.txt`: dependencies.

### Run Backend Locally
```bash
cd /path/to/project
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
# health: curl http://localhost:8000/health
```

### Deploy to Railway
1. Push repo to GitHub.
2. Create new Railway service → Deploy from repo.
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
4. Env (optional): `REDIS_URL` for caching; `APP_TZ` for timezone; `LOG_LEVEL` for verbosity; `RATE_LIMIT_PER_MIN` for rate limiting. For tighter CORS in production set `ALLOW_ORIGINS` to a comma-separated list of allowed origins (e.g., `https://your-frontend.com`).
5. Grab the public URL.

## Frontend (Vite + React + drei)
- Key files:
  - `index.tsx`: Main UI with profiles, readings, numerology, compatibility, and learning views.
  - `styles.css`: Comprehensive styling.
  - `vite.config.ts`: Dev server + alias.
  - `.env.example`: `VITE_API_URL` placeholder.

### Run Frontend Locally
```bash
npm install
VITE_API_URL=http://localhost:8000 npm run dev
# open http://localhost:3000
```

### Build for Production
```bash
VITE_API_URL=https://your-app.up.railway.app npm run build
# deploy ./dist to your static host
```

## API Endpoints

### Profiles
- `POST /profiles` - Create a profile
- `GET /profiles` - List all profiles
- `PUT /profiles/{id}` - Update a profile
- `DELETE /profiles/{id}` - Delete a profile

### Core Products (engine v2)
- `POST /natal-profile` - Structured natal profile. Body: inline `profile` or `{profile_id}`.
- `POST /forecast` - Daily/weekly/monthly forecast. Body: `scope: daily|weekly|monthly`, optional `date`, plus inline `profile` or `{profile_id}`.
- `POST /compatibility` - Synastry + numerology blend. Body: `person_a`, `person_b`, `relationship_type` (default `romantic`).

### Readings (legacy + v2)
- `POST /reading` - Legacy sun-sign/numerology daily/weekly/monthly. Response also includes `engine_v2` forecast.
- `GET /readings/{profile_id}` - Reading history
- `POST /readings/{reading_id}/feedback` - Add feedback/journal

### Numerology
- `GET /numerology/profile/{profile_id}` - Full numerology profile
- `POST /numerology/name-analysis` - Analyze any name

### Compatibility (legacy simple endpoints)
- `POST /compatibility/combined` - Full compatibility analysis
- `POST /compatibility/astrology` - Astrology-only compatibility
- `POST /compatibility/numerology` - Numerology-only compatibility

### Favorites & Preferences
- `POST /favourites/{reading_id}` - Add to favorites
- `DELETE /favourites/{reading_id}` - Remove from favorites
- `GET /favourites/{profile_id}` - List favorites
- `GET /preferences/{profile_id}` - Get preferences
- `PUT /preferences/{profile_id}` - Update preferences

### Learning
- `GET /learn/zodiac` - All zodiac signs
- `GET /learn/zodiac/{sign}` - Specific sign info
- `GET /learn/numerology` - All numerology terms
- `GET /learn/numerology/{term}` - Specific term info
- `GET /learn/search?q=term` - Search glossary

## Testing
```bash
cd /path/to/project
python -m pytest backend/tests/ -v
# 24 tests covering astrology, numerology, compatibility, and glossary
```

## Notes
- CORS is open (`*`) for easy local testing; tighten allow_origins if needed.
- Three.js layer is decorative; core UX still works without WebGL.
- Deterministic outputs: same user/date → same reading; different dates → new reading.
- Dev-only: `FORCE_SIMULATION` in `index.tsx` can be toggled true to bypass the backend for demos.
- Logging: FastAPI uses Python logging with `LOG_LEVEL`.
- Caching: If `REDIS_URL` is set, daily readings are cached by user/date for 24h.
- Rate Limiting: Redis-backed sliding window rate limiter (default 60 requests/min per IP).
