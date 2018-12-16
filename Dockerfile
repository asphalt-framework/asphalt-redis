FROM python:3.5.2

RUN wget -qO- https://github.com/jwilder/dockerize/releases/download/v0.4.0/dockerize-linux-amd64-v0.4.0.tar.gz |\
    tar xzC /usr/local/bin
RUN pip install -U setuptools

ENV SETUPTOOLS_SCM_PRETEND_VERSION 3.0.0

WORKDIR /app
COPY asphalt ./asphalt
COPY setup.* pyproject.toml ./
RUN pip install -e .[test]
