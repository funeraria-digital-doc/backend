#!/bin/bash

echo "Applying migrations"

python manage.py makemigrations
python manage.py migrate
python manage.py initadmin

echo "finished successfully"
python manage.py runserver 0.0.0.0:9000