#!/usr/bin/env bash

# for current testing technique:

curl  -X PUT -F file_blob=@/Users/kobarhan/workspace/bitz/user/user_exe.py "http://0.0.0.0:3000/payload"
curl  -X PUT -F file_blob=@/Users/kobarhan/workspace/bitz/user/user_exe.py "http://0.0.0.0:5000/execute"
