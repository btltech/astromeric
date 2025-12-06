# Deployment Guide: Railway (Backend) + Cloudflare Pages (Frontend)

## Prerequisites

- GitHub account with this repository pushed
- Railway account (https://railway.app)
- Cloudflare account (https://cloudflare.com)

---

## Part 1: Deploy Backend to Railway

### Step 1: Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select the `astromeric` repository

### Step 2: Configure Backend Service

1. Railway will auto-detect the Dockerfile in `/backend`
2. If not, click **"Add Service"** → **"GitHub Repo"** → select the repo
3. Go to **Settings** for the service:
   - **Root Directory**: Set to `backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Set Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```
JWT_SECRET_KEY=<generate with: openssl rand -hex 32>
EPHEMERIS_PATH=/app/app/ephemeris
ALLOW_ORIGINS=https://your-app.pages.dev
```

Optional variables:
```
GEMINI_API_KEY=<your Gemini API key for AI explanations>
GEMINI_MODEL=gemini-2.0-flash
REDIS_URL=<if using Redis for caching>
```

### Step 4: Add Database (Optional)

1. In Railway project, click **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway will automatically set `DATABASE_URL` for your backend service
3. The app will use PostgreSQL instead of SQLite

### Step 5: Deploy

1. Railway will automatically build and deploy
2. Wait for the build to complete (2-3 minutes)
3. Get your public URL from the **Settings** tab (e.g., `https://astromeric-backend.up.railway.app`)
4. Test: `curl https://your-app.up.railway.app/health`

---

## Part 2: Deploy Frontend to Cloudflare Pages

### Step 1: Create Cloudflare Pages Project

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **Workers & Pages** → **Pages**
3. Click **"Create a project"** → **"Connect to Git"**
4. Authorize Cloudflare to access your GitHub
5. Select the `astromeric` repository

### Step 2: Configure Build Settings

- **Project name**: `astromeric` (or your preferred name)
- **Production branch**: `main`
- **Build command**: `npm run build`
- **Build output directory**: `dist`
- **Root directory**: `/` (leave empty, not `/backend`)

### Step 3: Set Environment Variables

In **Environment variables** section, add:

```
VITE_API_URL=https://your-backend.up.railway.app
```

> Replace with your actual Railway backend URL from Part 1, Step 5.

### Step 4: Deploy

1. Click **"Save and Deploy"**
2. Wait for the build (1-2 minutes)
3. Your site will be live at `https://astromeric.pages.dev`

### Step 5: Custom Domain (Optional)

1. Go to your Pages project → **Custom domains**
2. Add your domain (e.g., `astromeric.com`)
3. Follow Cloudflare's DNS setup instructions

---

## Part 3: Update CORS on Railway

After you have both URLs:

1. Go back to Railway → your backend service → **Variables**
2. Update `ALLOW_ORIGINS`:
   ```
   ALLOW_ORIGINS=https://astromeric.pages.dev,https://yourdomain.com
   ```
3. Railway will automatically redeploy

---

## Verification Checklist

- [ ] Backend health check: `curl https://your-backend.up.railway.app/health`
- [ ] Frontend loads at your Cloudflare Pages URL
- [ ] Enter birth details and get a reading
- [ ] Check browser console for any CORS errors

---

## Troubleshooting

### "Connection lost" error
- Verify `VITE_API_URL` is set correctly in Cloudflare Pages
- Check that `ALLOW_ORIGINS` in Railway includes your frontend URL
- Ensure the backend is running (check Railway logs)

### Build fails on Railway
- Check that `/backend` is set as the root directory
- Verify `requirements.txt` is in the backend folder
- Check Railway build logs for specific errors

### Build fails on Cloudflare
- Ensure build command is `npm run build`
- Ensure output directory is `dist`
- Check that `package.json` exists in root

### Ephemeris errors
- Verify `EPHEMERIS_PATH=/app/app/ephemeris` is set
- The Dockerfile should copy ephemeris files automatically

---

## Cost Estimates

- **Railway**: Free tier includes 500 hours/month. For production, ~$5-20/month.
- **Cloudflare Pages**: Free for most use cases. Unlimited requests.
- **Total**: $0-20/month depending on usage.
