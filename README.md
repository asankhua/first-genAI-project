# Zomato AI Recommender

AI-powered restaurant recommendation service for Bangalore. Get personalized restaurant suggestions based on locality, rating, price, and cuisine.

## Quick Start

```bash
# 1. Install dependencies
python3 -m venv phase1/.venv phase2/.venv phase3/.venv phase4/.venv
phase1/.venv/bin/pip install -r phase1/requirements.txt
phase2/.venv/bin/pip install -r phase2/requirements.txt
phase3/.venv/bin/pip install -r phase3/requirements.txt
phase4/.venv/bin/pip install -r phase4/requirements.txt
cd phase5 && npm install

# 2. Add GROQ_API_KEY to .env (see .env.example)

# 3. Run full stack
./run_all.sh
# → UI: http://localhost:5173  |  Streamlit: ./run_streamlit.sh → http://localhost:5175
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. New app → Select repo, main file: `streamlit_app.py`
4. Add secret: `API_BASE_URL` = your deployed backend URL

See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions.

## Project Structure

- **Phase 1**: Data fetch (Hugging Face)
- **Phase 2**: Data cleaning pipeline
- **Phase 3**: Filter + LLM (Groq)
- **Phase 4**: FastAPI backend
- **Phase 5**: React UI
- **streamlit_app.py**: Streamlit UI (for deployment)

## Footer

Zomato-AI-Recommender  
© 2026 Ashish Kumar Sankhua. All rights reserved.
