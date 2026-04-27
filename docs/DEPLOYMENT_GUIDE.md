# Deployment Guide — TutorIA Física Stack Migration

## Overview

TutorIA Física foi migrada de **Streamlit** para uma arquitetura moderna:
- **Frontend:** Next.js → Cloudflare Workers (via @opennextjs/cloudflare)
- **Backend:** FastAPI → Render.com (free tier)
- **Database:** Supabase PostgreSQL com pgvector
- **Authentication:** Cloudflare Access (opcional)

---

## Frontend Deployment — Cloudflare Workers + @opennextjs/cloudflare

### Why Cloudflare Workers?

- ✅ Zero cold starts (unlike Render free tier)
- ✅ Global edge deployment
- ✅ Perfect for Next.js static + serverless
- ✅ Free tier includes 100k requests/day
- ❌ NOT Cloudflare Pages (Pages doesn't handle Node.js server files)

### Setup Steps

#### 1. Install Dependencies

```bash
cd frontend
npm install @opennextjs/cloudflare
```

#### 2. Create `open-next.config.ts`

```typescript
import { defineCloudflareConfig } from "@opennextjs/cloudflare";
export default defineCloudflareConfig();
```

#### 3. Create `wrangler.jsonc`

```json
{
  "main": ".open-next/worker.js",
  "name": "tutoriafisica",
  "compatibility_date": "2026-04-27",
  "compatibility_flags": ["nodejs_compat"],
  "assets": {
    "directory": ".open-next/assets",
    "binding": "ASSETS"
  }
}
```

#### 4. Update `package.json` Scripts

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "build:cloudflare": "opennextjs-cloudflare build",
    "start": "next start",
    "lint": "next lint",
    "preview": "opennextjs-cloudflare build && opennextjs-cloudflare preview",
    "deploy": "opennextjs-cloudflare build && opennextjs-cloudflare deploy"
  }
}
```

#### 5. Deploy via Cloudflare Dashboard (Recommended)

1. Go to **https://dash.cloudflare.com/**
2. **Workers & Pages** → **Create** → **Deploy with Git**
3. Select repository: `TutorIAFisica`
4. Configure:
   - **Build command:** `npm run build:cloudflare`
   - **Build output directory:** `.open-next`
   - **Root directory:** `frontend`
5. Click **Deploy**

Cloudflare auto-detects `wrangler.jsonc` and deploys to Workers.

#### 6. Verify Deployment

- Check **Workers & Pages** → **tutoriafisica** → **Visit**
- Should load the Next.js app immediately (no "Hello world")

### Troubleshooting

**Problem:** Build fails with "Could not find compiled Open Next config"
- **Fix:** Ensure build command is `npm run build:cloudflare` (not `npm run build`)

**Problem:** Page shows "Hello world" instead of chat interface
- **Fix 1:** Check if Cloudflare Access is blocking (remove if not needed)
- **Fix 2:** Verify `.open-next/` directory exists after build
- **Fix 3:** Hard refresh browser (Ctrl+Shift+R)

**Problem:** Cloudflare Access login loop
- **Fix:** Remove Access policy or allow public access to the Worker

---

## Backend Deployment — Render.com + FastAPI

### Setup

1. Backend files in `/backend/`
2. Uses `requirements.txt` (Python 3.11)
3. `Dockerfile` provided for containerization

### Deploy via Render Blueprint

1. Create `/render.yaml` at project root:

```yaml
services:
  - type: web
    name: tutor-ia-fisica-api
    runtime: docker
    plan: free
    healthCheckPath: /health
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      # ... other API keys
```

2. Push to GitHub
3. Go to **https://render.com/** → **New** → **Blueprint**
4. Connect repo and deploy

### Environment Variables

Set in Render dashboard:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Service role key (with RLS bypass)
- `OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.
- `FRONTEND_URL`: `https://tutoriafisica.hans-059.workers.dev`

### Cold Starts

⚠️ **Render free tier has 15-min cold start timeout.** On first request after inactivity, backend may take 15+ seconds.

Monitor logs:
```
Render Dashboard → tutor-ia-fisica-api → Logs
```

---

## Frontend-Backend Integration

### Environment Variables in Frontend

File: `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=https://tutor-ia-fisica-api.onrender.com
NEXT_PUBLIC_APP_NAME=TutorIA Física — UFSM
```

**Important:** `NEXT_PUBLIC_*` variables are bundled into the client. Never include secrets (API keys) in these.

### API Endpoints

Frontend calls:
- `POST /tutor/ask` — Non-streaming responses
- `POST /tutor/ask/stream` — SSE streaming (for progressive agent output)
- `POST /tutor/feedback` — SM-2 quiz updates
- `GET /health` — Health check

---

## Database — Supabase

### Schema

4 main tables:
1. **students** — User records (email, name, created_at)
2. **concept_status** — SM-2 spaced repetition tracking
3. **misconceptions** — Detected learning gaps
4. **session_log** — Complete interaction logs with agent outputs

### Setup

1. Create Supabase project
2. Run migrations in `supabase/migrations/001_initial_schema.sql`
3. Enable RLS (Row-Level Security) for data isolation
4. Configure pgvector extension (for future semantic search)

### Accessing from Backend

```python
from supabase import create_client
client = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_SERVICE_KEY")
)
```

---

## Deployment Checklist

- [ ] Frontend: All dependencies installed (`npm install`)
- [ ] Frontend: `open-next.config.ts` exists
- [ ] Frontend: `wrangler.jsonc` configured with correct paths
- [ ] Frontend: `.env.local` has correct `NEXT_PUBLIC_API_URL`
- [ ] Backend: `requirements.txt` up to date
- [ ] Backend: `Dockerfile` exists and builds locally
- [ ] Backend: Environment variables set in Render
- [ ] Backend: Supabase credentials configured
- [ ] Backend: Health check endpoint responding (`/health`)
- [ ] Frontend-Backend: Able to make API calls without CORS errors
- [ ] Database: Schema migrated, tables created
- [ ] Database: RLS policies enabled

---

## Common Issues & Solutions

### CORS Errors

**Problem:** Frontend can't reach backend API
- **Check:** `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- **Check:** Backend `main.py` has CORS middleware:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],  # or specify frontend URL
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

### Cold Start Delays

**Problem:** First request takes 15+ seconds
- **Why:** Render free tier pauses inactive apps
- **Workaround:** Use a cron job to ping `/health` every 10 minutes
- **Better:** Upgrade to paid Render plan

### Database Pauses

**Problem:** Supabase project paused after inactivity (free tier)
- **Check:** Supabase dashboard for project status
- **Workaround:** Schedule daily cron to keep DB warm
- **Better:** Upgrade to Pro plan

### Cloudflare Access Blocking

**Problem:** Worker redirects to Cloudflare Access login
- **Fix:** Remove Access policy or allow public routes
- **Or:** Use Access authentication tokens for API calls

---

## Future Improvements

1. **CI/CD:** GitHub Actions to auto-deploy on push
2. **Monitoring:** Sentry for error tracking
3. **Analytics:** Vercel Analytics or Plausible
4. **Caching:** Redis for session storage (Upstash)
5. **Backup:** Automated Supabase backups
6. **Scaling:** Move from free tiers to paid plans for production

---

## Contact & Support

- **Code:** https://github.com/hansufsm/TutorIAFisica
- **Issues:** GitHub Issues
- **Deployment Help:**
  - Cloudflare: https://developers.cloudflare.com/workers/
  - Render: https://render.com/docs
  - Supabase: https://supabase.com/docs

---

**Last Updated:** 2026-04-27
**Deployed Stack:** Cloudflare Workers + Render.com + Supabase
