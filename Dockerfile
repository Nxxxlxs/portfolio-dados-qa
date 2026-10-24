FROM python:3.12-slim

# Copia o binário do uv da imagem oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

# 1) Só as dependências primeiro (aproveita o cache do Docker)
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project

# 2) Depois o código
COPY app ./app
COPY core ./core
COPY .streamlit ./.streamlit

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]