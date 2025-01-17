FROM python:3.11-slim

# Accept build arguments for port configuration
ARG CONTAINER_INTERNAL_PORT=8080

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables with default values and support for overrides
ENV STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-$CONTAINER_INTERNAL_PORT} \
    STREAMLIT_SERVER_ADDRESS=${STREAMLIT_SERVER_ADDRESS:-0.0.0.0} \
    STREAMLIT_SERVER_ENABLE_CORS=${STREAMLIT_SERVER_ENABLE_CORS:-false} \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=${STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION:-true} \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=${STREAMLIT_BROWSER_GATHER_USAGE_STATS:-false}

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose the port dynamically
EXPOSE ${CONTAINER_INTERNAL_PORT}

# Create a non-root user
RUN useradd -m appuser
USER appuser

# Healthcheck with dynamic port
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${STREAMLIT_SERVER_PORT}/_stcore/health || exit 1

# Command to run the application with dynamic port and address
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=${STREAMLIT_SERVER_PORT}", "--server.address=${STREAMLIT_SERVER_ADDRESS}"]
