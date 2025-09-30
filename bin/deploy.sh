#!/usr/bin/env bash
# Helper to deploy to Heroku, run migrations and collectstatic
set -e
APP=${1:-django-project-shutterspace-a676bf7fbd5b}

echo "Pushing to Heroku app: $APP"
git push heroku main

echo "Running migrations"
heroku run python manage.py migrate --app $APP

echo "Collecting static"
heroku run python manage.py collectstatic --noinput --app $APP

echo "Restarting dynos"
heroku restart --app $APP

echo "Deploy complete"
