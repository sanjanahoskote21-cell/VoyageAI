# VoyageAI

**Your AI travel companion: plan smarter, travel better.**

VoyageAI is a full-stack travel planner that combines route optimization, a data-backed budget estimator, a place recommendation engine and an AI chat assistant in one workflow. It is built to show end-to-end engineering: a secure auth system, a from-scratch route optimizer, an LLM-powered chat, database-level integrity guarantees, and an automated test suite.

---

## Architecture

```mermaid
flowchart LR
  UI["React + TypeScript SPA"] -->|"REST + JWT"| API["FastAPI backend"]
  API --> DB[("PostgreSQL")]
  API --> GEM["Gemini API (Travel Twin chat)"]
  API --> GEO["Nominatim (geocoding)"]
  API --> GP["Google Places (live, or mock fallback)"]
  API --> SMTP["Gmail SMTP (verification and reset emails)"]
```

<!--
Screenshots: save images in docs/screenshots/ and uncomment the lines you use.

![Trip planner](docs/screenshots/trip-planner.png)
![Itinerary and route](docs/screenshots/itinerary.png)
![Travel Twin chat](docs/screenshots/travel-twin.png)
-->

---

## Features

**Trip planning**
- Create a trip with start and end location, number of days, travelers, budget tier and travel mode
- Add places from the local database, or type any place name and have it geocoded as a custom place
- Route optimization with a fixed end point, so the order of stops makes the whole start-to-end trip short, not just the leg to the last stop
- Budget estimate split into hotel, food, fuel and misc costs
- Ordered itinerary view showing the visit sequence, total distance and distance saved
- Delete a trip along with its places, budget estimate and chat history

**Recommendation engine**
- Suggests places to add to a trip, scored on three signals: rating (40%), category match with the trip's existing places (35%) and proximity to the trip's places within 50 km (25%)
- Never suggests a place that is already on the trip; returns the top 10

**Travel Twin (AI chat)**
- Trip-aware assistant powered by Gemini, with automatic retry on transient API failures and markdown-formatted replies

**Auth and accounts**
- Register and log in with JWT sessions
- Email verification required before login, with real email delivery through Gmail SMTP
- Forgot-password and reset-password flow with short-lived, scope-limited tokens
- No email enumeration: forgot-password and resend-verification behave the same whether or not the email exists
- Profile page to update your display name
- Rate limiting on the auth endpoints

**Places**
- Local places database with search
- Google Places sync pipeline: tries the live API first and falls back to curated mock data, so the full pipeline can be tested without billing enabled
- Duplicate-proof by design (see below)

**Design**
- A consistent warm charcoal and terracotta design system with Fraunces (display) and Inter (body) typefaces
- Loading, error and empty states handled throughout

---

## Engineering highlights

- **Route optimizer.** Written from scratch: Haversine distances, a nearest-neighbor starting route, then 2-opt improvement to remove crossing legs, with an optional fixed end point. It reports total distance and distance saved.
- **Budget engine.** Hotel and food rates come from per-city, per-tier rows in the database. Cities without their own rows fall back to the tier-wide average, so a budget is always produced.
- **Duplicate-place protection.** All place creation goes through one `get_or_create_place()` function that matches on a normalized name and city, and a unique index on `lower(btrim(name)), lower(btrim(city))` makes the database itself reject duplicates. The Google Places sync links a hand-seeded row to its synced twin instead of creating a second row.
- **Per-user data isolation.** Every trip query is scoped to the logged-in user. Another user's trip returns 404, so trip IDs cannot be probed. This includes the recommendations endpoint.
- **Scoped JWTs.** Password reset and email verification reuse the login signing infrastructure but carry a `scope` claim, so a token for one purpose can never be replayed for another.
- **Cascade deletes.** Deleting a trip removes its places, budget estimate and chat messages through SQLAlchemy cascades, covered by regression tests.
- **Rate limiting.** Implemented with slowapi on the auth endpoints:

| Endpoint | Limit |
|---|---|
| `POST /auth/register` | 5 per minute |
| `POST /auth/login` | 10 per minute |
| `POST /auth/forgot-password` | 3 per minute |
| `POST /auth/reset-password` | 5 per minute |
| `POST /auth/verify-email` | 5 per minute |
| `POST /auth/resend-verification` | 3 per minute |

---

## Tech stack

| Layer | Tools |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS 4, React Router, TanStack Query, axios, react-markdown, lucide-react |
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic Settings, slowapi |
| Database | PostgreSQL (Supabase in development) |
| Auth | JWT (python-jose), bcrypt (passlib) |
| AI | Gemini API (Travel Twin) |
| Email | Gmail SMTP |
| External APIs | Nominatim (geocoding), Google Places (with mock fallback) |
| Testing | pytest, FastAPI TestClient, throwaway PostgreSQL test database |

---

## API overview

All routes are under `/api/v1`. Full interactive docs are at `/docs` when the server is running.

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `PATCH /auth/me`, `POST /auth/forgot-password`, `POST /auth/reset-password`, `POST /auth/verify-email`, `POST /auth/resend-verification` |
| Trips | `POST /trips/`, `GET /trips/`, `GET /trips/{id}`, `DELETE /trips/{id}` |
| Trip places | `POST /trips/{id}/places/{place_id}`, `POST /trips/{id}/places/custom`, `DELETE /trips/{id}/places/{trip_place_id}` |
| Recommendations | `GET /trips/{id}/recommendations` |

---

## Project structure

```
VoyageAI/
├── backend/
│   ├── alembic/              # database migrations
│   ├── app/
│   │   ├── api/v1/           # route handlers
│   │   ├── core/             # config, security (JWT, hashing), rate limiter, dependencies
│   │   ├── db/               # engine, session, declarative base
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── services/         # business logic (auth, trips, places, budget,
│   │                         #   recommendations, route optimization, email, chat)
│   ├── scripts/              # maintenance scripts (seeding, dedupe, constraint check)
│   ├── test/                 # pytest suite (conftest.py, api/, services/)
│   ├── .env.example
│   ├── pytest.ini
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/              # typed API client functions
        ├── pages/            # route-level page components
        ├── routes/           # React Router config
        └── hooks/            # shared hooks (auth context, etc.)
```

---

## Getting started

### Prerequisites
- Python 3.13
- Node.js
- A PostgreSQL database (a free Supabase project works, or a local install)

### Backend

```bash
git clone https://github.com/sanjanahoskote21-cell/VoyageAI.git
cd VoyageAI/backend

python -m venv .venv
# Windows (Git Bash): source .venv/Scripts/activate
# Windows (cmd/PowerShell): .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Only `DATABASE_URL` and `JWT_SECRET_KEY` are required to start the app. Generate a secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

The other values enable optional features: SMTP credentials for real emails, `GEMINI_API_KEY` for Travel Twin, `GOOGLE_MAPS_API_KEY` for live Google Places data (without it the sync uses mock data). With `ENVIRONMENT=development` and no SMTP configured, the API returns verification and reset links in the response so you can test the flows locally.

Apply migrations and start the server:

```bash
python -m alembic upgrade head
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`, with docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

### Maintenance scripts

Run from `backend/` with the virtual environment active:

```bash
python -m scripts.seed_extra_cities      # hotel and restaurant rates for extra cities (safe to re-run)
python -m scripts.dedupe_places          # preview duplicate places (dry run)
python -m scripts.dedupe_places --apply  # merge duplicates for real
python -m scripts.check_place_constraint # confirm the unique index rejects duplicates
```

---

## Running the tests

The tests run against a separate, throwaway PostgreSQL database and never touch your development data. Each test runs inside a transaction that is rolled back afterwards.

1. Create an empty test database. Its name must contain `test`:

   ```bash
   psql -U postgres -c "CREATE DATABASE voyageai_test;"
   ```

2. Create `backend/.env.test` (it is gitignored) with a single line:

   ```
   TEST_DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/voyageai_test
   ```

   If your password contains special characters, URL-encode them (for example `@` becomes `%40`). Use your server's port if it is not 5432.

   Keep this variable out of `.env`: the app's settings reject unknown variables and will fail to start.

3. Install the test tools and run the suite from `backend/`:

   ```bash
   python -m pip install pytest httpx
   python -m pytest -v
   ```

The suite refuses to run if `TEST_DATABASE_URL` points at your development database, at a Supabase host, or at any database whose name does not contain `test`. Rate limiting is switched off and outgoing email is mocked, so tests are fast and make no network calls to SMTP.

**What is covered (60+ tests):**
- Route optimizer: distances, nearest-neighbor, 2-opt, fixed end point
- Place service: normalization, duplicate prevention at both the code and database level, sync linking to seeded rows
- Auth: registration, duplicate emails, login failures, email verification, `/auth/me`
- Profile update: validation, authentication, no password hash in responses
- Trip deletion: cascade to places, budget and chat history, ownership checks
- Recommendations: ownership enforcement, ordering, score ranges

---

## Roadmap

- [ ] Recommendations section on the itinerary page, with one-click add
- [ ] Live Google Places integration (pending Cloud billing)
- [ ] Deployment (frontend on Vercel, backend on Render, database on Supabase)
- [ ] Tests for the Travel Twin chat service, with the Gemini client mocked

---

## License

Personal/portfolio project, not currently licensed for reuse.
