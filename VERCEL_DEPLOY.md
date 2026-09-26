# Deploy Seatify to Vercel

Vercel detects this Django project from `manage.py` and uses `seatify/wsgi.py`. Static files are collected during the Vercel build. No custom build command is required.

## Before the first deploy

1. Push this project to GitHub, then import that repository in Vercel (or link it with the Vercel CLI).
2. Create a persistent PostgreSQL database with a provider such as Neon or Supabase. Do not use the local `db.sqlite3` file on Vercel; serverless filesystems are temporary.
3. In Vercel Project Settings > Environment Variables, add these for Production and Preview:
   - `SECRET_KEY`: a long, random secret. Generate one locally with `python -c "import secrets; print(secrets.token_urlsafe(50))"`.
   - `DATABASE_URL`: the PostgreSQL connection URL from your database provider.
4. Deploy the project. The Vercel project domain is added to Django's allowed hosts automatically. For a custom domain, add `ALLOWED_HOSTS` as a comma-separated list of hostnames (no scheme), and `CSRF_TRUSTED_ORIGINS` as comma-separated HTTPS origins, for example `https://seatify.example.com`.

## Run database migrations

After linking the project with `vercel link` and setting the production environment variables, run this from PowerShell in the project folder:

```powershell
vercel env run -e production -- .\venv\Scripts\python.exe manage.py migrate
```

Create an admin login if needed:

```powershell
vercel env run -e production -- .\venv\Scripts\python.exe manage.py createsuperuser
```

Redeploy after changing Vercel environment variables.

## Important file storage note

Vercel's filesystem is not permanent. Seatify currently stores uploaded timetable files under `/tmp` on Vercel, so an uploaded file can disappear after a function restarts. Database records are persistent, but the original uploaded files are not. For reliable long-term uploads, configure object storage (such as an S3-compatible bucket) before relying on timetable uploads in production.

## Optional email settings

Email sending is not currently used by the app. If it is added later, configure `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and either `EMAIL_USE_TLS=true` or `EMAIL_USE_SSL=true` in Vercel.
