# Phase 5: UI for Recommendations

Single-page UI to submit place, rating, and optional price/cuisine and display restaurant recommendations from the Phase 4 API.

## Stack

- **React 18** + **Vite 5**
- Styling: plain CSS (no framework)
- Tests: **Vitest** + **React Testing Library**

## Setup

```bash
cd phase5
npm install
```

## Run tests

From **phase5** directory:

```bash
npm test
```

From **project root**:

```bash
cd phase5 && npm install && npm test
```

**To confirm everything is working:**

```bash
cd phase5 && npm test
```

## Run the UI (dev)

```bash
cd phase5
npm run dev
```

Open http://localhost:5173. The app uses Vite’s proxy: requests to `/api/*` are forwarded to the Phase 4 backend (default http://localhost:8000). So run the Phase 4 API first:

```bash
# Terminal 1: Phase 4 API
cd phase4 && uvicorn src.app:app --reload --port 8000

# Terminal 2: Phase 5 UI
cd phase5 && npm run dev
```

Then use the form at http://localhost:5173.

## API base URL

To point the UI at a different backend, set `VITE_API_URL` when building or in a `.env` file:

```bash
VITE_API_URL=http://localhost:8000 npm run dev
```

If `VITE_API_URL` is unset, the app uses the Vite proxy (`/api` → backend).

## Build for production

```bash
npm run build
npm run preview   # serve dist/
```
