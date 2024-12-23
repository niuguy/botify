# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for faster Python package management
RUN pip install uv

# Copy all files
COPY . .

# Create virtual environment using uv
RUN uv venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install project dependencies using uv
RUN uv pip install -e .

# Create logs directory
RUN mkdir -p logs

# Command to run the application
CMD ["python", "-m", "botify"]