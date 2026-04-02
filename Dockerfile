# --- Backend Build Stage ---
FROM python:3.11-slim as backend-builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

# --- Frontend Build Stage ---
FROM node:20-slim as frontend-builder

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# --- Final Production Image ---
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy project files
COPY . .

# Copy built frontend assets to a place where FastAPI can serve them (if desired)
# or just keep them separate for Nginx. For simplicity, we'll run both.
COPY --from=frontend-builder /app/dist ./frontend/dist

EXPOSE 8000
EXPOSE 5173

# Default environment variables
ENV DATABASE_URL=sqlite:///./data/sk-agentcorp.db
ENV LOG_LEVEL=INFO

# Command to run both (using a simple script or just backend for now)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
