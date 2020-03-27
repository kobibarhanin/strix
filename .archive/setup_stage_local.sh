#!/usr/bin/env bash

# this will setup db and tracker locally for staging deployment.

source utils.sh

echo -e "${GREEN}Launching Tracker db:${NC}"
docker stop bitz_db
docker container rm bitz_db
docker run -d -p 27017:27017 --name bitz_db mongo

cd tracker
echo -e "${GREEN}Launching Tracker:${NC}"
source venv/bin/activate
export DB_CTX='localhost'
python3 entry_point.py
deactivate