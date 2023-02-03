FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
WORKDIR /code
COPY . /code/
COPY requirements.txt /code/
RUN pip install -r requirements.txt
EXPOSE 27017
# CMD python manage.py makemigrations && python manage.py migrate && python manage.py initadmin

