FROM python:3.12.12-bookworm
LABEL authors="Dmitry"

RUN apt-get update && apt-get install -y \
    locales && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && apt-get clean


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./

ENV UV_VENV_MANAGED=0
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PYTHONUNBUFFERED=1
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
ENV PATH="/opt/venv/bin:$PATH"

RUN uv sync --no-cache

COPY . /app/
RUN chmod +x /app/scripts/docker-entrypoint.sh

CMD ["/app/scripts/docker-entrypoint.sh"]
