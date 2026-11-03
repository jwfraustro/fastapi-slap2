FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install the locked dependencies first so this layer is cached across code changes.
COPY requirements.txt /app/
RUN pip install --require-hashes -r requirements.txt

COPY . /app
RUN pip install --no-deps .

EXPOSE 8000

CMD ["/bin/sh", "/app/start.sh"]
