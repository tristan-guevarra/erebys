# erebys

**analytics + dynamic pricing engine for sports academies**

understand. price. grow.

---

## why i built this

most sports academies are run by coaches, not business people. they're leaving money on the table because they don't know when to raise prices on high demand events, when to discount low fill rate camps with 3 days to go, or which athletes are about to stop coming. pricing is done by gut feel, churn is invisible until it's too late, and there's zero data on what's actually working.

erebys is my answer to that. it's a b2b saas dashboard that gives academy owners two things: revenue intelligence (real numbers on what's happening across their business) and a dynamic pricing engine that uses ml to suggest better prices based on fill rates, coach ratings, seasonality, and competition. there's also a what-if simulator so you can model demand at different price points before committing.

the goal was to build something an academy owner could plug in and immediately start making smarter decisions — not just measuring results after the fact.

---

## what's inside

```
erebys/
├── backend/              python fastapi backend
│   ├── app/
│   │   ├── api/          all the route handlers (auth, events, analytics, pricing, etc)
│   │   ├── models/       sqlalchemy database models
│   │   ├── schemas/      pydantic request/response shapes
│   │   ├── services/     business logic — analytics calculations, ml pricing engine
│   │   └── workers/      celery background jobs (nightly metrics, weekly insights)
│   ├── alembic/          database migrations
│   └── Dockerfile
├── frontend/             next.js dashboard
│   └── src/
│       ├── app/          pages (dashboard, events, athletes, pricing, experiments, settings)
│       ├── components/   reusable ui bits (charts, cards, tables)
│       ├── hooks/        react query hooks that talk to the api
│       ├── lib/          api client, auth context, utils
│       └── types/        typescript interfaces for everything
├── docker-compose.yml    spins up all 5 services at once
└── .env.example          config template
```

---

## tech stack

| what | how |
|------|-----|
| frontend | next.js 14 (app router), typescript, tailwind css |
| charts | recharts |
| data fetching | tanstack query (react query) |
| forms | react hook form + zod |
| backend | fastapi, python 3.11 |
| orm | sqlalchemy 2.0 async |
| database | postgresql 16 |
| migrations | alembic |
| cache + job queue | redis 7 |
| background jobs | celery |
| ml / pricing math | scikit-learn, pandas, numpy |
| auth | jwt (access + refresh tokens), bcrypt via passlib |
| api client | axios with auto auth header injection |
| infra | docker compose |

---

## how the auth works

- login → backend returns an access token (30 min) + refresh token (7 days)
- both stored in localstorage on the frontend
- every api request automatically gets an `Authorization: Bearer <token>` header injected
- if a request comes back 401, the frontend tries to use the refresh token to get a new access token before giving up
- multi-tenancy: every request also needs an `X-Organization-Id` header so the backend knows which org's data to return
- roles: superadmin (platform-level), admin (org owner), manager (coach/staff)

---

## how the pricing engine works

the ml engine scores each event on a few signals:
- **historical fill rate** — did similar events sell out?
- **days to start** — urgency increases as the event gets closer
- **coach rating** — higher rated coaches can command more
- **seasonality** — certain months are busier
- **competition proxy** — manually set per-region score (1-10) for how competitive the local market is

it outputs: a suggested price, a confidence score (0-100), and the top factors driving the recommendation. there's also a what-if simulator that lets you model demand at different price points.

---

## how the data model is set up

the whole thing is multi-tenant — every table has an `organization_id` so orgs never see each other's data.

main tables:
- `organizations` — each academy is one org
- `users` + `org_user_roles` — users can belong to multiple orgs with different roles
- `coaches` — the actual coaches (separate from user accounts)
- `athletes` — students/participants, tracks ltv, no-show rate, booking history
- `events` — camps, clinics, private sessions
- `bookings` — who signed up for what, at what price
- `attendance` — who actually showed up vs no-showed
- `payments` — revenue tracking (stripe-ready field structure)
- `ratings` — post-event scores for coaches and events
- `metrics_daily` — pre-aggregated daily kpis so dashboard queries are fast
- `pricing_recommendations` — ml-generated price suggestions with drivers
- `price_change_requests` — approval workflow before a price change goes live
- `experiments` — a/b price testing framework
- `feature_flags` — per-org feature gating
- `audit_logs` — full action trail
- `insight_reports` — ai-generated weekly summaries

---

## setting up locally

you need docker desktop installed. that's it.

**1. clone the repo and copy the env file**

```bash
git clone https://github.com/tristan-guevarra/erebys.git
cd erebys
cp .env.example .env
```

**2. start all services**

```bash
docker compose up --build -d
```

this builds and starts:
- frontend at `http://localhost:3000`
- backend api at `http://localhost:8000`
- interactive api docs at `http://localhost:8000/docs`
- postgresql on port 5432
- redis on port 6379

first time it'll take a minute to build. after that `docker compose up -d` is fast.

**3. seed the database**

migrations run automatically on backend startup. you just need to seed:

```bash
docker compose exec backend python -m app.seed
```

**4. log in**

don't use the superadmin for the dashboard — it has no org assigned. use an org owner instead:

| role | email | password |
|------|-------|----------|
| superadmin (no org data) | admin@erebys.io | admin123 |
| elite soccer — owner | owner@elite-soccer.com | password123 |
| elite soccer — coach | coach@elite-soccer.com | password123 |
| bay area tennis — owner | owner@bay-tennis.com | password123 |
| bay area tennis — coach | coach@bay-tennis.com | password123 |
| northside basketball — owner | owner@northside-bball.com | password123 |
| northside basketball — coach | coach@northside-bball.com | password123 |

---

## useful docker commands

```bash
# start everything
docker compose up --build -d

# stop everything
docker compose down

# see backend logs
docker compose logs -f backend

# see all logs
docker compose logs -f

# run seed data
docker compose exec backend python -m app.seed

# open a shell inside the backend container
docker compose exec backend bash

# connect to postgres directly
docker compose exec postgres psql -U erebys -d erebys

# reset db from scratch (drops everything and re-seeds)
docker compose exec backend alembic downgrade base
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed

# restart just the backend after code changes
docker compose restart backend
```

---

## api overview

all endpoints need a jwt in the `Authorization: Bearer <token>` header. most also need `X-Organization-Id` for multi-tenancy. full interactive docs at `/docs`.

| group | what it does |
|-------|-------------|
| `POST /api/v1/auth/login` | returns access + refresh tokens |
| `POST /api/v1/auth/refresh` | swap a refresh token for a new access token |
| `GET /api/v1/auth/me` | get current user + their org roles |
| `GET /api/v1/events` | list events for the org |
| `GET /api/v1/events/performance` | per-event revenue, utilization, ratings |
| `GET /api/v1/analytics/overview` | main kpi numbers |
| `GET /api/v1/analytics/revenue` | daily revenue breakdown |
| `GET /api/v1/analytics/cohorts` | monthly retention cohorts |
| `GET /api/v1/analytics/no-show-risk` | athletes ranked by no-show risk |
| `GET /api/v1/pricing/recommendations` | ml pricing suggestions |
| `POST /api/v1/pricing/what-if` | simulate demand at different prices |
| `POST /api/v1/pricing/change-requests` | submit a price change for approval |
| `GET /api/v1/experiments` | a/b price experiments |
| `GET /api/v1/admin/audit-logs` | full action trail |
| `GET /api/v1/admin/feature-flags` | per-org feature toggles |
| `POST /api/v1/imports/events` | bulk import events from csv |

---

## environment variables

| variable | what it's for | default |
|----------|--------------|---------|
| `DATABASE_URL` | async postgres connection (used by fastapi) | set in .env |
| `DATABASE_URL_SYNC` | sync postgres connection (used by seed + celery) | set in .env |
| `REDIS_URL` | redis for caching | redis://redis:6379/0 |
| `JWT_SECRET` | signs all jwt tokens — change this in prod | set in .env |
| `JWT_ALGORITHM` | hs256 | hs256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | how long access tokens last | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | how long refresh tokens last | 7 |
| `CORS_ORIGINS` | which frontend origins the api allows | http://localhost:3000 |
| `NEXT_PUBLIC_API_URL` | what url the browser uses to hit the api | http://localhost:8000 |

---

## background jobs (celery)

there's a celery worker running alongside the backend. it handles:
- **nightly metrics** — pre-aggregates daily kpis so dashboard queries are instant
- **weekly insights** — generates ai-written summaries of academy performance
- **pricing retraining** — periodically retrains the ml model as new booking data comes in

the worker uses redis as its broker. you can see worker logs with:

```bash
docker compose logs -f worker
```

---

## known things to be aware of

- the superadmin account (`admin@erebys.io`) has no organization assigned — it won't show any dashboard data. log in with an org owner to see actual data.
- seed data generates random events with dates spanning 120 days back and 60 days forward, so what you see will vary slightly each time you seed.
- athlete `no_show_rate` is tracked on the model but the seed doesn't backfill it from attendance records, so it'll show 0% in the risk table. in production this would be calculated from actual attendance.
- the ml pricing engine in dev mode falls back to a heuristic model if there isn't enough training data (which is normal right after seeding).

---

## license

proprietary. all rights reserved.
