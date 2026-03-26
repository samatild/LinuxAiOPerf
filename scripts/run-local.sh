#!/bin/bash
# Build and run the LinuxAiOPerf container locally.
# Stops and removes any existing container before rebuilding.

set -e

CONTAINER_NAME="linuxaio-app"
IMAGE_NAME="linuxaio-app:local"
HOST_PORT=8000

# Colours
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

# Go to project root (script lives in scripts/ subdirectory)
cd "$(dirname "$0")/.."

echo -e "${YELLOW}==> Checking for existing container '${CONTAINER_NAME}'...${NC}"
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${YELLOW}    Stopping running container...${NC}"
        docker stop "${CONTAINER_NAME}"
    fi
    echo -e "${YELLOW}    Removing container...${NC}"
    docker rm "${CONTAINER_NAME}"
    echo -e "${GREEN}    Done.${NC}"
else
    echo -e "${GREEN}    No existing container found.${NC}"
fi

echo
echo -e "${YELLOW}==> Building image '${IMAGE_NAME}'...${NC}"
docker build -t "${IMAGE_NAME}" .
echo -e "${GREEN}    Build complete.${NC}"

echo
echo -e "${YELLOW}==> Starting container...${NC}"
mkdir -p uploads
docker run -d \
    --name "${CONTAINER_NAME}" \
    -p "${HOST_PORT}:80" \
    -v "$(pwd)/uploads:/linuxaio/digest" \
    -e FLASK_ENV=production \
    -e WORKERS=4 \
    -e TIMEOUT=300 \
    -e UPLOAD_FOLDER=/linuxaio/digest \
    --restart unless-stopped \
    "${IMAGE_NAME}"

echo -e "${GREEN}    Container '${CONTAINER_NAME}' started.${NC}"
echo
echo -e "${GREEN}==> App available at http://localhost:${HOST_PORT}${NC}"
echo -e "${YELLOW}    Logs: docker logs -f ${CONTAINER_NAME}${NC}"
echo -e "${YELLOW}    Stop: docker stop ${CONTAINER_NAME} && docker rm ${CONTAINER_NAME}${NC}"
