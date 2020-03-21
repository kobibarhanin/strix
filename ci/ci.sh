#!/usr/bin/env bash

echo "======================================="
ls -l
echo "======================================="

cd agent

docker network create mynet
docker run -d -p 27017:27017 --network=mynet --name bitz_0_db mongo
../setup/agentctl restart bitz_0 bitz_0 5000 tracker host rebuild bitz_0_db 27017

docker ps
docker ps -a

sleep 10

curl  -X GET  "http://0.0.0.0:5000/heartbeat"

