#!/bin/bash

# Source config
source config.sh

# Build the Docker image using the MariaDB base image and the database dump
docker build -t $DOCKER_IMAGE_NAME_ARM:$DOCKER_IMAGE_TAG -f Dockerfile_arm .

# Login to Docker Hub
docker login --username $DOCKER_HUB_USERNAME --password $DOCKER_HUB_PASSWORD

# Tag the Docker image for deployment to Docker Hub
docker tag $DOCKER_IMAGE_NAME_ARM:$DOCKER_IMAGE_TAG $DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_ARM:$DOCKER_IMAGE_TAG

# Push the Docker image to Docker Hub
docker push $DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_ARM:$DOCKER_IMAGE_TAG

# Remove the local Docker image
docker rmi $DOCKER_IMAGE_NAME_ARM:$DOCKER_IMAGE_TAG
