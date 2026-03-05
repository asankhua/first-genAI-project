# Deployment Guide

## Streamlit Cloud (Frontend)

### Prerequisites

- GitHub account
- [Streamlit Community Cloud](https://share.streamlit.io/) account
- Backend API deployed (see below)

### Deploy to Streamlit Cloud

1. **Push code to GitHub** (see GitHub section below).

2. **Go to [share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.

3. **New app** → Select your repo `zomato-ai-recommender`.

4. **Main file path:** `streamlit_app.py`

5. **Advanced settings** → Secrets. Add:

```toml
API_BASE_URL = "https://your-backend-url.onrender.com"
```

Replace with your deployed backend URL.

6. **Deploy.** Streamlit Cloud will install from `requirements.txt` and run the app.

---

## Backend Deployment (Required for Streamlit app)

The Streamlit frontend calls the Phase 4 API. Deploy the backend to one of:

### Option A: Render

1. Create `render.yaml` or use Render dashboard.
2. Add a **Web Service**:
   - Build: `pip install -r phase4/requirements.txt`
   - Start: `uvicorn phase4.src.app:app --host 0.0.0.0 --port $PORT`
   - Set env vars: `CLEANED_DATA_PATH`, `GROQ_API_KEY` (from .env)
3. Run e2e pipeline once to generate `phase4/data/cleaned.csv` and commit it, or run as a build step.

### Option B: Railway / Fly.io / Heroku

Similar: deploy the Phase 4 FastAPI app, set `CLEANED_DATA_PATH` and `GROQ_API_KEY`, then use the public URL in Streamlit secrets.

---

## GitHub Setup & Push

```bash
cd zomato-ai-recommender
git init
git add .
git commit -m "Initial commit: Zomato AI Recommender"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/zomato-ai-recommender.git
git push -u origin main
```

Create the repo on GitHub first (github.com/new), then add the remote and push.
