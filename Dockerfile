# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variable to force Python output to be unbuffered
ENV PYTHONUNBUFFERED=1

# Set the working directory to /app
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Ensure start-services.sh has execute permissions
RUN chmod +x start-services.sh

# Expose port 5000 (Cloud Run sets the PORT env variable)
EXPOSE 8080

# Run the API Gateway.
# Cloud Run will set PORT, so we use that environment variable.
# CMD ["python", "backend/api_gateway/api_gateway.py"]
CMD ["./start-services.sh"]