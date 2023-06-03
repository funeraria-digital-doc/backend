FROM python:3.11.2
COPY ./requirements.txt /requirements.txt
COPY ./funeraria /funeraria
WORKDIR /funeraria

RUN python -m venv /py && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --no-create-home django-user

ENV PATH="/py/bin:$PATH"

USER django-user
