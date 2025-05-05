#!/bin/bash
set -e

INIT_FLAG="data/.initialized"

# Stop the ollama service if it is running
systemctl is-active --quiet ollama.service && systemctl stop ollama.service

# Run first-time setup only once
if [ ! -f "$INIT_FLAG" ]; then
  echo "[Init] First-time setup running..."

  # Docker compose build and up
  echo "[Init] Docker compose build and up"
  docker compose build
  docker compose up -d

  # Wait some time until it is up
  echo "[Init] Wait for 20 seconds until docker compose is up"
  sleep 20

  # Set up the database
  echo "[Init] Set up the database"
  docker exec -it api_c python law_rag/build_graph.py

  # Download the model
  # It should be matched with the model in config file
  echo "[Init] Download the model"
  docker exec -it ollama_c ollama pull gemma2

  echo "[Init] Setup done."
  touch "$INIT_FLAG"

# Run if not first-time setup
else
  echo "[Init] Docker compose up"
  docker compose up -d

  echo "[Init] Wait for 20 seconds until docker compose is up"
  sleep 20

fi

echo "[Init] Setup is complete! The app is in:"
echo "http://localhost:3000"
echo "You are free to explore it!"