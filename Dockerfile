FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    xvfb \
    xauth \
    xfonts-base \
    xfonts-75dpi \
    git openssh-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install -r requirements.txt

RUN playwright install-deps

RUN playwright install

COPY ./src /app/

ENTRYPOINT [ "xvfb-run", "--auto-servernum", "--server-args=-screen 0 1280x1024x24", "python3", "main.py" ]