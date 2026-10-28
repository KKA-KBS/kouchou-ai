FROM python:3.12-slim

WORKDIR /app

ARG ENVIRONMENT

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

# Copy API package files (context is repository root)
COPY apps/api/pyproject.toml apps/api/requirements.lock apps/api/requirements-dev.lock apps/api/README.md ./

# Copy and install analysis-core package
COPY packages/analysis-core /packages/analysis-core

# ステージングの埋め込みは Titan なので、ローカル埋め込み用の torch は入れない。
# full には embeddings（sentence-transformers と torch）が含まれる。
RUN set -- "/packages/analysis-core[gemini,clustering]" && \
    if [ "$ENVIRONMENT" = "development" ]; then \
        set -- "$@" -r requirements-dev.lock; \
    else \
        set -- "$@" -r requirements.lock; \
    fi && \
    echo "Installing dependencies (ENV=$ENVIRONMENT)" && \
    uv pip install --no-cache --system "$@" "boto3>=1.35.0"

# Copy application source
COPY apps/api/ .

# アプリケーションの実行
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
