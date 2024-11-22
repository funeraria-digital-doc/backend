FROM python:3.11.2
COPY ./requirements.txt /requirements.txt
COPY ./funeraria /funeraria
RUN apt-get update && apt-get install -y  sudo
#sudo default-jdk-headless
RUN sudo apt-get install -y libreoffice
#RUN sudo apt-get install -y pdftk
WORKDIR /funeraria

RUN python -m venv /py && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --gecos "" django-user
RUN usermod -aG sudo django-user
RUN echo 'django-user:password' | chpasswd
ENV PATH="/py/bin:$PATH"
EXPOSE 8000
USER django-user
CMD python manage.py runserver 0.0.0.0:80
# --no-cache-dir