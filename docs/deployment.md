# Deployment Notes

## Current deployment architecture

```text
Browser → Render web service → Python WSGI application → Rule engine
```

## Files used by Render

| File | Purpose |
|---|---|
| `requirements.txt` | Lists Gunicorn, the production web server used by Render. |
| `render.yaml` | Describes the service Render should create, build, check, and run. |
| `web/server.py` | Exposes the `application` WSGI callable that serves the website. |

## Local versus deployed server

Locally, run:

```powershell
python web/server.py
```

On Render, Gunicorn runs the application with this command:

```text
gunicorn --chdir web --bind 0.0.0.0:$PORT server:application
```

`$PORT` is provided by Render. `0.0.0.0` means the service accepts public network requests through Render's proxy; it does not expose the app directly from your personal computer.

## Data policy for version 1

FitGuide AI does not store user profiles, height, weight, or results. Therefore, version 1 has no database, no accounts, and no secret keys to configure.
