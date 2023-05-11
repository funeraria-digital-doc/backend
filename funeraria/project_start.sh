#!/bin/bash
echo "Applying migrations"
python funeraria/manage.py makemigrations
python funeraria/manage.py migrate
python funeraria/manage.py initadmin
echo "finished successfully"
python funeraria/manage.py runserver 0.0.0.0:8000

