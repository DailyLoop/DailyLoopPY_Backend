# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variable to force Python output to be unbuffered
ENV PYTHONUNBUFFERED=1

# Install uv
RUN pip install --no-cache-dir uv

# Set the working directory to /app
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copy the entire project into the container
COPY . .

# Ensure start-services.sh has execute permissions
RUN chmod +x start-services.sh

# Expose port 8080 (Cloud Run sets the PORT env variable)
EXPOSE 8080

# Run the API Gateway.
# Cloud Run will set PORT, so we use that environment variable.
# Use uv run to execute within the virtual environment
CMD ["uv", "run", "-m", "backend.api_gateway.api_gateway"]