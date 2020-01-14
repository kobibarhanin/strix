#!/usr/bin/env bash

# for current testing technique:


curl  -X PUT -F file_blob=@/Users/kobarhan/workspace/bitz/user/user_exe.py "http://0.0.0.0:3000/payload"



docker network create mynet
docker network connect mynet bitz_2
docker network connect mynet bitz

curl  -X PUT -F file_blob=@/Users/kobarhan/workspace/bitz/user/user_exe.py agent=bitz_2 "http://0.0.0.0:5000/execute"
curl  -X PUT -F file_blob=@/Users/kobarhan/workspace/bitz/user/user_exe.py "http://0.0.0.0:5000/execute"