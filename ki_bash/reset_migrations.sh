#!/bin/bash

# --- CONFIG ---
APP_PYTHON="python manage.py"
DB_ENGINE="sqlite"   # change to 'postgres' or 'mysql' if needed

echo "🔥 Deleting old migrations..."
find . -path "*/migrations/*.py" ! -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

echo "🔥 Clearing migration history from DB..."
if [ "$DB_ENGINE" = "sqlite" ]; then
    $APP_PYTHON dbshell <<EOF
DELETE FROM django_migrations;
EOF
elif [ "$DB_ENGINE" = "postgres" ]; then
    $APP_PYTHON dbshell <<EOF
TRUNCATE TABLE django_migrations RESTART IDENTITY CASCADE;
EOF
elif [ "$DB_ENGINE" = "mysql" ]; then
    $APP_PYTHON dbshell <<EOF
TRUNCATE TABLE django_migrations;
EOF
fi

echo "🔥 Making new migrations..."
$APP_PYTHON makemigrations

echo "🔥 Applying migrations..."
$APP_PYTHON migrate --fake-initial

echo "✅ Migrations reset complete!"
