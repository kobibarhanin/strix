#!/usr/bin/env bash

echo "======================================="
ls -l
echo "======================================="

cd agent

docker network create mynet

../setup/agentctl restart bitz_0 bitz_0 5000 tracker

sleep 5

curl  -X GET  "http://0.0.0.0:5000/heartbeat"