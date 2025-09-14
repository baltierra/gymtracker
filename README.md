
# FitTrack (Django) — with Weekly Summary & CSV Export

## Local quick start
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata tracker/fixtures.json
python manage.py runserver 0.0.0.0:8000
```

## Docker Compose (Gunicorn + Nginx)
```bash
export DJANGO_SECRET_KEY="$(python3 - <<'PY'
import secrets; print(secrets.token_urlsafe(50))
PY)"
docker compose build
docker compose up -d
docker exec -it fittrack_web python manage.py migrate
docker exec -it fittrack_web python manage.py createsuperuser
docker exec -it fittrack_web python manage.py loaddata tracker/fixtures.json
# Visit: http://149.165.173.174/
```
