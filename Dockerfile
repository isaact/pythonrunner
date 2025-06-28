# --------------------------------------------
# 🐍 System stage: base image with updates
# --------------------------------------------
FROM python:3.12.11-slim as system

RUN apt-get update && apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends \
    libc6 \
    libstdc++6 \
    libprotobuf32 \
    libnl-route-3-200 \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------
# 🧱 Builder stage: clone & build nsjail
# --------------------------------------------
FROM system as builder

RUN apt-get update && apt-get install --no-install-recommends -y \
  autoconf \
  bison \
  flex \
  gcc \
  g++ \
  git \
  libprotobuf-dev \
  libnl-route-3-dev \
  libtool \
  make \
  pkg-config \
  protobuf-compiler \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/google/nsjail.git /nsjail && \
    make -C /nsjail

# --------------------------------------------
# 🐍 Runtime stage: minimal Python + app + nsjail
# --------------------------------------------
FROM system as runtime

# Create a non-root user and group
RUN groupadd --system app && useradd --system --gid app app

# === Runtime configuration via environment variables ===
ENV FLASK_RUN_PORT=8080
ENV SANDBOX_PATH=/tmp/sandbox
ENV SANDBOX_SIZE=16m
ENV NSJAIL_CONFIG=/app/nsjail.cfg

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy compiled nsjail from builder
COPY --from=builder /nsjail/nsjail /usr/local/bin/nsjail

# Copy runner and app code separately
COPY runner/ /runner/
COPY app.py nsjail.cfg requirements.txt ./

# Create sandbox path (tmpfs will override it at runtime)
RUN mkdir -p ${SANDBOX_PATH}
# Change ownership of the app, runner, and sandbox directories
RUN chown -R app:app /app /runner ${SANDBOX_PATH}

# Switch to the non-root user
USER app


# Expose port for Flask API
EXPOSE ${FLASK_RUN_PORT}

# Entrypoint runs Flask app
CMD ["python", "app.py"]
