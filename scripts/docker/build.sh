#!/bin/bash

PROJECT_DIR=$(dirname $(dirname $(realpath $(dirname $0))))
DOCKERFILE_PATH=${PROJECT_DIR}/docker

docker build -t mate2024 $DOCKERFILE_PATH
docker run -it --rm mate2024
# docker run -it --name cont-mate2024 mate2024