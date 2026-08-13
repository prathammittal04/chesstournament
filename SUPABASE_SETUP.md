# Moving the tournament data to Supabase (Postgres)

Your app now stores everything in Postgres instead of `database/tournament.db`,
so nothing resets when you redeploy and no `.db` file goes to GitHub.
No application code changed — only the connection.

## 1. Create the database
1. Go to https://supabase.com → **New project** (free tier is enough).
2. Choose a **database password** and save it somewhere safe.
3. Wait ~2 minutes for the project to finish provisioning.

## 2. Copy the connection string
1. In the project, click **Connect** (top bar).
2. Pick **Session pooler** (port `5432`), and copy the URI. It looks like:
   `postgresql://postgres.abcdefgh:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres`
   <!-- postgresql://postgres:Seema_03/06/83@db.bjimdxmvhdsiavwpeewd.supabase.co:5432/postgres -->
3. Replace `[YOUR-PASSWORD]` with the password from step 1.

## 3. Run locally
```bash
pip install -r requirements.txt
cp .env.example .env        # then paste your URL into DATABASE_URL
python app.py
```
On first start the app creates all seven tables automatically
(`users`, `tournaments`, `teams`, `players`, `rounds`, `matches`, `board_results`)
and the admin login. Nothing is ever seeded beyond that.

## 4. Deploy
Set the same environment variables on your host (Render / Railway / Fly / PythonAnywhere):

| Variable | Value |
|---|---|
| `DATABASE_URL` | the Supabase session-pooler URI |
| `SECRET_KEY` | any long random string |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | your login (optional) |

Start command: `gunicorn app:app`

Because the data now lives in Supabase, redeploys, restarts and ephemeral disks
no longer touch it. Deleted tournaments stay deleted; new ones stay forever.

## 5. (Optional) Bring your old SQLite data across
If you still have an old `tournament.db` you want to keep:
```bash
python migrate_sqlite_to_postgres.py path/to/tournament.db
```
Run it once, with `DATABASE_URL` set.

## Notes
- `.gitignore` now excludes `database/`, `*.db` and `.env`, so no database file
  or password can be pushed to GitHub again.
- If you see `SSL connection has been closed unexpectedly`, that is a dropped
  idle pooler connection; the app already retries via `pool_pre_ping`.
