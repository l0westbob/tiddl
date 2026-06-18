FROM python:3.13-alpine

WORKDIR /app

RUN apk add --no-cache ffmpeg

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
  && uv sync --no-dev --frozen

COPY . .
RUN pip install --no-cache-dir --no-deps .

ENV TIDDL_PATH=/data/tiddl
VOLUME ["/data/tiddl"]

ENTRYPOINT ["tiddl"]
