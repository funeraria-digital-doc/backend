#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py makemigrations
python manage.py migrate --noinput
python manage.py initadmin
# If running in 'production' mode, we would need these

# echo "Compile CSS"
# python manage.py sass profiles/assets/scss/ profiles/static/css/

# echo "Collect static files"
# python manage.py collectstatic --noinput

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:9000