#!/bin/bash
docker build --tag amazon-bot:latest .
docker tag amazon-bot:latest docker.io/raelix/amazon-bot:latest
docker push docker.io/raelix/amazon-bot:latest