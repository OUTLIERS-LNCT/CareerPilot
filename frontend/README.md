# PrepPilot AI frontend

React + Vite frontend for the PrepPilot FastAPI backend. It uses the backend's bearer-token login, dashboard, roadmap, assessment, resource, interview, resume/JD, and profile APIs.

## Run locally

Start the backend first at `http://127.0.0.1:8000`. From this `frontend` directory:

```powershell
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. If the API runs elsewhere, set `VITE_API_BASE_URL` in `.env` to its `/api/v1` URL. The API's `FRONTEND_ORIGIN` should match `http://localhost:5173` or `http://127.0.0.1:5173`.

The frontend stores the access token in browser local storage for this local MVP. For a public production deployment, use HTTPS and consider moving authentication to secure, HTTP-only cookies with CSRF protection. AI interview answers are sent to the configured backend AI provider for coaching, as described in the backend README.

## Deploy

Build with `npm run build`; the static files are written to `dist/` and can be deployed to Vercel. Set `VITE_API_BASE_URL` to the deployed backend API base and set the backend CORS `FRONTEND_ORIGIN` to the Vercel site origin.
