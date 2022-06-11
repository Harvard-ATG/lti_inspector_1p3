#!/bin/sh

# get the command from the first parameter; default to gunicorn
cmd="${1:-gunicorn}"

if [ "$cmd" = "gunicorn" ]; then
    ./python_venv/bin/python manage.py migrate                  # Apply database migrations
    ./python_venv/bin/python manage.py collectstatic --noinput  # Collect static files

    # Start Gunicorn processes
    echo Starting Gunicorn.
    exec ./python_venv/bin/gunicorn -c lti_inspector_1p3/settings/gunicorn.conf.py lti_inspector_1p3.wsgi:application
else
    ./python_venv/bin/python manage.py migrate                  # Apply database migrations
    ./python_venv/bin/python manage.py "$@"
fi
