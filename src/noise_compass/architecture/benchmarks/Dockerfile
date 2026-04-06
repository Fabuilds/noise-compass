# Antigravity Polyglot Benchmark Dockerfile
# Provides a safe, isolated environment for evaluating LLM-generated code.

FROM rust:1.76-slim-bookworm

# Install Python and essential build tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    build-essential \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python testing dependencies
RUN pip3 install --no-cache-dir --break-system-packages \
    pytest \
    numpy

# Create exercise workspace
WORKDIR /workspace

# Default command: Run whatever the harness tells us
CMD ["/bin/bash"]
