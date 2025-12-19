#!/bin/bash

# Linux AIO Performance Checker - Build and Run Script
# This script builds a local Docker container and runs it,
# replacing any existing container with the same version

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Ensure uploads directory exists with proper permissions
echo -e "${YELLOW}Ensuring uploads directory exists...${NC}"
mkdir -p uploads
chmod 755 uploads
# Ensure ownership is correct for the container user (1000:1000)
chown -R 1000:1000 uploads 2>/dev/null || echo -e "${YELLOW}Note: Could not set ownership (may need sudo)${NC}"
echo -e "${GREEN}Uploads directory ready.${NC}"
echo

# Read version from VERSION file
if [ ! -f "VERSION" ]; then
    echo -e "${RED}Error: VERSION file not found in project root${NC}"
    exit 1
fi

VERSION=$(cat VERSION | tr -d '\n\r')
IMAGE_NAME="linuxaio-app"
IMAGE_TAG="${IMAGE_NAME}:${VERSION}"
CONTAINER_NAME="linuxaio-app"

echo -e "${BLUE}=== Linux AIO Performance Checker Build & Run Script ===${NC}"
echo -e "${BLUE}Version: ${VERSION}${NC}"
echo -e "${BLUE}Image: ${IMAGE_TAG}${NC}"
echo -e "${BLUE}Container: ${CONTAINER_NAME}${NC}"
echo

# Check if user can run docker commands
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Error: Cannot connect to Docker daemon. Please ensure:${NC}"
    echo -e "${YELLOW}  1. Docker is installed and running${NC}"
    echo -e "${YELLOW}  2. You are in the 'docker' group: sudo usermod -aG docker \$USER${NC}"
    echo -e "${YELLOW}  3. Log out and back in, or run: newgrp docker${NC}"
    exit 1
fi

# Function to check if container is running
is_container_running() {
    docker ps --filter "name=${CONTAINER_NAME}" --filter "status=running" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

# Function to check if container exists (running or stopped)
container_exists() {
    docker ps -a --filter "name=${CONTAINER_NAME}" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

# Function to get container image
get_container_image() {
    docker ps -a --filter "name=${CONTAINER_NAME}" --format "{{.Image}}" | head -n1
}

echo -e "${YELLOW}Step 1: Checking for existing containers...${NC}"

if container_exists; then
    CURRENT_IMAGE=$(get_container_image)
    echo -e "${YELLOW}Found existing container using image: ${CURRENT_IMAGE}${NC}"

    if is_container_running; then
        echo -e "${YELLOW}Container is currently running. Stopping it...${NC}"
        docker stop "${CONTAINER_NAME}"
    fi

    echo -e "${YELLOW}Removing existing container...${NC}"
    docker rm "${CONTAINER_NAME}"
    echo -e "${GREEN}Existing container removed.${NC}"
else
    echo -e "${GREEN}No existing container found.${NC}"
fi

echo
echo -e "${YELLOW}Step 2: Building Docker image...${NC}"
echo -e "${BLUE}Building image: ${IMAGE_TAG}${NC}"

if docker build -t "${IMAGE_TAG}" .; then
    echo -e "${GREEN}Docker image built successfully: ${IMAGE_TAG}${NC}"
else
    echo -e "${RED}Failed to build Docker image${NC}"
    exit 1
fi

echo
echo -e "${YELLOW}Step 3: Starting new container...${NC}"

# Run the container using docker-compose
if docker-compose up -d; then
    echo -e "${GREEN}Container started successfully!${NC}"
    echo -e "${GREEN}Application should be available at: http://localhost:8000${NC}"
else
    echo -e "${RED}Failed to start container${NC}"
    exit 1
fi

echo
echo -e "${YELLOW}Step 4: Verifying container health...${NC}"

# Wait a bit for the container to start
sleep 5

# Check if container is running
if is_container_running; then
    echo -e "${GREEN}✓ Container is running${NC}"

    # Check health status if health check is available
    if docker ps --filter "name=${CONTAINER_NAME}" --format "{{.Status}}" | grep -q "healthy\|Up"; then
        echo -e "${GREEN}✓ Container appears healthy${NC}"
    else
        echo -e "${YELLOW}⚠ Container status uncertain - checking logs...${NC}"
        docker logs "${CONTAINER_NAME}" | tail -10
    fi
else
    echo -e "${RED}✗ Container failed to start${NC}"
    echo -e "${YELLOW}Checking container logs:${NC}"
    docker logs "${CONTAINER_NAME}" 2>/dev/null || echo "No logs available"
    exit 1
fi

echo
echo -e "${GREEN}=== Build and deployment completed successfully! ===${NC}"
echo -e "${GREEN}Container: ${CONTAINER_NAME}${NC}"
echo -e "${GREEN}Image: ${IMAGE_TAG}${NC}"
echo -e "${GREEN}Access the application at: http://localhost:8000${NC}"
echo
echo -e "${BLUE}To view logs: docker logs ${CONTAINER_NAME}${NC}"
echo -e "${BLUE}To stop: docker-compose down${NC}"
echo -e "${BLUE}To restart: docker-compose restart${NC}"
