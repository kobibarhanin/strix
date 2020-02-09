#!/usr/bin/env bash

source utils.sh

if [[ -n $1 ]];
then
    AGENTS=$1
else
    AGENTS=2
fi

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
for (( i=0; i<${AGENTS}; i++ ));
do
    PORT=$((5000 + ${i}))
    agentctl restart bitz_${i} bitz_${i} ${PORT} tracker
done

sleep 5

echo -e "${GREEN}Registering agents:${NC}"
for (( i=0; i<${AGENTS}; i++ ));
do
    PORT=$((5000 + ${i}))
    echo "agent ${i} -> $(agentctl register bitz_${i} bitz_${i} ${PORT} localhost)"
done
