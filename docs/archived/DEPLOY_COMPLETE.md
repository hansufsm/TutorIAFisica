# 🚀 TutorIAFisica — Complete Deployment Guide

**Status:** ✅ Frontend LIVE | ✅ Backend LIVE | ⏳ Integration Testing

---

## Live URLs

| Component | URL | Status |
|-----------|-----|--------|
| **Frontend** | https://tutoriafisica.vercel.app | ✅ Live |
| **Backend** | https://tutor-ia-fisica-api.onrender.com | ✅ Live |
| **Streamlit** | Local only (offline mode) | – |

---

## Frontend Deployment (Vercel)

### Status: ✅ Active

**Project:** TutorIAFisica on Vercel  
**Deployment:** Automatic on `main` branch push  
**Build:** Next.js 15 (frontend/) via root `vercel.json`

### Configuration (vercel.json at root)

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "installCommand": "cd frontend && npm install",
  "devCommand": "cd frontend && npm run dev",
  "crons": [
    {
      "path": "/api/keepalive",
      "schedule": "0 12 */5 * *"
    }
  ]
}
```

### Environment Variables (Set in Vercel Dashboard)

**Required:**
```
NEXT_PUBLIC_API_URL=https://tutor-ia-fisica-api.onrender.com
```

**How to set:**
1. Go to https://vercel.com/dashboard
2. Select `TutorIAFisica` project
3. Settings → Environment Variables
4. Add `NEXT_PUBLIC_API_URL` with the backend URL
5. Redeploy

---

## Backend Deployment (Render.com)

### Status: ✅ Active

**Service:** tutor-ia-fisica-api  
**URL:** https://tutor-ia-fisica-api.onrender.com  
**Runtime:** Python 3.11 on Render.com free tier  
**Deployment:** Auto-deploy from `main` branch

### Configuration (render.yaml at root)

```yaml
services:
  - type: web
    name: tutor-ia-fisica-api
    runtime: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: SUPABASE_URL
        scope: build,run
      - key: SUPABASE_KEY
        scope: build,run
      - key: GEMINI_API_KEY
        scope: build,run
      # ... all other API keys
```

### Environment Variables (Set in Render Dashboard)

**Required:**
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
GEMINI_API_KEY=xxx
OPENAI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
DEEPSEEK_API_KEY=xxx
PERPLEXITY_API_KEY=xxx
GROK_API_KEY=xxx
```

**How to set:**
1. Go to https://dashboard.render.com
2. Select `tutor-ia-fisica-api` service
3. Settings → Environment
4. Add all API keys from your `.env` file
5. Service will auto-redeploy

### Available Endpoints

```
GET  /health              — Health check
GET  /docs                — OpenAPI Swagger UI
GET  /models              — List available models
POST /tutor/ask           — Synchronous request
GET  /tutor/ask/stream    — SSE streaming response
POST /tutor/feedback      — SM-2 spaced repetition feedback
```

---

## Integration Checklist

- [ ] Frontend loads at https://tutoriafisica.vercel.app
- [ ] Backend accessible at https://tutor-ia-fisica-api.onrender.com/health
- [ ] CORS enabled (backend allows all origins, frontend can call API)
- [ ] `NEXT_PUBLIC_API_URL` set in Vercel environment
- [ ] All API keys configured in Render.com environment
- [ ] Try sending a question in frontend and see SSE stream response
- [ ] Student feedback triggers SM-2 calculation
- [ ] Cron job `/api/keepalive` runs every 5 days (prevents Render free tier sleep)

---

## Testing Integration

### 1. Test Backend Health

```bash
curl https://tutor-ia-fisica-api.onrender.com/health
# Expected: {"status": "ok", "version": "2026.2.0"}
```

### 2. Test Frontend to Backend Connection

1. Open https://tutoriafisica.vercel.app
2. Press F12 → Console
3. Type a physics question
4. Watch Network tab → look for request to `/tutor/ask/stream`
5. Should see streaming response (EventSource)

### 3. Check CORS Issues

If you see CORS error in console:
```
Access to XMLHttpRequest blocked by CORS policy...
```

**Fix:** Backend `backend/main.py` already has `allow_origins=["*"]`, so CORS should work. If not:
- Clear browser cache
- Check that `NEXT_PUBLIC_API_URL` is correct (with `https://`, not `http://`)
- Check Render logs for errors

### 4. Verify Environment Variables

In browser console (frontend):
```javascript
// Should return the backend URL
console.log(process.env.NEXT_PUBLIC_API_URL)
```

---

## Troubleshooting

### Frontend won't build
- Check `frontend/package.json` has `next` in dependencies
- Verify `vercel.json` has correct `buildCommand` and `outputDirectory`
- Check build logs in Vercel dashboard

### Backend returns 502/503
- Render free tier goes to sleep after 15 min of inactivity
- Cron job `/api/keepalive` should prevent this
- Check Render logs for errors

### CORS errors when sending question
- Frontend sends request to backend
- Backend CORS middleware must allow the frontend origin
- Current config: `allow_origins=["*"]` (allows all)
- If issue persists, add explicit frontend URL to `allow_origins`

### API keys not found
- Make sure keys are set in Render.com environment (not just `.env`)
- Render builds fresh container each time, doesn't have local `.env`
- Check `render.yaml` references the right env var names

---

## Auto-Deployment

### Frontend (Vercel)
- Triggers on: push to `main` branch
- Build time: ~2-3 min
- Deploy time: Instant (CDN)

### Backend (Render.com)
- Triggers on: push to `main` branch
- Build time: ~5-10 min (pip install, etc)
- Deploy time: 1-2 min (container spin-up)

Both use GitHub webhook, so push once and both deploy automatically.

---

## Next Steps

1. **Verify integration works** — Send a test question from frontend
2. **Monitor logs** — Check Vercel + Render dashboards for errors
3. **Load test** — Try high-volume requests to check backend stability
4. **Implement speech input** — VoiceInput component already exists, wire to `/api/transcribe`
5. **Add student auth** — Use Supabase Auth or external OAuth

---

## Rollback Plan

If something breaks:

**Frontend:**
```bash
# Revert to previous deployment
# Via Vercel dashboard: Deployments → Select previous → Promote to Production
```

**Backend:**
```bash
# Render keeps last 10 deployments
# Via Render dashboard: Deployments → Select previous → Redeploy
```

---

## Maintenance

### Weekly
- Monitor Render logs for errors
- Check if any API rate limits hit

### Monthly
- Review deployment costs (Vercel free, Render free tier)
- Update dependencies (`npm update`, `pip list --outdated`)

### As-needed
- Add new API keys to both Vercel and Render.com dashboards
- Update `vercel.json` or `render.yaml` if deployment config changes
