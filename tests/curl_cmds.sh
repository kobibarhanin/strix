#!/usr/bin/env bash

# for current testing technique:


curl  -X PUT -F file_blob=@/Users/kobarhan/workspace/bitz/user/user_exe.py "http://0.0.0.0:3000/payload"



docker network create mynet
docker network connect mynet bitz_2
docker network connect mynet bitz

curl  -X PUT -F file_blob=@/Users/kobarhan/workspace/bitz/user/user_exe.py "http://0.0.0.0:5000/execute"

../setup/agentctl restart bitz 5000



docker run -d -p 27017:27017 --name bitz_db mongo

# TODO - add this to ctl
docker stop tracker
docker container rm tracker
docker build --rm -t tracker:latest .
docker run -d  --network=mynet --name tracker -p 3000:3000 tracker

docker exec -it bitz_2 /bin/bash