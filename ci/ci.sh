#!/usr/bin/env bash

echo "======================================="
ls -l
echo "======================================="

docker --version
curl --version

echo "======================================="

cd agent
../setup/agentctl restart bitz_0 bitz_0 5000 tracker

curl  -X GET  "http://0.0.0.0:5000/heartbeat"