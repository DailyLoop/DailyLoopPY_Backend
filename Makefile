# Makefile for News Aggregator Project

.PHONY: run test docker-build docker-clean install

# Install dependencies using uv
install:
	uv sync

# Run the API Gateway
run:
	uv run -m backend.api_gateway.api_gateway

# Run tests using pytest via uv
test:
	uv run pytest --maxfail=1 --disable-warnings -q

# Build Docker image
docker-build:
	docker build -t news-aggregator:latest .

# Clean Docker image
docker-clean:
	docker rmi news-aggregator:latest
