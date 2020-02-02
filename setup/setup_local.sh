#!/usr/bin/env bash

source utils.sh


docker network create mynet

echo -e "${GREEN}Launching Tracker db:${NC}"
docker stop bitz_db
docker container rm bitz_db
docker run -d -p 27017:27017 --network=mynet --name bitz_db mongo

cd tracker
echo -e "${GREEN}Launching Tracker:${NC}"
docker stop tracker
docker container rm tracker
docker build --rm -t tracker:latest .
docker run -d  --network=mynet --name tracker -p 3000:3000 tracker

cd ../agent
echo -e "${GREEN}Launching agents:${NC}"
agentctl restart bitz 5000 tracker bitz
agentctl restart bitz_2 5001 tracker bitz_2

sleep 5
echo -e "${GREEN}Registering agents:${NC}"
echo "agent 1 -> $(curl -X GET  'http://0.0.0.0:3000/register_agent?agent_name=bitz&agent_url=bitz&agent_port=5000')"
echo "agent 2 -> $(curl -X GET  'http://0.0.0.0:3000/register_agent?agent_name=bitz_2&agent_url=bitz_2&agent_port=5001')"
