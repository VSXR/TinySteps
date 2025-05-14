#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Manejo de DATABASE_URL vacío o inexistente en Render
if [ -z "$DATABASE_URL" ] || [ "$DATABASE_URL" = "" ]; then
  echo "Setting DATABASE_URL to SQLite for build process"
  export DATABASE_URL="sqlite:///db.sqlite3"
fi

# Run Django commands
python manage.py collectstatic --noinput
python manage.py migrate