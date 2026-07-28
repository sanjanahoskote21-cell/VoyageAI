# VoyageAI

**Your AI Travel Companion** — plan smarter, travel better.

VoyageAI is a full-stack travel planning app that combines route optimization, AI-assisted trip planning, and budget estimation into one workflow. Built as a resume/portfolio flagship project, it's designed to show real end-to-end engineering: a working auth system, a custom route optimizer, an LLM-powered chat assistant, and a consistent, hand-built design system across every page.

---

## Features

**Trip Planning**
- Create a trip with start/end location, number of days, travelers, budget tier, and travel mode
- Search and select places to visit, then generate an optimized route between them
- Route optimization (nearest-neighbor based) shows total distance and how much distance was saved vs. a naive route
- Automatic budget estimation broken down by hotel, food, fuel, and misc costs
- Ordered itinerary view showing visit sequence

**Travel Twin (AI Chat)**
- Trip-aware chat assistant to ask questions about your itinerary, budget, or route

**Auth**
- Register / login with JWT-based sessions
- Email verification required before login (real email delivery via Gmail SMTP)
- Forgot / reset password flow with short-lived, scope-limited reset tokens
- No email enumeration — forgot-password and resend-verification endpoints behave identically whether or not the email exists

**Places**
- Local places database with search
- Google Places sync pipeline (live API integration with a curated mock-data fallback, since it doesn't require billing to be enabled to test the full pipeline)

**Design**
- Consistent visual identity across every page — a warm charcoal/terracotta palette with Fraunces (display) and Inter (body) typefaces
- Loading, error, and empty states handled throughout (trip search, chat, dashboard, auth flows)

---

## Tech Stack

| Layer | Tools |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, lucide-react |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic Settings |
| Database | PostgreSQL |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Email | Gmail SMTP |
| External APIs | Google Places API (with mock fallback) |

---

## Architecture Notes

- **Route optimizer**: a from-scratch nearest-neighbor route optimization algorithm — the core DSA piece of the project — computes visit order and reports distance saved vs. an unoptimized route.
- **Scoped JWT tokens**: password reset and email verification both reuse the same JWT signing infrastructure as login, but with a `scope` claim baked into the token so a reset token can never be replayed as a verification token or vice versa.
- **Graceful external-API fallback**: the Google Places sync pipeline attempts a real API call first and transparently falls back to curated mock data if the call fails (e.g. billing not enabled) — the code path is fully real and switches to live data automatically once billing is available, no code changes needed.

---

## Project Structure

```
VoyageAI/
├── backend/
│   └── app/
│       ├── api/v1/          # route handlers
│       ├── core/            # config, security (JWT, hashing)
│       ├── models/          # SQLAlchemy models
│       ├── schemas/         # Pydantic request/response schemas
│       └── services/        # business logic (auth, trips, places, email, route optimization)
└── frontend/
    └── src/
        ├── api/              # typed API client functions
        ├── pages/            # route-level page components
        ├── routes/           # React Router config
        └── hooks/            # shared hooks (auth context, etc.)
```

---

## Getting Started

### Prerequisites
- Python 3.13+
- Node.js
- PostgreSQL

### Backend Setup

```bash
cd backend
pip install -r requirements.txt --break-system-packages
```

Create a `.env` file in `backend/` (see `.env.example`):

```
DATABASE_URL=postgresql://user:password@localhost/voyageai
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_URL=http://localhost:5173

SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password

GOOGLE_MAPS_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
```

Run migrations and start the server:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

API docs available at `http://127.0.0.1:8000/docs`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`.

---

## Roadmap

- [ ] Recommendation engine (place-scoring based on trip preferences) — designed, not yet implemented
- [ ] Automated tests, particularly for the route optimizer
- [ ] Rate limiting on auth endpoints
- [ ] Live Google Places integration (pending Cloud billing)

---

## License

Personal/portfolio project — not currently licensed for reuse.