# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for faster Python package management
RUN pip install uv

# Copy project files
COPY . .

# Install project dependencies using uv
RUN uv pip install -e .

# Command to run the application
CMD ["python", "-m", "botify.main"]