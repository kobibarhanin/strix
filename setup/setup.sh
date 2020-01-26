#!/usr/bin/env bash

source utils.sh

echo -e "${GREEN}Launching agents:${NC}"
cd agent
agentctl restart bitz 5000
agentctl restart bitz_2 5001
echo -e "${GREEN}Launching DB:${NC}"
cd ..
docker stop bitz_db
docker container rm bitz_db
docker run -d -p 27017:27017 --network=mynet --name bitz_db mongo
echo -e "${GREEN}Launching Tracker:${NC}"
cd tracker
docker stop tracker
docker container rm tracker
docker build --rm -t tracker:latest .
docker run -d  --network=mynet --name tracker -p 3000:3000 tracker