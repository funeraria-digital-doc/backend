FROM python:3.11.2
COPY ./requirements.txt /requirements.txt
COPY ./funeraria /funeraria
RUN apt-get update && apt-get install -y sudo
WORKDIR /funeraria
RUN sudo apt-get install -y xvfb 
RUN sudo apt-get install -y xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic 
RUN sudo apt-get install -y wkhtmltopdf 
RUN python -m venv /py && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --gecos "" django-user
    #adduser --disabled-password --no-create-home django-user

RUN usermod -aG sudo django-user
RUN echo 'django-user:password' | chpasswd
ENV PATH="/py/bin:$PATH"
USER django-user