#!/usr/bin/env bash

echo "======================================="
ls -l
echo "======================================="

cd agent

../setup/agentctl restart bitz_0 bitz_0 5000 tracker host

docker ps
docker ps -a

sleep 5

curl  -X GET  "http://0.0.0.0:5000/heartbeat"

