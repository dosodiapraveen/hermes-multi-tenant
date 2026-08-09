FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl git ca-certificates && rm -rf /var/lib/apt/lists/*

# Install Hermes Agent system-wide (in container's python env)
RUN curl -fsSL https://hermes-agent.nousresearch.com/install.sh -o /tmp/hermes-install.sh && \
    bash /tmp/hermes-install.sh 2>&1 | tail -5

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
