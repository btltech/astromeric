# Railway Deployment Guide

## Quick Deploy via Railway CLI

If you have Railway linked to VS Code:

```bash
# 1. Initialize Railway project in this directory
railway init

# 2. Link to existing project (if you already created one on railway.app)
railway link

# 3. Add environment variables
railway variables set ALLOW_ORIGINS="https://your-frontend-domain.com"
railway variables set REDIS_URL="redis://your-redis-url"  # Optional, for caching

# 4. Deploy
railway up
```

## Deploy via GitHub (Recommended)

1. Go to [railway.app](https://railway.app)
2. Create New Project → Import from GitHub
3. Select this repository
4. Choose root directory: `/` (Railway will detect `railway.json`)
5. Click Deploy

## Environment Variables

Set these in Railway dashboard:

| Variable | Value | Required |
|----------|-------|----------|
| `ALLOW_ORIGINS` | `https://your-frontend.vercel.app,https://your-domain.com` | Recommended |
| `REDIS_URL` | Redis connection URL | Optional (for caching) |
| `FUSION_CACHE_TTL` | `3600` | Optional |
| `LOG_LEVEL` | `info` | Optional |
| `EPHEMERIS_PATH` | `/app/ephemeris` | Automatic |

## Add Database & Redis

### PostgreSQL (Optional - instead of SQLite)
1. In Railway Dashboard → New
2. Select PostgreSQL
3. Copy connection string
4. Update `backend/app/models.py` to use PostgreSQL

### Redis (Optional - for caching)
1. In Railway Dashboard → New
2. Select Redis
3. Copy connection URL
4. Set as `REDIS_URL` environment variable

## Get Your Backend URL

After deployment:
```bash
# Get service URL
railway status

# Or find it in Railway Dashboard under "Deployments"
```

Use this URL as `VITE_API_URL` in your frontend deployment.

## Local Testing Before Deploy

```bash
# Build Docker image locally
docker build -f backend/Dockerfile -t astromeric-backend .

# Run locally
docker run -p 8000:8000 -e PORT=8000 astromeric-backend

# Test
curl http://localhost:8000/health
```

## Troubleshooting

### Check Logs
```bash
railway logs -f
```

### Restart Service
```bash
railway restart
```

### Deploy Specific Version
```bash
railway up --service astromeric-backend
```

## Production Checklist

- [ ] Set `ALLOW_ORIGINS` to your actual frontend domain
- [ ] Add Redis for caching (improves performance)
- [ ] Enable HTTPS (Railway does this automatically)
- [ ] Set up monitoring/alerts in Railway dashboard
- [ ] Configure automatic deploys from GitHub main branch
