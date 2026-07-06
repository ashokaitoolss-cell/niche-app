# Niche

Personal market intelligence tool with three feeds — AI/semiconductor research, consumer app market intel,
and a daily synthesis layer that cross-references the two — delivered via a Telegram bot and a card-swipe PWA.

## Structure

```
niche-app/
  backend/    FastAPI + APScheduler + python-telegram-bot + SQLite
  frontend/   React + Vite + Tailwind PWA (dark, Bumble-style swipe stack)
```

## Backend setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in tokens below
uvicorn app.main:app --reload
```

Required in `.env`:
- `ANTHROPIC_API_KEY` — used to summarize/categorize items and generate the daily niche idea
- `TELEGRAM_BOT_TOKEN` — from @BotFather; the bot is disabled (logs a warning) if unset
- `TELEGRAM_CHAT_ID` — your chat/user id, so the hourly and daily jobs know where to push
- `PRODUCT_HUNT_TOKEN` — optional, Product Hunt v2 API developer token (Feed 2 launches fetcher no-ops without it)
- `CRUNCHBASE_API_KEY` — optional, Crunchbase v4 API key (funding-round fetcher no-ops without it)

The scheduler runs an hourly ingest job (Feed 1 + Feed 2) and a daily synthesis job (Feed 3, 08:00 server time)
as soon as the app starts — no separate cron needed.

## Frontend setup

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173, expects backend on http://localhost:8000
```

Set `VITE_API_BASE_URL` to point at a deployed backend when building for production.

## Telegram commands

`/digest` `/research` `/market` `/investors` `/idea` `/add <note>`

## Deployment

See [DEPLOY.md](DEPLOY.md).

## Notes / known gaps

- Operator philosophy (Nikita Bier-style X commentary) is covered only via secondary sources that write about
  or transcribe operator interviews (Lenny's Newsletter, a16z, Not Boring RSS) — live X scraping needs a paid
  API and is intentionally out of scope for v1. Use `/add` to manually log anything you see on X.
- `frontend/public/icons/icon.svg` is a placeholder app icon — swap in real branded icons before a real
  home-screen install.
