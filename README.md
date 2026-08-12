# Hybrid Routine Tracker

A self-hosted, multi-user web app for tracking progression through the six movement
families of the Hybrid Calisthenics bodyweight routine (Pushups, Leg Raises, Pullups,
Squats, Bridges, Twists). Each user logs workout sessions against their current exercise
variation in a family and is prompted to advance to the next variation once they
consistently meet the level-3 standard.

## Running with Docker (recommended)

1. Copy `.env.example` to `.env` and set a real `SECRET_KEY`:

   ```bash
   cp .env.example .env
   python3 -c "import secrets; print(secrets.token_hex(32))"   # paste the output into .env
   ```

2. Start the app:

   ```bash
   docker compose up --build -d
   ```

3. Open `http://localhost:8000` (or the port set via `HOST_PORT` in `.env`) and register
   an account.

The SQLite database lives in the `hybrid-tracker-data` named Docker volume, mounted at
`/data` inside the container. It's created automatically on first run — no manual setup
or migration step is needed.

### Environment variables

| Variable         | Required | Default                        | Purpose                                                   |
|-------------------|----------|---------------------------------|-------------------------------------------------------------|
| `SECRET_KEY`      | yes      | —                                | Signs session cookies. `docker compose` refuses to start without it. |
| `HOST_PORT`       | no       | `8000`                          | Host port the app is exposed on.                            |
| `SECURE_COOKIES`  | no       | `true`                          | Set to `false` only for local HTTP testing without TLS.     |
| `DATABASE_PATH`   | no       | `/data/hybrid-tracker.db`       | Set by `docker-compose.yml`; only override for local dev.   |

## Running locally without Docker

```bash
python -m venv .venv
.venv/Scripts/activate            # .venv/bin/activate on macOS/Linux
pip install -r requirements.txt

SECRET_KEY=dev-secret SECURE_COOKIES=false DATABASE_PATH=./data/dev.db \
  uvicorn app.main:app --reload
```

Open `http://localhost:8000`.

## Running the tests

```bash
pip install -r requirements.txt
pytest
```

The progression rules (meeting a standard, the two-session advance gate, the caution
flag) are covered by pure unit tests in `tests/test_progression.py` with no database or
HTTP layer involved. API-level tests cover auth, sessions CRUD, progress/advance
wiring, and — importantly — cross-user data isolation (`tests/test_isolation.py`).

## Backup and restore

The entire app's state is one SQLite file. To back it up:

```bash
docker compose stop
docker run --rm -v hybridcalisthenics_hybrid-tracker-data:/data -v "$PWD":/backup \
  alpine cp /data/hybrid-tracker.db /backup/hybrid-tracker-backup.db
docker compose start
```

To restore, stop the app, copy a backup file back into the volume at
`/data/hybrid-tracker.db`, and start it again.

## Known limitations

- **No password reset flow.** If a user forgets their password, an admin has to reset
  it directly in the database (or the user re-registers under a new username). This is
  a deliberate scope decision for a small, self-hosted, household-scale tool — not an
  oversight.
- **No email verification or OAuth.** Username + password only.
- **Open self-registration.** Anyone who can reach the app can create an account. If
  you're exposing this beyond a trusted network, put it behind a reverse proxy with
  its own access control.
- **No cross-user visibility.** Each user's progress and history is fully isolated;
  there's no shared "household" view.
- **SQLite's single-writer characteristics** are fine at household scale but aren't
  meant to support heavy concurrent write load.
