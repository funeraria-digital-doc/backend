FROM python:3.11.2
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
WORKDIR /code
COPY . /code/
COPY requirements.txt /code/
RUN pip install -r requirements.txt

CMD ["/bin/sh", "-c", "python manage.py migrate && python manage.py runserver 8000"]
