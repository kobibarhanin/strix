#!/usr/bin/env bash

curl  -X PUT -F file_blob=@/Users/kobarhan/workspace/bitz/user/user_exe.py "http://0.0.0.0:3000/payload"
curl  -X PUT -F file_blob=@/Users/kobarhan/workspace/bitz/user/user_exe.py "http://0.0.0.0:5000/execute"
curl  -X GET  "http://0.0.0.0:5000/jobs"

cat script.py|head -{a+b}|tail -{b-a}|python -i

curl  -X PUT -F file_blob=@/home/kobarhan/utecomp/tests/exe.py "http://0.0.0.0:5000/execute"

../setup/agentctl restart bitz 5000 192.168.1.14 192.168.1.24

az container create --resource-group utecomprg --name bitzdb --image mongo:latest --dns-name-label bitzdb --ports 27017

az container create --resource-group utecomprg --name tracker --image utecompacr.azurecr.io/tracker:v1 --dns-name-label tracker --ports 3000 --environment-variables 'DB_CTX'='bitzdb.westeurope.azurecontainer.io'

az container create --resource-group utecomprg --name bitz --image utecompacr.azurecr.io/bitz:v1 --dns-name-label bitzagent --ports 5000 --environment-variables 'AGENT_NAME'='bitz' 'PORT'='5000' 'AGENT_URL'='bitzagent.westeurope.azurecontainer.io' 'TRACKER_HOST'='tracker.westeurope.azurecontainer.io'

az container create --resource-group utecomprg --name bitz_2 --image utecompacr.azurecr.io/bitz:v1 --dns-name-label bitzagent2 --ports 5000 --environment-variables 'AGENT_NAME'='bitz_2' 'PORT'='5000' 'AGENT_URL'='bitzagent2.westeurope.azurecontainer.io' 'TRACKER_HOST'='tracker.westeurope.azurecontainer.io'

az container logs --resource-group utecomprg --name tracker

curl -X GET  'http://bitzagent.westeurope.azurecontainer.io:5000/logs'

utecompacr:PAKVsChXECxH43ixhNlrxNpeQ=KTkYRH

curl -X GET  'http://tracker.westeurope.azurecontainer.io:3000/register_agent?agent_name=bitz&agent_url=bitzagent.westeurope.azurecontainer.io&agent_port=5000'
curl -X GET  'http://tracker.westeurope.azurecontainer.io:3000/register_agent?agent_name=bitz2&agent_url=bitzagent2.westeurope.azurecontainer.io&agent_port=5000'

docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)